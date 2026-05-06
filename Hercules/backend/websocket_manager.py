"""
WebSocket Connection Manager
==============================
Manages WebSocket connections for real-time scan status updates.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections grouped by scan_id."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._message_buffer: Dict[str, List[dict]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, scan_id: str):
        """Accept and register a WebSocket connection for a scan."""
        await websocket.accept()
        async with self._lock:
            if scan_id not in self._connections:
                self._connections[scan_id] = set()
            self._connections[scan_id].add(websocket)

            # Send buffered messages to new connection
            if scan_id in self._message_buffer:
                for msg in self._message_buffer[scan_id]:
                    try:
                        await websocket.send_json(msg)
                    except Exception:
                        pass

        logger.info(f"WebSocket connected for scan {scan_id}")

    async def disconnect(self, websocket: WebSocket, scan_id: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            if scan_id in self._connections:
                self._connections[scan_id].discard(websocket)
                if not self._connections[scan_id]:
                    del self._connections[scan_id]
        logger.info(f"WebSocket disconnected for scan {scan_id}")

    async def broadcast(self, scan_id: str, message: dict):
        """Broadcast a message to all connections for a scan."""
        # Buffer the message
        async with self._lock:
            if scan_id not in self._message_buffer:
                self._message_buffer[scan_id] = []
            self._message_buffer[scan_id].append(message)

            # Keep only last 500 messages per scan
            if len(self._message_buffer[scan_id]) > 500:
                self._message_buffer[scan_id] = self._message_buffer[scan_id][-500:]

        # Send to active connections
        if scan_id in self._connections:
            dead_connections = set()
            for ws in self._connections[scan_id].copy():
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_connections.add(ws)

            # Clean up dead connections
            if dead_connections:
                async with self._lock:
                    if scan_id in self._connections:
                        self._connections[scan_id] -= dead_connections

    def get_buffer(self, scan_id: str) -> List[dict]:
        """Get buffered messages for a scan."""
        return self._message_buffer.get(scan_id, [])

    def clear_buffer(self, scan_id: str):
        """Clear message buffer for a completed scan."""
        self._message_buffer.pop(scan_id, None)
