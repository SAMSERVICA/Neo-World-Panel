from __future__ import annotations

PROTOCOLS: list[dict] = [
    {
        "id": "vless",
        "name": "VLESS",
        "variants": "Reality · Vision · gRPC · WS",
        "desc_fa": "پروتکل مدرن و سبک ضد DPI با قابلیت شبیه‌سازی ترافیک واقعی",
        "desc_en": "Modern lightweight anti-DPI protocol",
        "icon": "vless",
        "fields": ["port", "sni", "network", "tls"],
    },
    {
        "id": "vmess",
        "name": "VMess",
        "variants": "TCP · WS · gRPC",
        "desc_fa": "پروتکل کلاسیک V2Ray با پایداری حداکثری و سازگاری بالا",
        "desc_en": "Classic V2Ray protocol",
        "icon": "vmess",
        "fields": ["port", "network", "tls", "sni"],
    },
    {
        "id": "trojan",
        "name": "Trojan",
        "variants": "TLS · WS",
        "desc_fa": "پنهان‌سازی فوق‌العاده مقاوم در برابر فیلترینگ مانند ترافیک HTTPS",
        "desc_en": "Looks like real HTTPS",
        "icon": "trojan",
        "fields": ["port", "sni", "network", "tls"],
    },
    {
        "id": "shadowsocks",
        "name": "Shadowsocks",
        "variants": "chacha20-ietf-poly1305",
        "desc_fa": "پروکسی سریع و کم‌مصرف برای انواع دستگاه‌ها و موبایل",
        "desc_en": "Fast simple proxy",
        "icon": "ss",
        "fields": ["port"],
    },
]

PROTO_IDS = [p["id"] for p in PROTOCOLS]

def is_supported(protocol: str) -> bool:
    return (protocol or "").lower() in PROTO_IDS
