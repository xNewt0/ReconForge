"""Subfinder tool adapter."""

from typing import Any
from .base import ToolAdapter


class SubfinderAdapter(ToolAdapter):
    name = "subfinder"
    label = "Subfinder"
    description = "Passive subdomain discovery tool"
    category = "recon"
    binary = "subfinder"
    install_hint = "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "basic", "label": "Basic Discovery", "description": "Passive subdomain enumeration"},
            {"name": "recursive", "label": "Recursive Discovery", "description": "Recursive subdomain enumeration"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "threads", "label": "Threads", "type": "number", "required": False, "default": 10, "options": [], "description": "Number of concurrent goroutines"},
            {"name": "timeout", "label": "Timeout", "type": "number", "required": False, "default": 30, "options": [], "description": "Timeout in seconds"},
            {"name": "recursive", "label": "Recursive", "type": "boolean", "required": False, "default": False, "options": [], "description": "Use recursive discovery"},
            {"name": "silent", "label": "Silent Mode", "type": "boolean", "required": False, "default": False, "options": [], "description": "Show only subdomains in output"},
            {"name": "all_sources", "label": "All Sources", "type": "boolean", "required": False, "default": False, "options": [], "description": "Use all sources for enumeration"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["subfinder", "-d", target]

        if preset == "recursive":
            cmd.append("-recursive")

        if params.get("threads"):
            threads = int(params["threads"])
            if 1 <= threads <= 100:
                cmd += ["-t", str(threads)]

        if params.get("timeout"):
            timeout = int(params["timeout"])
            if 1 <= timeout <= 300:
                cmd += ["-timeout", str(timeout)]

        if params.get("recursive"):
            cmd.append("-recursive")
        if params.get("silent"):
            cmd.append("-silent")
        if params.get("all_sources"):
            cmd.append("-all")

        return cmd
