"""Gobuster tool adapter."""

from typing import Any
from .base import ToolAdapter


class GobusterAdapter(ToolAdapter):
    name = "gobuster"
    label = "Gobuster"
    description = "Directory, DNS and VHost brute-forcing"
    category = "scanner"
    binary = "gobuster"
    install_hint = "sudo apt update && sudo apt install -y gobuster"

    def get_presets(self) -> list[dict]:
        return [
            {"name": "dir_common", "label": "Directory Scan (Common)", "description": "Directory brute-force with common wordlist"},
            {"name": "dir_medium", "label": "Directory Scan (Medium)", "description": "Directory brute-force with medium wordlist"},
            {"name": "dns", "label": "DNS Subdomain Scan", "description": "DNS subdomain enumeration"},
            {"name": "vhost", "label": "VHost Scan", "description": "Virtual host discovery"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "mode", "label": "Mode", "type": "select", "required": True, "default": "dir", "options": ["dir", "dns", "vhost"], "description": "Gobuster mode"},
            {"name": "wordlist", "label": "Wordlist", "type": "text", "required": True, "default": "/usr/share/wordlists/dirb/common.txt", "options": [], "description": "Path to wordlist file"},
            {"name": "threads", "label": "Threads", "type": "number", "required": False, "default": 10, "options": [], "description": "Number of concurrent threads"},
            {"name": "extensions", "label": "Extensions", "type": "text", "required": False, "default": "", "options": [], "description": "File extensions to search for (e.g. php,html,txt)"},
            {"name": "status_codes", "label": "Status Codes", "type": "text", "required": False, "default": "", "options": [], "description": "Include status codes (e.g. 200,301,302)"},
            {"name": "useragent", "label": "User-Agent", "type": "text", "required": False, "default": "Mozilla/5.0 ReconForge/1.0", "options": [], "description": "Custom User-Agent string"},
            {"name": "proxy", "label": "Proxy", "type": "text", "required": False, "default": "", "options": [], "description": "Proxy to use for requests (e.g. http://127.0.0.1:8080)"},
            {"name": "timeout", "label": "Timeout", "type": "number", "required": False, "default": 10, "options": [], "description": "HTTP Timeout (seconds)"},
            {"name": "headers", "label": "Headers", "type": "text", "required": False, "default": "", "options": [], "description": "Custom HTTP headers (e.g. Header1:Value1,Header2:Value2)"},
            {"name": "follow_redirect", "label": "Follow Redirects", "type": "boolean", "required": False, "default": False, "options": [], "description": "Follow redirects"},
            {"name": "no_tls_validation", "label": "Skip TLS Validation", "type": "boolean", "required": False, "default": False, "options": [], "description": "Skip TLS certificate verification"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        mode = str(params.get("mode", "dir"))
        if mode not in ("dir", "dns", "vhost"):
            mode = "dir"

        wordlist = str(params.get("wordlist", "/usr/share/wordlists/dirb/common.txt"))
        
        if mode == "dns":
            cmd = ["gobuster", mode, "-d", target, "-w", wordlist]
        else:
            cmd = ["gobuster", mode, "-u", target, "-w", wordlist]

        if preset == "dir_common":
            cmd = ["gobuster", "dir", "-u", target, "-w", "/usr/share/wordlists/dirb/common.txt"]
        elif preset == "dir_medium":
            cmd = ["gobuster", "dir", "-u", target, "-w", "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"]
        elif preset == "dns":
            cmd = ["gobuster", "dns", "-d", target, "-w", wordlist]
        elif preset == "vhost":
            cmd = ["gobuster", "vhost", "-u", target, "-w", wordlist]

        threads = int(params.get("threads", 10))
        if 1 <= threads <= 100:
            cmd += ["-t", str(threads)]

        if params.get("extensions"):
            ext = str(params["extensions"])
            if all(c.isalnum() or c in ",." for c in ext):
                cmd += ["-x", ext]

        if params.get("status_codes"):
            codes = str(params["status_codes"])
            if all(c.isdigit() or c == "," for c in codes):
                cmd += ["-s", codes]

        if params.get("useragent"):
            cmd += ["-a", str(params["useragent"])]

        if params.get("proxy"):
            cmd += ["-p", str(params["proxy"])]

        if params.get("timeout"):
            cmd += ["--timeout", f"{params['timeout']}s"]

        if params.get("headers"):
            hdrs = str(params["headers"]).split(",")
            for h in hdrs:
                if ":" in h:
                    cmd += ["-H", h.strip()]

        if params.get("follow_redirect"):
            cmd.append("-r")

        if params.get("no_tls_validation"):
            cmd.append("-k")

        return cmd
