"""Base tool adapter abstract class."""

from abc import ABC, abstractmethod
from typing import Any
import shutil


class ToolAdapter(ABC):
    """Abstract base for all tool adapters."""

    name: str = ""
    label: str = ""
    description: str = ""
    category: str = ""  # recon, scanner, brute-force, web, crawl
    binary: str = ""
    enabled: bool = True

    # Human-friendly installation command hint (best-effort, usually Debian/Kali based)
    install_hint: str = ""

    @abstractmethod
    def get_presets(self) -> list[dict]:
        """Return available preset scan profiles."""
        ...

    @abstractmethod
    def get_parameters(self) -> list[dict]:
        """Return available configurable parameters."""
        ...

    @abstractmethod
    def build_command(self, target: str, params: dict[str, Any], preset: str = "") -> list[str]:
        """Build a safe command list from validated parameters."""
        ...

    def is_installed(self) -> bool:
        """Check if the binary is available on the system."""
        return shutil.which(self.binary) is not None

    def validate(self, params: dict[str, Any]) -> dict[str, Any]:
        """Validate and sanitise parameters. Override for special validation."""
        clean = {}
        allowed = {p["name"] for p in self.get_parameters()}
        for k, v in params.items():
            if k in allowed and v not in (None, "", False):
                clean[k] = v
        return clean

    def info(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "category": self.category,
            "installed": self.is_installed(),
            "enabled": self.enabled,
            "install_hint": getattr(self, "install_hint", "") or "",
            "presets": self.get_presets(),
            "parameters": self.get_parameters(),
        }
