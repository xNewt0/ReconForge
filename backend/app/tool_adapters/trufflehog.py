"""TruffleHog tool adapter for finding secrets."""

from typing import Any
from .base import ToolAdapter

class TrufflehogAdapter(ToolAdapter):
    name = "trufflehog"
    label = "TruffleHog"
    description = "Find secrets, API keys and credentials in source code or files"
    category = "vulnerability"
    binary = "trufflehog"
    install_hint = "brew install trufflehog OR docker run --rm -it trufflesecurity/trufflehog"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "filesystem", "label": "Scan Filesystem", "description": "Scan a local directory for secrets"},
            {"name": "github", "label": "Scan GitHub", "description": "Scan a GitHub repository for secrets"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "only_verified", "label": "Only Verified", "type": "boolean", "required": False, "default": True, "options": [], "description": "Only show secrets that can be verified against the provider"},
            {"name": "json", "label": "JSON Output", "type": "boolean", "required": False, "default": True, "options": [], "description": "Output results in JSON format"},
            {"name": "extra_args", "label": "Extra Arguments", "type": "text", "required": False, "default": "", "options": [], "description": "Additional command line arguments"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["trufflehog"]

        if preset == "github":
            cmd += ["github", "--repo", target]
        else:
            cmd += ["filesystem", target]

        if params.get("only_verified"):
            cmd.append("--only-verified")
        if params.get("json"):
            cmd.append("--json")
        if params.get("extra_args"):
            cmd += params["extra_args"].split()

        return cmd
