"""Nikto tool adapter."""

from typing import Any
from .base import ToolAdapter


class NiktoAdapter(ToolAdapter):
    name = "nikto"
    label = "Nikto"
    description = "Web server vulnerability scanner"
    category = "web"
    binary = "nikto"
    install_hint = "sudo apt update && sudo apt install -y nikto"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "full", "label": "Full Scan", "description": "Complete web vulnerability scan"},
            {"name": "quick", "label": "Quick Scan", "description": "Quick scan with common checks"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "port", "label": "Port", "type": "number", "required": False, "default": 80, "options": [], "description": "Target port"},
            {"name": "ssl", "label": "Use SSL", "type": "boolean", "required": False, "default": False, "options": [], "description": "Use SSL/TLS connection"},
            {"name": "tuning", "label": "Tuning", "type": "text", "required": False, "default": "", "options": [], "description": "Scan tuning (1-9, a-c)"},
            {"name": "no_404", "label": "No 404 Checking", "type": "boolean", "required": False, "default": False, "options": [], "description": "Disable 404 guessing"},
            {"name": "evasion", "label": "Evasion", "type": "text", "required": False, "default": "", "options": [], "description": "Evasion technique (1-8)"},
            {"name": "timeout", "label": "Timeout", "type": "number", "required": False, "default": 10, "options": [], "description": "Timeout per request in seconds"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["nikto", "-h", target, "-nointeractive"]

        if params.get("port"):
            port = int(params["port"])
            if 1 <= port <= 65535:
                cmd += ["-p", str(port)]

        if params.get("ssl"):
            cmd.append("-ssl")

        if params.get("tuning"):
            tuning = str(params["tuning"])
            if all(c in "0123456789abc" for c in tuning):
                cmd += ["-Tuning", tuning]

        if params.get("no_404"):
            cmd.append("-no404")

        if params.get("evasion"):
            evasion = str(params["evasion"])
            if all(c in "12345678" for c in evasion):
                cmd += ["-evasion", evasion]

        if params.get("timeout"):
            timeout = int(params["timeout"])
            if 1 <= timeout <= 300:
                cmd += ["-timeout", str(timeout)]

        return cmd
