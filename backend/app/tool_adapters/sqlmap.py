"""SQLMap tool adapter."""

from typing import Any
from .base import ToolAdapter


class SqlmapAdapter(ToolAdapter):
    name = "sqlmap"
    label = "SQLMap"
    description = "Automatic SQL injection detection and exploitation"
    category = "web"
    binary = "sqlmap"
    install_hint = "sudo apt update && sudo apt install -y sqlmap"
    enabled = True

    def get_presets(self) -> list[dict]:
        return [
            {"name": "basic", "label": "Basic Scan", "description": "Test URL for SQL injection"},
            {"name": "dbs", "label": "Enumerate Databases", "description": "List accessible databases"},
            {"name": "tables", "label": "Enumerate Tables", "description": "List tables in a database"},
            {"name": "dump", "label": "Dump Data", "description": "Dump table contents"},
            {"name": "full", "label": "Full Audit", "description": "Comprehensive scan with high level/risk"},
        ]

    def get_parameters(self) -> list[dict]:
        return [
            {"name": "dbs", "label": "Enumerate Databases", "type": "boolean", "required": False, "default": False, "options": [], "description": "Enumerate DBMS databases"},
            {"name": "tables", "label": "Enumerate Tables", "type": "boolean", "required": False, "default": False, "options": [], "description": "Enumerate DBMS tables"},
            {"name": "dump", "label": "Dump", "type": "boolean", "required": False, "default": False, "options": [], "description": "Dump DBMS database table entries"},
            {"name": "database", "label": "Database Name", "type": "text", "required": False, "default": "", "options": [], "description": "Target database name (-D)"},
            {"name": "table", "label": "Table Name", "type": "text", "required": False, "default": "", "options": [], "description": "Target table name (-T)"},
            {"name": "level", "label": "Level", "type": "select", "required": False, "default": "1", "options": ["1", "2", "3", "4", "5"], "description": "Detection level (1-5)"},
            {"name": "risk", "label": "Risk", "type": "select", "required": False, "default": "1", "options": ["1", "2", "3"], "description": "Risk level (1-3)"},
            {"name": "threads", "label": "Threads", "type": "number", "required": False, "default": 1, "options": [], "description": "Number of concurrent threads"},
            {"name": "random_agent", "label": "Random Agent", "type": "boolean", "required": False, "default": True, "options": [], "description": "Use randomly selected HTTP User-Agent header"},
            {"name": "proxy", "label": "Proxy", "type": "text", "required": False, "default": "", "options": [], "description": "Use a proxy to connect to the target URL"},
            {"name": "tor", "label": "Use Tor", "type": "boolean", "required": False, "default": False, "options": [], "description": "Use Tor network"},
            {"name": "dbms", "label": "DBMS", "type": "text", "required": False, "default": "", "options": [], "description": "Force back-end DBMS to this value (e.g. mysql)"},
            {"name": "technique", "label": "Techniques", "type": "text", "required": False, "default": "BEUSTQ", "options": [], "description": "SQL injection techniques to use (default BEUSTQ)"},
            {"name": "hex", "label": "Hex", "type": "boolean", "required": False, "default": False, "options": [], "description": "Use DBMS hex function for data retrieval"},
            {"name": "batch", "label": "Batch Mode", "type": "boolean", "required": False, "default": True, "options": [], "description": "Never ask for user input, use defaults"},
        ]

    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        params = self.validate(params)
        cmd = ["sqlmap", "-u", target, "--batch"]

        if preset == "dbs":
            cmd.append("--dbs")
        elif preset == "tables":
            cmd.append("--tables")
            if params.get("database"):
                cmd += ["-D", str(params["database"])]
        elif preset == "dump":
            cmd.append("--dump")
            if params.get("database"):
                cmd += ["-D", str(params["database"])]
            if params.get("table"):
                cmd += ["-T", str(params["table"])]
        elif preset == "full":
            cmd += ["--level", "5", "--risk", "3", "--dbs"]

        if params.get("dbs") and "--dbs" not in cmd:
            cmd.append("--dbs")
        if params.get("tables") and "--tables" not in cmd:
            cmd.append("--tables")
        if params.get("dump") and "--dump" not in cmd:
            cmd.append("--dump")

        if params.get("database"):
            if "-D" not in cmd:
                cmd += ["-D", str(params["database"])]
        if params.get("table"):
            if "-T" not in cmd:
                cmd += ["-T", str(params["table"])]

        if params.get("level") and params["level"] in ("1", "2", "3", "4", "5") and "--level" not in cmd:
            cmd += ["--level", params["level"]]

        if params.get("risk") and params["risk"] in ("1", "2", "3") and "--risk" not in cmd:
            cmd += ["--risk", params["risk"]]

        if params.get("threads"):
            threads = int(params["threads"])
            if 1 <= threads <= 10:
                cmd += ["--threads", str(threads)]
        
        if params.get("random_agent"):
            cmd.append("--random-agent")
        
        if params.get("proxy"):
            cmd += ["--proxy", str(params["proxy"])]
        
        if params.get("tor"):
            cmd.append("--tor")
        
        if params.get("dbms"):
            cmd += ["--dbms", str(params["dbms"])]
        
        if params.get("technique"):
            cmd += ["--technique", str(params["technique"])]
        
        if params.get("hex"):
            cmd.append("--hex")

        return cmd
