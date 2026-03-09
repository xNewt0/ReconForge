"""Katana web crawler adapter."""

from typing import Any
from .base import ToolAdapter


class KatanaAdapter(ToolAdapter):
    name = "katana"
    label = "Katana"
    description = "Fast web crawler for endpoint discovery"
    category = "crawl"
    binary = "katana"
    install_hint = "go install -v github.com/projectdiscovery/katana/cmd/katana@latest"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "basic", "label": "Basic Crawl", "description": "Standard web crawl"},
            {"name": "deep", "label": "Deep Crawl", "description": "Deep crawl with higher depth"},
            {"name": "js", "label": "JavaScript Crawl", "description": "Headless crawl with JavaScript rendering"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "depth", "label": "Crawl Depth", "type": "number", "required": False, "default": 3, "options": [], "description": "Maximum crawl depth"},
            {"name": "threads", "label": "Threads", "type": "number", "required": False, "default": 10, "options": [], "description": "Number of concurrent threads"},
            {"name": "headless", "label": "Headless Browser", "type": "boolean", "required": False, "default": False, "options": [], "description": "Use headless browser for JavaScript rendering"},
            {"name": "js_crawl", "label": "JavaScript Crawl", "type": "boolean", "required": False, "default": False, "options": [], "description": "Enable JavaScript file parsing"},
            {"name": "scope_domain", "label": "Scope to Domain", "type": "boolean", "required": False, "default": True, "options": [], "description": "Restrict crawl to target domain"},
            {"name": "timeout", "label": "Timeout", "type": "number", "required": False, "default": 15, "options": [], "description": "Request timeout in seconds"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["katana", "-u", target]

        if preset == "deep":
            cmd += ["-d", "10"]
        elif preset == "js":
            cmd += ["-headless", "-jc"]

        if params.get("depth"):
            depth = int(params["depth"])
            if 1 <= depth <= 20:
                cmd += ["-d", str(depth)]

        if params.get("threads"):
            threads = int(params["threads"])
            if 1 <= threads <= 100:
                cmd += ["-c", str(threads)]

        if params.get("headless"):
            cmd.append("-headless")
        if params.get("js_crawl"):
            cmd.append("-jc")
        if params.get("scope_domain"):
            cmd.append("-fs")
            cmd.append("dn")
        if params.get("timeout"):
            timeout = int(params["timeout"])
            if 1 <= timeout <= 120:
                cmd += ["-timeout", str(timeout)]

        return cmd
