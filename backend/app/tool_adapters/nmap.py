"""Nmap tool adapter."""

from typing import Any
from .base import ToolAdapter


class NmapAdapter(ToolAdapter):
    name = "nmap"
    label = "Nmap"
    description = "Network exploration and port scanning"
    category = "recon"
    binary = "nmap"
    install_hint = "sudo apt update && sudo apt install -y nmap"

    TIMING_TEMPLATES = ["T0", "T1", "T2", "T3", "T4", "T5"]

    def get_presets(self) -> list[dict]:
        return [
            {"name": "quick", "label": "Quick Scan", "description": "Fast scan of top 100 ports"},
            {"name": "full", "label": "Full Port Scan", "description": "Scan all 65535 ports"},
            {"name": "service", "label": "Service Detection", "description": "Detect service versions on open ports"},
            {"name": "os", "label": "OS Detection", "description": "Detect operating system"},
            {"name": "aggressive", "label": "Aggressive Scan", "description": "OS detection, version, script scanning and traceroute"},
            {"name": "scripts", "label": "Script Scan", "description": "Run default NSE scripts"},
            {"name": "vuln", "label": "Vulnerability Scan", "description": "Run vulnerability detection scripts"},
            {"name": "udp", "label": "UDP Scan", "description": "Scan UDP ports"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "ports", "label": "Port Range", "type": "text", "required": False, "default": "", "options": [], "description": "e.g. 22,80,443 or 1-1024"},
            {"name": "top_ports", "label": "Top Ports", "type": "number", "required": False, "default": 0, "options": [], "description": "Scan most common X ports"},
            {"name": "timing", "label": "Timing Template", "type": "select", "required": False, "default": "T3", "options": self.TIMING_TEMPLATES, "description": "T0=paranoid to T5=insane"},
            {"name": "service_detection", "label": "Service Detection", "type": "boolean", "required": False, "default": False, "options": [], "description": "Detect service versions (-sV)"},
            {"name": "os_detection", "label": "OS Detection", "type": "boolean", "required": False, "default": False, "options": [], "description": "Detect operating system (-O)"},
            {"name": "script_scan", "label": "Script Scan", "type": "boolean", "required": False, "default": False, "options": [], "description": "Run default scripts (-sC)"},
            {"name": "udp_scan", "label": "UDP Scan", "type": "boolean", "required": False, "default": False, "options": [], "description": "UDP scan (-sU)"},
            {"name": "aggressive", "label": "Aggressive Mode", "type": "boolean", "required": False, "default": False, "options": [], "description": "Aggressive scan (-A)"},
            {"name": "no_ping", "label": "No Ping", "type": "boolean", "required": False, "default": False, "options": [], "description": "Treat all hosts as online (-Pn)"},
            {"name": "packet_trace", "label": "Packet Trace", "type": "boolean", "required": False, "default": False, "options": [], "description": "Show all packets sent/received"},
            {"name": "scripts", "label": "NSE Scripts", "type": "text", "required": False, "default": "", "options": [], "description": "Comma-separated script names"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        cmd = ["nmap"]

        if preset == "quick":
            cmd += ["-F", "-T4"]
        elif preset == "full":
            cmd += ["-p-", "-T4"]
        elif preset == "service":
            cmd += ["-sV", "-T3"]
        elif preset == "os":
            cmd += ["-O", "-T3"]
        elif preset == "aggressive":
            cmd += ["-A", "-T4"]
        elif preset == "scripts":
            cmd += ["-sC", "-T3"]
        elif preset == "vuln":
            cmd += ["--script", "vuln", "-T4"]
        elif preset == "udp":
            cmd += ["-sU", "-T3"]

        params = self.validate(params)

        if params.get("ports"):
            port_val = str(params["ports"])
            if all(c in "0123456789,- " for c in port_val):
                cmd += ["-p", port_val]
        
        if params.get("top_ports") and int(params["top_ports"]) > 0:
            cmd += ["--top-ports", str(params["top_ports"])]

        if params.get("timing") and params["timing"] in self.TIMING_TEMPLATES:
            cmd.append(f"-{params['timing']}")

        if params.get("service_detection"):
            cmd.append("-sV")
        if params.get("os_detection"):
            cmd.append("-O")
        if params.get("script_scan"):
            cmd.append("-sC")
        if params.get("udp_scan"):
            cmd.append("-sU")
        if params.get("aggressive"):
            cmd.append("-A")
        if params.get("no_ping"):
            cmd.append("-Pn")
        if params.get("packet_trace"):
            cmd.append("--packet-trace")

        if params.get("scripts"):
            scripts = str(params["scripts"])
            if all(c.isalnum() or c in "-_,." for c in scripts):
                cmd += ["--script", scripts]

        cmd.append(target)
        return cmd
