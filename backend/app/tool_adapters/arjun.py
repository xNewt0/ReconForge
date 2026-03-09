"""Arjun tool adapter for HTTP parameter discovery."""

from typing import Any
from .base import ToolAdapter

class ArjunAdapter(ToolAdapter):
    name = "arjun"
    label = "Arjun"
    description = "HTTP parameter discovery suite"
    category = "scanner"
    binary = "arjun"
    install_hint = "pip3 install arjun"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "get", "label": "GET Parameter Scan", "description": "Scan for hidden GET parameters"},
            {"name": "post", "label": "POST Parameter Scan", "description": "Scan for hidden POST parameters"},
            {"name": "json", "label": "JSON Body Scan", "description": "Scan for hidden parameters in JSON body"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "threads", "label": "Threads", "type": "number", "required": False, "default": 20, "options": [], "description": "Number of concurrent threads"},
            {"name": "wordlist", "label": "Wordlist", "type": "text", "required": False, "default": "", "options": [], "description": "Path to custom wordlist"},
            {"name": "passive", "label": "Passive Mode", "type": "boolean", "required": False, "default": False, "options": [], "description": "Gather parameters from passive sources like Wayback Machine"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["arjun", "-u", target]

        if preset == "post":
            cmd += ["-m", "POST"]
        elif preset == "json":
            cmd += ["-m", "JSON"]
        else:
            cmd += ["-m", "GET"]

        if params.get("threads"):
            cmd += ["-t", str(params["threads"])]
        if params.get("wordlist"):
            cmd += ["-w", params["wordlist"]]
        if params.get("passive"):
            cmd.append("--passive")

        return cmd
