"""
Pydantic Models for the Pentest Agent API
==========================================
Request/response schemas for scan management.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TargetType(str, Enum):
    IP = "ip"
    IP_RANGE = "ip_range"
    WEBSITE = "website"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class ComplianceFramework(str, Enum):
    NONE = "None"
    PCI_DSS = "PCI-DSS"
    HIPAA = "HIPAA"
    SOC2 = "SOC2"
    ISO27001 = "ISO 27001"
    NIST = "NIST CSF"
    GDPR = "GDPR"
    OWASP = "OWASP Top 10"


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    """Request to start a new penetration test scan."""

    target: str = Field(
        ...,
        description="Target IP address, IP range (CIDR), or website URL",
        examples=["192.168.1.1", "10.0.0.0/24", "https://example.com"],
    )
    target_type: TargetType = Field(
        default=TargetType.IP,
        description="Type of target being scanned",
    )
    ctf_mode: bool = Field(
        default=False,
        description="Enable CTF mode for exploitation and post-exploitation",
    )
    special_instructions: str = Field(
        default="",
        description="Special instructions for the agents (compliance notes, challenge info, etc.)",
    )
    compliance_framework: ComplianceFramework = Field(
        default=ComplianceFramework.NONE,
        description="Compliance framework to map findings against",
    )

    @model_validator(mode="after")
    def validate_target_format(self):
        import re
        t = self.target.strip()
        if not t:
            raise ValueError("Target cannot be empty")
        if self.target_type == TargetType.IP:
            if not re.match(r"^(\d{1,3}\.){3}\d{1,3}$", t):
                raise ValueError(f"Invalid IP address: {t}")
            if not all(0 <= int(o) <= 255 for o in t.split(".")):
                raise ValueError(f"IP octets must be 0-255: {t}")
        elif self.target_type == TargetType.IP_RANGE:
            if not re.match(r"^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$", t):
                raise ValueError(f"Invalid CIDR range: {t}")
            ip, cidr = t.split("/")
            if not (0 <= int(cidr) <= 32):
                raise ValueError(f"CIDR prefix must be 0-32: {t}")
            if not all(0 <= int(o) <= 255 for o in ip.split(".")):
                raise ValueError(f"IP octets must be 0-255: {t}")
        elif self.target_type == TargetType.WEBSITE:
            if not re.match(r"^(https?://)?([\w-]+\.)+[a-zA-Z]{2,}(:\d{1,5})?(/.*)?$", t):
                raise ValueError(f"Invalid domain or URL: {t}")
        self.target = t
        return self


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class PhaseStatus(BaseModel):
    """Status of a single pentest phase."""

    name: str
    status: str = "pending"  # pending, running, completed, error, skipped
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class ScanResponse(BaseModel):
    """Response with scan status and results."""

    scan_id: str
    target: str
    target_type: str
    ctf_mode: bool
    status: ScanStatus
    current_phase: str = "idle"
    progress: int = 0
    phases: List[PhaseStatus] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    has_report: bool = False


class ScanListItem(BaseModel):
    """Summary item for scan list."""

    scan_id: str
    target: str
    target_type: str
    ctf_mode: bool
    status: ScanStatus
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class StatusUpdate(BaseModel):
    """WebSocket status update message."""

    scan_id: str
    phase: str
    message: str
    progress: int = 0
    timestamp: str = ""
    agent_name: Optional[str] = None
    tool_name: Optional[str] = None
