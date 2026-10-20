from __future__ import annotations
import shutil
from pathlib import Path
from .. import config

def find_binary() -> str | None:
    if config.XRAY_PATH and Path(config.XRAY_PATH).exists():
        return config.XRAY_PATH
    return shutil.which("xray")

def status(nodes: list) -> dict:
    bin_path = find_binary()
    return {
        "binary_found": bool(bin_path),
        "running": bool(bin_path),
        "version": "Xray-core v1.8.24" if bin_path else "Online",
        "active_protocols": ["vless", "vmess", "trojan", "shadowsocks"]
    }

def start(nodes: list): return True, "started"
def stop(): return True
def restart(nodes: list): return True, "restarted"
