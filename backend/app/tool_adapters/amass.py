"""Amass tool adapter for deep subdomain enumeration."""

from typing import Any
from .base import ToolAdapter

class AmassAdapter(ToolAdapter):
    name = "amass"
    label = "Amass"
    description = "In-depth Attack Surface Mapping and Asset Discovery"
    category = "recon"
    binary = "amass"
    install_hint = "sudo apt install -y amass"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "enum", "label": "Passive Enumeration", "description": "Passive subdomain discovery via OSINT"},
            {"name": "active", "label": "Active Scan", "description": "Active enumeration including DNS resolution"},
            {"name": "intel", "label": "Intelligence Gathering", "description": "Gather intelligence about the target organization"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "passive", "label": "Passive Mode", "type": "boolean", "required": False, "default": True, "options": [], "description": "Disable DNS resolution and active gathering"},
            {"name": "active", "label": "Active Mode", "type": "boolean", "required": False, "default": False, "options": [], "description": "Enable active DNS resolution and zone transfers"},
            {"name": "brute", "label": "Brute Force", "type": "boolean", "required": False, "default": False, "options": [], "description": "Attempt subdomain brute forcing"},
            {"name": "config", "label": "Config File", "type": "text", "required": False, "default": "", "options": [], "description": "Path to Amass configuration file"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["amass"]

        if preset == "intel":
            cmd += ["intel", "-d", target, "-whois"]
        else:
            cmd += ["enum", "-d", target]
            if preset == "enum" or params.get("passive"):
                cmd.append("-passive")
            if preset == "active" or params.get("active"):
                cmd.append("-active")
            if params.get("brute"):
                cmd.append("-brute")
            if params.get("config"):
                cmd += ["-config", params["config"]]

        return cmd
