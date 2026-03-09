"""TestSSL tool adapter for SSL/TLS testing."""

from typing import Any
from .base import ToolAdapter

class TestsslAdapter(ToolAdapter):
    name = "testssl"
    label = "TestSSL"
    description = "Command line tool which checks a server's service on any port for the support of TLS/SSL ciphers, protocols"
    category = "vulnerability"
    binary = "testssl"
    install_hint = "git clone --depth 1 https://github.com/drwetter/testssl.sh.git"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "standard", "label": "Standard Scan", "description": "General check for vulnerabilities, protocols and ciphers"},
            {"name": "vuln_only", "label": "Vulnerabilities Only", "description": "Only check for known vulnerabilities (Heartbleed, BEAST, etc.)"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "severity", "label": "Severity", "type": "select", "required": False, "default": "MEDIUM", "options": ["LOW", "MEDIUM", "HIGH", "CRITICAL"], "description": "Minimum severity to report"},
            {"name": "quiet", "label": "Quiet", "type": "boolean", "required": False, "default": True, "options": [], "description": "Hide banner and other metadata"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["testssl.sh"]

        if preset == "vuln_only":
            cmd.append("-U")
        else:
            cmd.append("-p") # Protocols
            cmd.append("-S") # Ciphers
            cmd.append("-U") # Vulns

        if params.get("quiet"):
            cmd.append("--quiet")

        cmd.append(target)
        return cmd
