from __future__ import annotations
import json
from sqlalchemy.orm import Session
from .models import Setting

DEFAULTS: dict[str, str] = {
    "panel_name": "Neo World",
    "site_url": "",
    "default_lang": "fa",
    "timezone": "Asia/Tehran",
    "calendar": "jalali",
    "proto_defaults": "{}",
}

def get(db: Session, key: str, fallback: str = "") -> str:
    row = db.get(Setting, key)
    if row is not None and row.value != "":
        return row.value
    return DEFAULTS.get(key, fallback)

def set(db: Session, key: str, value: str) -> None:
    row = db.get(Setting, key)
    if row is None:
        row = Setting(key=key, value=value)
        db.add(row)
    else:
        row.value = value

def proto_defaults(db: Session) -> dict:
    try:
        return json.loads(get(db, "proto_defaults") or "{}")
    except Exception:
        return {}
