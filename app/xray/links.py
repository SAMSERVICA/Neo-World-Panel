from __future__ import annotations
import base64
import urllib.parse
from typing import Any

def _b64(data: str) -> str:
    return base64.b64encode(data.encode("utf-8")).decode("ascii")

def node_link(node: Any) -> str:
    proto = node.protocol.lower()
    name = urllib.parse.quote((node.remark or node.name).strip())
    host = node.host.strip()
    port = int(node.port)
    if proto == "vless":
        return f"vless://{node.secret}@{host}:{port}?security={'tls' if node.tls else 'none'}&type={node.network or 'tcp'}#{name}"
    elif proto == "vmess":
        return f"vmess://{_b64(f'{{\"v\":\"2\",\"ps\":\"{node.name}\",\"add\":\"{host}\",\"port\":{port},\"id\":\"{node.secret}\"}}')}"
    elif proto == "trojan":
        return f"trojan://{node.secret}@{host}:{port}?security=tls#{name}"
    elif proto == "shadowsocks":
        userinfo = _b64(f"chacha20-ietf-poly1305:{node.secret}")
        return f"ss://{userinfo}@{host}:{port}#{name}"
    return ""
