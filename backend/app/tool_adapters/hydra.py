"""Hydra tool adapter."""

from typing import Any
from .base import ToolAdapter


class HydraAdapter(ToolAdapter):
    name = "hydra"
    label = "Hydra"
    description = "Network login brute-force tool"
    category = "brute-force"
    binary = "hydra"
    install_hint = "sudo apt update && sudo apt install -y hydra"

    PROTOCOLS = ["ssh", "ftp", "http-get", "http-post-form", "rdp", "smb", "telnet", "mysql", "pop3", "imap"]

    def get_presets(self) -> list[dict]:
        return [
            {"name": "ssh", "label": "SSH Brute Force", "description": "Brute-force SSH login"},
            {"name": "ftp", "label": "FTP Brute Force", "description": "Brute-force FTP login"},
            {"name": "http", "label": "HTTP Brute Force", "description": "Brute-force HTTP authentication"},
            {"name": "form", "label": "HTTP Form Brute Force", "description": "Brute-force HTTP login form"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "protocol", "label": "Protocol", "type": "select", "required": True, "default": "ssh", "options": self.PROTOCOLS, "description": "Target service protocol"},
            {"name": "username", "label": "Username", "type": "text", "required": False, "default": "", "options": [], "description": "Single username"},
            {"name": "username_list", "label": "Username List", "type": "text", "required": False, "default": "", "options": [], "description": "Path to username wordlist"},
            {"name": "password", "label": "Password", "type": "text", "required": False, "default": "", "options": [], "description": "Single password"},
            {"name": "password_list", "label": "Password List", "type": "text", "required": False, "default": "", "options": [], "description": "Path to password wordlist"},
            {"name": "threads", "label": "Threads", "type": "number", "required": False, "default": 16, "options": [], "description": "Number of parallel connections"},
            {"name": "exit_on_success", "label": "Exit on Success", "type": "boolean", "required": False, "default": True, "options": [], "description": "Stop after first found login/password pair (-f)"},
            {"name": "try_empty", "label": "Try Empty/Login", "type": "boolean", "required": False, "default": False, "options": [], "description": "Try empty password and login as password (-e ns)"},
            {"name": "port", "label": "Port", "type": "number", "required": False, "default": None, "options": [], "description": "Service port"},
            {"name": "form_params", "label": "Form Parameters", "type": "text", "required": False, "default": "", "options": [], "description": "For http-post-form: path:params:failure_string"},
            {"name": "verbose", "label": "Verbose", "type": "boolean", "required": False, "default": False, "options": [], "description": "Show verbose output"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        protocol = str(params.get("protocol", "ssh"))
        if protocol not in self.PROTOCOLS:
            protocol = "ssh"

        if preset == "ssh":
            protocol = "ssh"
        elif preset == "ftp":
            protocol = "ftp"
        elif preset == "http":
            protocol = "http-get"
        elif preset == "form":
            protocol = "http-post-form"

        cmd = ["hydra"]

        if params.get("username"):
            cmd += ["-l", str(params["username"])]
        elif params.get("username_list"):
            cmd += ["-L", str(params["username_list"])]

        if params.get("password"):
            cmd += ["-p", str(params["password"])]
        elif params.get("password_list"):
            cmd += ["-P", str(params["password_list"])]

        threads = int(params.get("threads", 16))
        if 1 <= threads <= 64:
            cmd += ["-t", str(threads)]

        if params.get("exit_on_success"):
            cmd.append("-f")
        
        if params.get("try_empty"):
            cmd += ["-e", "ns"]

        if params.get("port"):
            port = int(params["port"])
            if 1 <= port <= 65535:
                cmd += ["-s", str(port)]

        if params.get("verbose"):
            cmd.append("-V")

        if protocol == "http-post-form" and params.get("form_params"):
            cmd += [target, protocol, str(params["form_params"])]
        else:
            cmd += [target, protocol]

        return cmd
