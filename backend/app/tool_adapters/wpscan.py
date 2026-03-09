"""WPScan tool adapter."""

from typing import Any
from .base import ToolAdapter


class WpscanAdapter(ToolAdapter):
    name = "wpscan"
    label = "WPScan"
    description = "WordPress security scanner"
    category = "web"
    binary = "wpscan"
    install_hint = "sudo apt update && sudo apt install -y wpscan  # or: sudo gem install wpscan"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "basic", "label": "Basic Scan", "description": "Basic WordPress scan"},
            {"name": "plugins", "label": "Enumerate Plugins", "description": "Enumerate all plugins"},
            {"name": "users", "label": "Enumerate Users", "description": "Enumerate WordPress users"},
            {"name": "full", "label": "Full Enumeration", "description": "Enumerate plugins, themes and users"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "enumerate", "label": "Enumerate", "type": "select", "required": False, "default": "", "options": ["", "p", "vp", "ap", "u", "t", "vt", "at", "cb", "dbe"], "description": "Enumeration mode"},
            {"name": "api_token", "label": "API Token", "type": "text", "required": False, "default": "", "options": [], "description": "WPScan API token for vulnerability data"},
            {"name": "detection_mode", "label": "Detection Mode", "type": "select", "required": False, "default": "mixed", "options": ["mixed", "passive", "aggressive"], "description": "Detection mode"},
            {"name": "plugins_detection", "label": "Plugins Detection", "type": "select", "required": False, "default": "passive", "options": ["passive", "aggressive", "mixed"], "description": "Plugin detection mode"},
            {"name": "force", "label": "Force", "type": "boolean", "required": False, "default": False, "options": [], "description": "Do not check if target is running WordPress"},
            {"name": "stealthy", "label": "Stealthy", "type": "boolean", "required": False, "default": False, "options": [], "description": "Use stealthy mode"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["wpscan", "--url", target, "--no-banner"]

        if preset == "basic":
            pass
        elif preset == "plugins":
            cmd += ["-e", "ap"]
        elif preset == "users":
            cmd += ["-e", "u"]
        elif preset == "full":
            cmd += ["-e", "ap,at,u"]

        allowed_enum = {"", "p", "vp", "ap", "u", "t", "vt", "at", "cb", "dbe"}
        if params.get("enumerate") and params["enumerate"] in allowed_enum:
            cmd += ["-e", params["enumerate"]]

        if params.get("api_token"):
            cmd += ["--api-token", str(params["api_token"])]

        if params.get("detection_mode") and params["detection_mode"] in ("mixed", "passive", "aggressive"):
            cmd += ["--detection-mode", params["detection_mode"]]

        if params.get("plugins_detection") and params["plugins_detection"] in ("passive", "aggressive", "mixed"):
            cmd += ["--plugins-detection", params["plugins_detection"]]

        if params.get("force"):
            cmd.append("--force")
        if params.get("stealthy"):
            cmd.append("--stealthy")

        return cmd
