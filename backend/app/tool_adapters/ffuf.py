"""FFUF tool adapter for web fuzzing."""

from typing import Any
from .base import ToolAdapter

class FfufAdapter(ToolAdapter):
    name = "ffuf"
    label = "FFUF"
    description = "Fast web fuzzer written in Go"
    category = "scanner"
    binary = "ffuf"
    install_hint = "go install github.com/ffuf/ffuf/v2@latest"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "common", "label": "Common Fuzzing", "description": "Fuzz directories with common wordlist"},
            {"name": "vhost", "label": "VHost Fuzzing", "description": "Fuzz virtual hosts"},
            {"name": "parameter", "label": "Parameter Fuzzing", "description": "Fuzz GET parameters"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "wordlist", "label": "Wordlist", "type": "text", "required": True, "default": "/usr/share/wordlists/dirb/common.txt", "options": [], "description": "Wordlist to use"},
            {"name": "threads", "label": "Threads", "type": "number", "required": False, "default": 40, "options": [], "description": "Number of threads"},
            {"name": "mc", "label": "Match Codes", "type": "text", "required": False, "default": "200,204,301,302,307,401,403,405", "options": [], "description": "Match HTTP status codes"},
            {"name": "fc", "label": "Filter Codes", "type": "text", "required": False, "default": "404", "options": [], "description": "Filter HTTP status codes"},
            {"name": "recursion", "label": "Recursion", "type": "boolean", "required": False, "default": False, "options": [], "description": "Scan recursively"},
            {"name": "user_agent", "label": "User-Agent", "type": "text", "required": False, "default": "ReconForge", "options": [], "description": "Custom User-Agent"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        wordlist = str(params.get("wordlist", "/usr/share/wordlists/dirb/common.txt"))
        
        # FFUF needs FUZZ keyword. We append it to the URL if it's missing.
        u = target
        if "FUZZ" not in u:
            u = u.rstrip("/") + "/FUZZ"

        cmd = ["ffuf", "-u", u, "-w", wordlist, "-t", str(params.get("threads", 40))]

        if params.get("mc"):
            cmd += ["-mc", str(params["mc"])]
        if params.get("fc"):
            cmd += ["-fc", str(params["fc"])]
        if params.get("recursion"):
            cmd.append("-recursion")
        if params.get("user_agent"):
            cmd += ["-H", f"User-Agent: {params['user_agent']}"]

        return cmd
