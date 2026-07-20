"""Stable report types shared by the Phase 0 tools."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2, "blocker": 3}


@dataclass(frozen=True)
class Finding:
    code: str
    profile: str
    severity: str
    message: str
    pointer: str = ""
    disposition: str | None = None
    source_field: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass
class ProfileResult:
    name: str
    contract: str
    findings: list[Finding] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        severities = {item.severity for item in self.findings}
        if "blocker" in severities:
            return "blocked"
        if "error" in severities:
            return "fail"
        if "warning" in severities:
            return "warn"
        return "pass"

    def to_dict(self) -> dict[str, Any]:
        findings = sorted(
            self.findings,
            key=lambda item: (
                -SEVERITY_ORDER.get(item.severity, -1),
                item.code,
                item.pointer,
                item.message,
            ),
        )
        result: dict[str, Any] = {
            "contract": self.contract,
            "status": self.status,
            "findings": [item.to_dict() for item in findings],
        }
        if self.details:
            result["details"] = self.details
        return result
