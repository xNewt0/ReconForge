"""WPProbe WordPress detection adapter."""

from typing import Any
from .base import ToolAdapter


class WpprobeAdapter(ToolAdapter):
    name = "wpprobe"
    label = "WPProbe"
    description = "WordPress detection and enumeration"
    category = "web"
    binary = "wpprobe"
    install_hint = "sudo apt update && sudo apt install -y wpprobe  # if unavailable: install wpprobe from its upstream"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "detect", "label": "WordPress Detection", "description": "Detect if target runs WordPress"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "verbose", "label": "Verbose", "type": "boolean", "required": False, "default": False, "options": [], "description": "Enable verbose output"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["wpprobe", target]

        if params.get("verbose"):
            cmd.append("-v")

        return cmd
