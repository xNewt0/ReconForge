"""Nuclei tool adapter for advanced vulnerability scanning."""

from typing import Any
from .base import ToolAdapter

class NucleiAdapter(ToolAdapter):
    name = "nuclei"
    label = "Nuclei"
    description = "Fast and customizable vulnerability scanner based on simple YAML based DSL"
    category = "vulnerability"
    binary = "nuclei"
    install_hint = "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "critical", "label": "Critical & High Only", "description": "Scan only for high and critical severity templates"},
            {"name": "technologies", "label": "Tech Detection", "description": "Identify technologies used by the target"},
            {"name": "fuzzing", "label": "Fuzzing Templates", "description": "Run fuzzing specific templates"},
            {"name": "exposures", "label": "Exposures Scan", "description": "Scan for common exposures (tokens, configs, etc.)"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "severity", "label": "Severity", "type": "text", "required": False, "default": "info,low,medium,high,critical", "options": [], "description": "Template severities to run (e.g. high,critical)"},
            {"name": "tags", "label": "Tags", "type": "text", "required": False, "default": "", "options": [], "description": "Filter templates by tags (e.g. cve,xss)"},
            {"name": "templates", "label": "Specific Templates", "type": "text", "required": False, "default": "", "options": [], "description": "Specific templates to run (paths)"},
            {"name": "rate_limit", "label": "Rate Limit", "type": "number", "required": False, "default": 150, "options": [], "description": "Max requests per second"},
            {"name": "update_templates", "label": "Update Templates", "type": "boolean", "required": False, "default": True, "options": [], "description": "Update nuclei templates before scan"},
            {"name": "headless", "label": "Headless Mode", "type": "boolean", "required": False, "default": False, "options": [], "description": "Enable headless templates (requires browser)"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["nuclei", "-u", target, "-no-color"]

        if params.get("update_templates"):
            cmd.append("-ut")

        if preset == "critical":
            cmd += ["-severity", "high,critical"]
        elif preset == "technologies":
            cmd += ["-tags", "tech"]
        elif preset == "fuzzing":
            cmd += ["-tags", "fuzz"]
        elif preset == "exposures":
            cmd += ["-tags", "exposure"]

        if params.get("severity") and "-severity" not in cmd:
            cmd += ["-severity", str(params["severity"])]

        if params.get("tags") and "-tags" not in cmd:
            cmd += ["-tags", str(params["tags"])]

        if params.get("templates"):
            cmd += ["-t", str(params["templates"])]

        if params.get("rate_limit"):
            cmd += ["-rl", str(params["rate_limit"])]

        if params.get("headless"):
            cmd.append("-headless")

        return cmd
