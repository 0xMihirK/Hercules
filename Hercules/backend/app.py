"""
FastAPI Backend — Pentest Agent Suite
======================================

REST API + WebSocket server for orchestrating pentest flows
and streaming real-time status updates to the frontend.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import uuid
import ssl
from datetime import datetime
from pathlib import Path
from typing import Dict

# ---------------------------------------------------------------------------
# Global SSL Patch (Bypasses corporate proxy / self-signed cert issues)
# ---------------------------------------------------------------------------
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
os.environ["LITELLM_VERIFY_SSL"] = "False"

import httpx
# Sledgehammer SSL bypass for HTTPX (used by LiteLLM / CrewAI)
_original_init = httpx.Client.__init__
_original_async_init = httpx.AsyncClient.__init__

def _patched_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _original_init(self, *args, **kwargs)

def _patched_async_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _original_async_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_init
httpx.AsyncClient.__init__ = _patched_async_init

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Add parent directory to path for crew imports
AGENT_ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER_ROOT = AGENT_ROOT.parent / "MCP"
sys.path.insert(0, str(AGENT_ROOT))
sys.path.insert(0, str(MCP_SERVER_ROOT))

from backend.models import (
    ScanRequest,
    ScanResponse,
    ScanListItem,
    ScanStatus,
    PhaseStatus,
    StatusUpdate,
)
from backend.websocket_manager import WebSocketManager
from flows.pentest_flow import PentestFlow
from backend.shared_storage import AppendSharedStorageTool, ReadSharedStorageTool

# Load environment variables
load_dotenv(AGENT_ROOT.parent / ".env")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Pentest Agent Suite API",
    description="Automated Penetration Testing & CTF Solving powered by CrewAI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

ws_manager = WebSocketManager()
active_scans: Dict[str, dict] = {}  # scan_id → scan state
scan_tasks: Dict[str, asyncio.Task] = {}  # scan_id → background task


# ---------------------------------------------------------------------------
# Helper: Run pentest flow in background
# ---------------------------------------------------------------------------

async def run_pentest_flow(scan_id: str, request: ScanRequest):
    """Run the pentest flow in a background task."""
    loop = asyncio.get_event_loop()

    # Status callback that bridges sync crew output to async WebSocket
    def status_callback(update: dict):
        try:
            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast(scan_id, update),
                loop,
            )
        except Exception as e:
            logger.warning(f"Broadcast failed: {e}")

    # Update scan state
    active_scans[scan_id]["status"] = ScanStatus.RUNNING
    active_scans[scan_id]["started_at"] = datetime.now().isoformat()

    try:
        # Initialize MCP server and run flow
        mcp_tools = []
        try:
            from crewai_tools import MCPServerAdapter
            from mcp import StdioServerParameters

            server_py = MCP_SERVER_ROOT / "server.py"
            if server_py.exists():
                server_params = StdioServerParameters(
                    command=str(MCP_SERVER_ROOT / ".venv" / "bin" / "python"),
                    args=[str(server_py)],
                    env={**os.environ, "SCAN_ID": scan_id},
                )

                logger.info("Starting MCP server...")
                await ws_manager.broadcast(scan_id, {
                    "scan_id": scan_id,
                    "phase": "initializing",
                    "message": "Connecting to MCP security toolkit...",
                    "progress": 2,
                    "timestamp": datetime.now().isoformat(),
                })

                adapter = MCPServerAdapter(serverparams=server_params)
                await loop.run_in_executor(None, adapter.start)
                mcp_tools = adapter.tools
                logger.info(f"MCP server started with {len(mcp_tools)} tools")

                await ws_manager.broadcast(scan_id, {
                    "scan_id": scan_id,
                    "phase": "initializing",
                    "message": f"MCP toolkit connected — {len(mcp_tools)} security tools available",
                    "progress": 5,
                    "timestamp": datetime.now().isoformat(),
                })
            else:
                logger.warning(f"MCP server not found at {server_py}")
                await ws_manager.broadcast(scan_id, {
                    "scan_id": scan_id,
                    "phase": "initializing",
                    "message": "MCP server not found — running with LLM-only analysis",
                    "progress": 5,
                    "timestamp": datetime.now().isoformat(),
                })

        except ImportError as e:
            logger.warning(f"MCP libraries not available: {e}")
            await ws_manager.broadcast(scan_id, {
                "scan_id": scan_id,
                "phase": "initializing",
                "message": "MCP libraries not installed — running with LLM-only analysis",
                "progress": 5,
                "timestamp": datetime.now().isoformat(),
            })
        except Exception as e:
            logger.error(f"MCP server connection failed: {e}")
            await ws_manager.broadcast(scan_id, {
                "scan_id": scan_id,
                "phase": "initializing",
                "message": f"MCP connection failed: {str(e)} — running with LLM-only analysis",
                "progress": 5,
                "timestamp": datetime.now().isoformat(),
            })

        # Setup Shared Storage Tools
        shared_storage_path = str(AGENT_ROOT / "reports" / f"shared_storage_{scan_id}.md")
        
        # Create reports directory if it doesn't exist
        os.makedirs(os.path.dirname(shared_storage_path), exist_ok=True)
        with open(shared_storage_path, "w", encoding="utf-8") as f:
            f.write("# Shared Agent Knowledge Base\n\nThis file contains shared findings (passwords, open ports, flags) across all agents.\n\n")
            
        append_tool = AppendSharedStorageTool(storage_path=shared_storage_path)
        read_tool = ReadSharedStorageTool(storage_path=shared_storage_path)
        mcp_tools.extend([append_tool, read_tool])

        # Create and run the flow
        flow = PentestFlow(mcp_tools=mcp_tools, status_callback=status_callback)

        # Run in executor since crews are synchronous
        def _run_flow():
            return flow.kickoff(
                inputs={
                    "scan_id": scan_id,
                    "target": request.target,
                    "target_type": request.target_type.value,
                    "ctf_mode": request.ctf_mode,
                    "special_instructions": request.special_instructions,
                    "compliance_framework": request.compliance_framework.value,
                }
            )

        result = await loop.run_in_executor(None, _run_flow)

        # Update final state
        active_scans[scan_id]["status"] = ScanStatus.COMPLETED
        active_scans[scan_id]["completed_at"] = datetime.now().isoformat()
        active_scans[scan_id]["report_html"] = flow.state.report_html
        active_scans[scan_id]["phases_completed"] = flow.state.phases_completed
        active_scans[scan_id]["errors"] = flow.state.errors

    except asyncio.CancelledError:
        logger.warning(f"Scan {scan_id} was cancelled.")
        active_scans[scan_id]["status"] = ScanStatus.ERROR
        active_scans[scan_id]["completed_at"] = datetime.now().isoformat()
        active_scans[scan_id]["errors"].append("Scan was cancelled.")
        await ws_manager.broadcast(scan_id, {
            "scan_id": scan_id,
            "phase": "error",
            "message": "Scan cancelled.",
            "progress": 100,
            "timestamp": datetime.now().isoformat(),
        })
        raise
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}")
        active_scans[scan_id]["status"] = ScanStatus.ERROR
        active_scans[scan_id]["completed_at"] = datetime.now().isoformat()
        active_scans[scan_id]["errors"].append(str(e))

        await ws_manager.broadcast(scan_id, {
            "scan_id": scan_id,
            "phase": "error",
            "message": f"Scan failed: {str(e)}",
            "progress": 100,
            "timestamp": datetime.now().isoformat(),
        })
    finally:
        # Clean up MCP and Shared Storage
        try:
            if 'adapter' in locals() and adapter and adapter.is_connected:
                adapter.stop()
        except Exception as e:
            logger.warning(f"Error stopping adapter: {e}")
            
        try:
            if 'shared_storage_path' in locals() and os.path.exists(shared_storage_path):
                os.remove(shared_storage_path)
                logger.info(f"Cleaned up shared storage file: {shared_storage_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up shared storage file: {e}")


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Pentest Agent Suite API", "version": "1.0.0"}


@app.post("/api/scan", response_model=ScanResponse)
async def start_scan(request: ScanRequest):
    """Start a new penetration test scan."""
    scan_id = str(uuid.uuid4())[:8]

    # Initialize scan state
    active_scans[scan_id] = {
        "scan_id": scan_id,
        "target": request.target,
        "target_type": request.target_type.value,
        "ctf_mode": request.ctf_mode,
        "special_instructions": request.special_instructions,
        "compliance_framework": request.compliance_framework.value,
        "status": ScanStatus.PENDING,
        "current_phase": "pending",
        "progress": 0,
        "phases_completed": [],
        "errors": [],
        "started_at": None,
        "completed_at": None,
        "report_html": "",
    }

    # Start background task
    task = asyncio.create_task(run_pentest_flow(scan_id, request))
    scan_tasks[scan_id] = task

    logger.info(f"Scan {scan_id} created for target {request.target}")

    return ScanResponse(
        scan_id=scan_id,
        target=request.target,
        target_type=request.target_type.value,
        ctf_mode=request.ctf_mode,
        status=ScanStatus.PENDING,
        current_phase="pending",
        progress=0,
    )


@app.get("/api/scan/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: str):
    """Get the status of a scan."""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    scan = active_scans[scan_id]
    return ScanResponse(
        scan_id=scan["scan_id"],
        target=scan["target"],
        target_type=scan["target_type"],
        ctf_mode=scan["ctf_mode"],
        status=scan["status"],
        current_phase=scan.get("current_phase", "unknown"),
        progress=scan.get("progress", 0),
        errors=scan.get("errors", []),
        started_at=scan.get("started_at"),
        completed_at=scan.get("completed_at"),
        has_report=bool(scan.get("report_html")),
    )


@app.get("/api/scans")
async def list_scans():
    """List all scans."""
    return [
        ScanListItem(
            scan_id=s["scan_id"],
            target=s["target"],
            target_type=s["target_type"],
            ctf_mode=s["ctf_mode"],
            status=s["status"],
            started_at=s.get("started_at"),
            completed_at=s.get("completed_at"),
        )
        for s in active_scans.values()
    ]


@app.get("/api/report/{scan_id}")
async def get_report(scan_id: str):
    """Get the generated report HTML."""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    scan = active_scans[scan_id]
    report_html = scan.get("report_html", "")

    if not report_html:
        # Try loading from disk
        report_path = AGENT_ROOT / "reports" / f"report_{scan_id}.html"
        if report_path.exists():
            report_html = report_path.read_text(encoding="utf-8")
        else:
            raise HTTPException(status_code=404, detail="Report not yet generated")

    # Strip LLM markdown artifacts if present
    report_html = report_html.replace("```html\n", "").replace("```html", "").replace("```\n", "").replace("```", "")

    styled_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Pentest Report</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap');
            
            :root {{
                --colors-primary: #cc785c;
                --colors-ink: #141413;
                --colors-body: #3d3d3a;
                --colors-canvas: #faf9f5;
                --colors-border: #e6dfd8;
                --colors-surface: #ffffff;
                --colors-surface-soft: #f5f0e8;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                color: var(--colors-body);
                background-color: var(--colors-canvas);
                line-height: 1.65;
                max-width: 900px;
                margin: 0 auto;
                padding: 48px;
            }}
            
            h1, h2, h3, h4 {{
                font-family: 'Cormorant Garamond', serif;
                color: var(--colors-ink);
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                font-weight: 500;
                letter-spacing: -0.02em;
            }}
            
            h1 {{ font-size: 2.5em; border-bottom: 2px solid var(--colors-primary); padding-bottom: 10px; }}
            h2 {{ font-size: 1.8em; border-bottom: 1px solid var(--colors-border); padding-bottom: 8px; }}
            h3 {{ font-size: 1.4em; }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 24px 0;
                background: var(--colors-surface);
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                border: 1px solid var(--colors-border);
            }}
            
            th, td {{
                padding: 12px 16px;
                text-align: left;
                border-bottom: 1px solid var(--colors-border);
            }}
            
            th {{
                background-color: var(--colors-surface-soft);
                font-weight: 600;
                color: var(--colors-ink);
            }}
            
            tr:last-child td {{ border-bottom: none; }}
            
            pre, code {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.9em;
            }}
            
            code {{
                background-color: var(--colors-surface-soft);
                padding: 2px 6px;
                border-radius: 4px;
            }}
            
            pre {{
                padding: 16px;
                overflow-x: auto;
                background-color: #252320;
                color: #e8e0d2;
                border-radius: 8px;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
            }}
            
            ul, ol {{ margin-bottom: 16px; padding-left: 24px; }}
            li {{ margin-bottom: 8px; }}
            p {{ margin-bottom: 16px; }}
        </style>
    </head>
    <body>
        {report_html}
        <script>
            window.addEventListener('message', function(event) {{
                if (event.data === 'print_report') {{
                    window.print();
                }}
            }});
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=styled_report)


class LogMessage(BaseModel):
    message: str
    phase: str = "running"
    progress: int = 0

@app.post("/api/internal/stream_log/{scan_id}")
async def stream_log(scan_id: str, log: LogMessage):
    """Internal endpoint for MCP tools to stream raw stdout to the UI."""
    await ws_manager.broadcast(scan_id, {
        "scan_id": scan_id,
        "phase": log.phase,
        "message": log.message,
        "progress": log.progress,
        "timestamp": datetime.now().isoformat(),
    })
    return {"status": "ok"}

# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@app.websocket("/ws/{scan_id}")
async def websocket_endpoint(websocket: WebSocket, scan_id: str):
    """WebSocket endpoint for real-time scan status updates."""
    await ws_manager.connect(websocket, scan_id)
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            # Client can send ping/pong or commands
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, scan_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.disconnect(websocket, scan_id)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
