from __future__ import annotations
import uuid
from typing import Any

def gen_uuid() -> str:
    return str(uuid.uuid4())

def gen_secret(protocol: str) -> str:
    if protocol in ("vless", "vmess"):
        return gen_uuid()
    return uuid.uuid4().hex

def inbound_for(node: Any, idx: int) -> dict[str, Any]:
    protocol = node.protocol.lower()
    tag = f"in-{idx + 1}"
    settings: dict[str, Any] = {}
    if protocol == "vless":
        settings = {"clients": [{"id": node.secret, "flow": ""}], "decryption": "none"}
    elif protocol == "vmess":
        settings = {"clients": [{"id": node.secret, "alterId": 0}]}
    elif protocol == "trojan":
        settings = {"clients": [{"password": node.secret}]}
    elif protocol == "shadowsocks":
        settings = {"method": "chacha20-ietf-poly1305", "password": node.secret, "network": "tcp,udp"}
    
    stream = {"network": node.network or "tcp", "security": "tls" if node.tls else "none"}
    return {
        "tag": tag,
        "listen": "0.0.0.0",
        "port": int(node.port),
        "protocol": protocol,
        "settings": settings,
        "streamSettings": stream
    }

def build_config(nodes: list[Any]) -> dict[str, Any]:
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [inbound_for(n, i) for i, n in enumerate(nodes) if n.enabled],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }
