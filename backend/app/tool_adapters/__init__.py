"""Tool adapter registry – single import point for all adapters."""

from .nmap import NmapAdapter
from .gobuster import GobusterAdapter
from .hydra import HydraAdapter
from .wpscan import WpscanAdapter
from .nikto import NiktoAdapter
from .sqlmap import SqlmapAdapter
from .subfinder import SubfinderAdapter
from .katana import KatanaAdapter
from .wpprobe import WpprobeAdapter
from .ffuf import FfufAdapter
from .nuclei import NucleiAdapter
from .amass import AmassAdapter
from .trufflehog import TrufflehogAdapter
from .testssl import TestsslAdapter
from .arjun import ArjunAdapter

ADAPTERS = {
    "nmap": NmapAdapter(),
    "gobuster": GobusterAdapter(),
    "hydra": HydraAdapter(),
    "wpscan": WpscanAdapter(),
    "nikto": NiktoAdapter(),
    "sqlmap": SqlmapAdapter(),
    "subfinder": SubfinderAdapter(),
    "katana": KatanaAdapter(),
    "wpprobe": WpprobeAdapter(),
    "ffuf": FfufAdapter(),
    "nuclei": NucleiAdapter(),
    "amass": AmassAdapter(),
    "trufflehog": TrufflehogAdapter(),
    "testssl": TestsslAdapter(),
    "arjun": ArjunAdapter(),
}


def get_adapter(name: str):
    """Get a tool adapter by name."""
    return ADAPTERS.get(name)


def get_all_adapters():
    """Return all registered adapters."""
    return ADAPTERS
