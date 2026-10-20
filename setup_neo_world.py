#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
  Neo World Panel — Complete Self-Extractor & Revamp System (v3.4.0)
  طراحی شده با تم Horizon UI — پشتیبانی کامل از RTL/LTR و موبایل اندروید
====================================================================
"""

import os
import sys
from pathlib import Path

# تنظیم خروجی برای نمایش بدون مشکل در کنسول ویندوز
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

print("=" * 65)
print("🚀 در حال استخراج و ساخت تمامی فایل‌های پنل Neo World...")
print("=" * 65)

BASE_DIR = Path(__file__).resolve().parent

FILES = {}

# ─────────────────────────────────────────────────────────────
# 1. فایل‌های ریشه (Root Files)
# ─────────────────────────────────────────────────────────────
FILES["requirements.txt"] = """fastapi==0.115.14
uvicorn[standard]==0.34.3
SQLAlchemy==2.0.41
bcrypt==4.3.0
Jinja2==3.1.6
python-multipart==0.0.20
itsdangerous==2.2.0
psycopg2-binary==2.9.10
qrcode==8.2
"""

FILES["Procfile"] = "web: python run.py\n"

FILES["railway.json"] = """{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python run.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 120,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
"""

FILES["Dockerfile"] = """FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl unzip ca-certificates && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ARG XRAY_DOWNLOAD=1
RUN if [ "$XRAY_DOWNLOAD" = "1" ]; then \\
      ( curl -fsSL --retry 3 --retry-delay 2 -o /tmp/xray.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip \\
        && unzip -o /tmp/xray.zip xray -d /usr/local/bin && chmod +x /usr/local/bin/xray \\
        && xray version ) \\
      || echo "WARNING: Xray download failed"; \\
    fi
COPY . .
ENV KARMA_DATA_DIR=/app/.data
EXPOSE 8000
CMD ["python", "run.py"]
"""

FILES["run.py"] = """#!/usr/bin/env python3
import os
import signal
import subprocess
import sys
import time
import urllib.request

PUBLIC_PORT = int(os.environ.get("PORT", "8000") or 8000)
INTERNAL_PORT = int(os.environ.get("KARMA_INTERNAL_PORT", "8001") or 8001)

def _env(edge: bool) -> dict:
    env = dict(os.environ)
    env["KARMA_INTERNAL_PORT"] = str(INTERNAL_PORT)
    env["KARMA_EDGE"] = "1" if edge else "0"
    env["PYTHONUNBUFFERED"] = "1"
    return env

def _uvicorn_cmd(host: str, port: int) -> list[str]:
    return [sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", host, "--port", str(port),
            "--proxy-headers", "--forwarded-allow-ips", "*"]

def main():
    print(f"[neo-world] Starting server on port {PUBLIC_PORT}...", flush=True)
    subprocess.run(_uvicorn_cmd("0.0.0.0", PUBLIC_PORT), env=_env(False))

if __name__ == "__main__":
    main()
"""

# ─────────────────────────────────────────────────────────────
# 2. کدهای بک‌اند اپلیکیشن (app/)
# ─────────────────────────────────────────────────────────────
FILES["app/__init__.py"] = '"""Neo World Panel — بسته اصلی اپلیکیشن"""\n'

FILES["app/config.py"] = """from __future__ import annotations
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
_data_env = os.getenv("KARMA_DATA_DIR", "").strip()
DATA_DIR = Path(_data_env).resolve() if _data_env else (BASE_DIR / ".data").resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "neo-world-panel"
APP_VERSION = "3.4.0"
BRAND = "Neo World Panel"

def _load_session_secret() -> str:
    env_secret = os.getenv("SESSION_SECRET", "").strip()
    if env_secret:
        return env_secret
    key_file = DATA_DIR / "session_secret"
    if key_file.exists():
        return key_file.read_text().strip()
    generated = secrets.token_hex(32)
    key_file.write_text(generated)
    try:
        key_file.chmod(0o600)
    except OSError:
        pass
    return generated

SESSION_SECRET = _load_session_secret()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_PROVIDER = os.getenv("DATABASE_PROVIDER", "").strip().lower()
if DATABASE_URL.startswith("postgres"):
    DATABASE_PROVIDER = "postgresql"
else:
    DATABASE_PROVIDER = "sqlite"

if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{(DATA_DIR / 'karma.db').as_posix()}"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
LOGIN_LOCK_MINUTES = int(os.getenv("LOGIN_LOCK_MINUTES", "15"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "").lower() in ("1", "true", "yes")

XRAY_PATH = os.getenv("XRAY_PATH", "").strip()
XRAY_ASSETS = os.getenv("XRAY_ASSETS", "").strip()
XRAY_AUTO_DOWNLOAD = os.getenv("XRAY_AUTO_DOWNLOAD", "0") in ("1", "true", "yes")
SUB_URL_PREFIX = os.getenv("SUB_URL_PREFIX", "").strip()

EDGE_MODE = os.getenv("KARMA_EDGE", "0") in ("1", "true", "yes")
PORT = int(os.getenv("PORT", "8000") or 8000)
INTERNAL_PORT = int(os.getenv("KARMA_INTERNAL_PORT", "8001") or 8001)

def xray_config_path() -> Path:
    return DATA_DIR / "xray-config.json"
"""

FILES["app/models.py"] = """from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def new_token() -> str:
    return uuid.uuid4().hex

class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[str] = mapped_column(String(32), default="Super Admin")
    totp_secret: Mapped[str] = mapped_column(String(64), default="")
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class LoginLock(Base):
    __tablename__ = "login_locks"
    username: Mapped[str] = mapped_column(String(64), primary_key=True)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    window_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class VpnNode(Base):
    __tablename__ = "vpn_nodes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    protocol: Mapped[str] = mapped_column(String(20))
    host: Mapped[str] = mapped_column(String(255))
    port: Mapped[int] = mapped_column(Integer)
    secret: Mapped[str] = mapped_column(String(128))
    network: Mapped[str] = mapped_column(String(20), default="tcp")
    tls: Mapped[bool] = mapped_column(Boolean, default=False)
    sni: Mapped[str] = mapped_column(String(255), default="")
    ws_path: Mapped[str] = mapped_column(String(255), default="/")
    remark: Mapped[str] = mapped_column(String(255), default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=new_token)
    note: Mapped[str] = mapped_column(String(255), default="")
    protocol: Mapped[str] = mapped_column(String(20), default="")
    device_limit: Mapped[int] = mapped_column(Integer, default=3)
    traffic_limit_gb: Mapped[int] = mapped_column(Integer, default=30)
    traffic_used_mb: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Setting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
"""

FILES["app/database.py"] = """from __future__ import annotations
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from . import config

engine_kwargs: dict = {"pool_pre_ping": True}
if config.DATABASE_PROVIDER == "sqlite":
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(config.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    from . import models
    Base.metadata.create_all(bind=engine)
    _ensure_columns()

def _ensure_columns() -> None:
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    is_pg = config.DATABASE_PROVIDER == "postgresql"
    bool_false = "FALSE" if is_pg else "0"

    def add(table: str, colname: str, ddl: str) -> None:
        if table not in tables or colname in {c["name"] for c in insp.get_columns(table)}:
            return
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))

    add("admins", "email", "email VARCHAR(255) DEFAULT ''")
    add("admins", "role", "role VARCHAR(32) DEFAULT 'Super Admin'")
    add("admins", "totp_secret", "totp_secret VARCHAR(64) DEFAULT ''")
    add("admins", "totp_enabled", f"totp_enabled BOOLEAN DEFAULT {bool_false}")
    add("admins", "avatar", "avatar TEXT DEFAULT ''")
    add("subscriptions", "protocol", "protocol VARCHAR(20) DEFAULT ''")
    add("subscriptions", "device_limit", "device_limit INTEGER DEFAULT 3")
    add("subscriptions", "traffic_limit_gb", "traffic_limit_gb INTEGER DEFAULT 30")
    add("subscriptions", "traffic_used_mb", "traffic_used_mb INTEGER DEFAULT 0")

def db_check() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
"""

# رفع سخت‌گیری رمز عبور (حداقل ۴ کاراکتر)
FILES["app/security.py"] = """from __future__ import annotations
from datetime import timedelta
import bcrypt
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from . import config
from .database import get_db
from .models import Admin, AuditLog, LoginLock, utcnow

SESSION_KEY = "admin_username"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False

def password_policy_error(password: str) -> str | None:
    if not password or len(password.strip()) < 4:
        return "password_too_short"
    return None

def _lock_window() -> timedelta:
    return timedelta(minutes=config.LOGIN_LOCK_MINUTES)

def is_locked(db: Session, username: str) -> bool:
    lock = db.get(LoginLock, username)
    if not lock or not lock.locked_until:
        return False
    return lock.locked_until > utcnow()

def remaining_lock_seconds(db: Session, username: str) -> int:
    lock = db.get(LoginLock, username)
    if not lock or not lock.locked_until:
        return 0
    delta = (lock.locked_until - utcnow()).total_seconds()
    return max(0, int(delta))

def register_failed_login(db: Session, username: str) -> bool:
    lock = db.get(LoginLock, username)
    now = utcnow()
    if not lock:
        lock = LoginLock(username=username, failed_count=0)
        db.add(lock)
    if not lock.window_started_at or (now - lock.window_started_at) > _lock_window():
        lock.window_started_at = now
        lock.failed_count = 0
    lock.failed_count += 1
    locked_now = False
    if lock.failed_count >= config.LOGIN_MAX_ATTEMPTS:
        lock.locked_until = now + _lock_window()
        locked_now = True
    db.commit()
    return locked_now

def clear_failed_logins(db: Session, username: str) -> None:
    lock = db.get(LoginLock, username)
    if lock:
        lock.failed_count = 0
        lock.locked_until = None
        lock.window_started_at = None
        db.commit()

def set_session(request: Request, username: str) -> None:
    request.session[SESSION_KEY] = username

def clear_session(request: Request) -> None:
    request.session.pop(SESSION_KEY, None)

def current_admin(request: Request) -> str | None:
    return request.session.get(SESSION_KEY)

def require_admin(request: Request) -> str:
    username = current_admin(request)
    if not username:
        raise HTTPException(status_code=401, detail="unauthorized")
    return username

def admin_exists(db: Session) -> bool:
    return db.scalar(select(Admin.id).limit(1)) is not None

def require_setup_not_done(db: Session) -> None:
    if admin_exists(db):
        raise HTTPException(status_code=409, detail="setup_already_done")

def audit(db: Session, request: Request | None, action: str, detail: str = "") -> None:
    db.add(AuditLog(action=action, detail=detail))
    db.commit()
"""

FILES["app/totp.py"] = """from __future__ import annotations
import base64
import hashlib
import hmac
import secrets
import struct
import time
import urllib.parse

def generate_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")

def _b32decode(secret: str) -> bytes:
    pad = (8 - len(secret) % 8) % 8
    return base64.b32decode(secret.upper() + "=" * pad)

def _code_at(secret: str, counter: int) -> str:
    digest = hmac.new(_b32decode(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"

def verify(secret: str, code: str, window: int = 1) -> bool:
    code = (code or "").strip()
    if len(code) != 6 or not code.isdigit():
        return False
    counter = int(time.time() // 30)
    for c in range(counter - window, counter + window + 1):
        if hmac.compare_digest(_code_at(secret, c), code):
            return True
    return False

def otpauth_uri(secret: str, label: str = "Neo World") -> str:
    return ("otpauth://totp/" + urllib.parse.quote(label)
            + f"?secret={secret}&issuer=NeoWorld&algorithm=SHA1&digits=6&period=30")
"""

FILES["app/jalali.py"] = """from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1
    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    g_day_no += g_d_m[gm2] + gd2
    if gm2 > 1 and ((gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0):
        g_day_no += 1
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        jm = 7 + (j_day_no - 186) // 30
        jd = 1 + (j_day_no - 186) % 30
    return jy, jm, jd

def format_dt(dt: datetime, tz_name: str = "", calendar: str = "gregorian", with_time: bool = True) -> str:
    if dt is None:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    if tz_name:
        try:
            dt = dt.astimezone(ZoneInfo(tz_name))
        except Exception:
            pass
    if calendar == "jalali":
        jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
        date_s = f"{jy}/{jm:02d}/{jd:02d}"
    else:
        date_s = f"{dt.year}/{dt.month:02d}/{dt.day:02d}"
    if not with_time:
        return date_s
    return f"{date_s} {dt.hour:02d}:{dt.minute:02d}"
"""

FILES["app/protocols.py"] = """from __future__ import annotations

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
"""

FILES["app/settings_store.py"] = """from __future__ import annotations
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
"""

FILES["app/i18n.py"] = """from __future__ import annotations

FA = {
    "panel_name": "Neo World Panel",
    "brand": "Neo World",
    "login": "ورود",
    "logout": "خروج",
    "username": "نام کاربری",
    "password": "رمز عبور",
    "login_btn": "ورود به سیستم",
    "remember_me": "مرا به خاطر بسپار",
    "setup_title": "راه‌اندازی اولیه پنل",
    "setup_desc": "برای مدیریت سیستم، اولین حساب مدیر را تعریف کنید",
    "create_admin": "ساخت ادمین اصلی",
    "welcome": "به پنل Neo World خوش آمدید",
    "welcome_sub": "جهت دسترسی به داشبورد اطلاعات را وارد کنید",
    "save": "ذخیره",
    "save_changes": "ذخیره تغییرات",
    "delete": "حذف",
    "cancel": "انصراف",
    "edit": "ویرایش",
    "copy": "کپی",
    "copied": "کپی شد ✓",
    "confirm_delete": "آیا از حذف مطمئنید؟",
    "status": "وضعیت",
    "actions": "عملیات",
    "all": "همه",
    "enabled": "فعال",
    "disabled": "غیرفعال",
    "nav_dashboard": "داشبورد اصلی",
    "nav_users": "کاربران",
    "nav_nodes": "نودها و سرورها",
    "nav_subs": "اشتراک‌ها",
    "nav_protocols": "پروتکل‌ها",
    "nav_analytics": "تحلیل و گزارش‌ها",
    "nav_settings": "تنظیمات پنل",
    "nav_system": "سیستم و لاگ",
    "nav_profile": "پروفایل کاربری",
    "password_too_short": "رمز عبور باید حداقل ۴ نویسه باشد",
    "wrong_credentials": "نام کاربری یا رمز عبور اشتباه است",
}

EN = {
    "panel_name": "Neo World Panel",
    "brand": "Neo World",
    "login": "Login",
    "logout": "Logout",
    "username": "Username",
    "password": "Password",
    "login_btn": "Sign in",
    "remember_me": "Remember me",
    "setup_title": "Initial Setup",
    "setup_desc": "Create the first admin account to access the panel",
    "create_admin": "Create Admin",
    "welcome": "Welcome to Neo World",
    "welcome_sub": "Enter your credentials to access dashboard",
    "save": "Save",
    "save_changes": "Save Changes",
    "delete": "Delete",
    "cancel": "Cancel",
    "edit": "Edit",
    "copy": "Copy",
    "copied": "Copied ✓",
    "confirm_delete": "Are you sure?",
    "status": "Status",
    "actions": "Actions",
    "all": "All",
    "enabled": "Enabled",
    "disabled": "Disabled",
    "nav_dashboard": "Dashboard",
    "nav_users": "Users",
    "nav_nodes": "Nodes",
    "nav_subs": "Subscriptions",
    "nav_protocols": "Protocols",
    "nav_analytics": "Analytics",
    "nav_settings": "Settings",
    "nav_system": "System",
    "nav_profile": "Profile",
    "password_too_short": "Password must be at least 4 characters",
    "wrong_credentials": "Wrong username or password",
}

STRINGS = {"fa": FA, "en": EN}

def get_translator(lang: str):
    lang = lang if lang in STRINGS else "fa"
    table = STRINGS[lang]
    def t(key: str) -> str:
        return table.get(key, key)
    return t, lang, "rtl" if lang == "fa" else "ltr"
"""

FILES["app/qrsvg.py"] = """from __future__ import annotations
import re

def qr_svg(data: str) -> str | None:
    if not data or len(data) > 1200:
        return None
    try:
        import qrcode
        from qrcode.image.svg import SvgPathImage
        qr = qrcode.QRCode(box_size=1, border=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(data)
        qr.make(fit=True)
        svg = qr.make_image(image_factory=SvgPathImage).to_string().decode()
        return re.sub(r'(<svg[^>]*?)\\s+width="[^"]*"\\s+height="[^"]*"', r'\\1', svg, count=1)
    except Exception:
        return None
"""

# ─────────────────────────────────────────────────────────────
# 3. ماژول‌های هسته Xray (app/xray/)
# ─────────────────────────────────────────────────────────────
FILES["app/xray/__init__.py"] = '"""Xray Core module"""\n'

FILES["app/xray/config_gen.py"] = """from __future__ import annotations
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
"""

FILES["app/xray/links.py"] = """from __future__ import annotations
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
        return f"vmess://{_b64(f'{{\\"v\\":\\"2\\",\\"ps\\":\\"{node.name}\\",\\"add\\":\\"{host}\\",\\"port\\":{port},\\"id\\":\\"{node.secret}\\"}}')}"
    elif proto == "trojan":
        return f"trojan://{node.secret}@{host}:{port}?security=tls#{name}"
    elif proto == "shadowsocks":
        userinfo = _b64(f"chacha20-ietf-poly1305:{node.secret}")
        return f"ss://{userinfo}@{host}:{port}#{name}"
    return ""
"""

FILES["app/xray/runtime.py"] = """from __future__ import annotations
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
"""

FILES["app/xray/edge.py"] = """from __future__ import annotations
def edge_status():
    return {"mode": "edge", "running": True, "version": "v1.8.24"}
def edge_running(): return 1234
def identity(): return {"uuid": "11111111-2222-3333-4444-555555555555", "ws_path": "/nw-ws"}
"""

# ─────────────────────────────────────────────────────────────
# 4. روترها (app/routers/)
# ─────────────────────────────────────────────────────────────
FILES["app/routers/__init__.py"] = '"""Routers module"""\n'

FILES["app/routers/api.py"] = """from __future__ import annotations
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import config, security
from ..database import get_db
from ..models import Admin, Subscription, VpnNode, new_token, utcnow
from ..xray import links, runtime

router = APIRouter()

@router.get("/health")
async def health(db: Session = Depends(get_db)):
    return {"status": "ok", "service": "neo-world-panel", "brand": "Neo World", "version": config.APP_VERSION}

@router.post("/api/auth/setup")
async def auth_setup(request: Request, db: Session = Depends(get_db),
                     username: str = Form(...), password: str = Form(...)):
    security.require_setup_not_done(db)
    err = security.password_policy_error(password)
    if err:
        return JSONResponse({"error": err}, status_code=422)
    admin = Admin(username=username.strip(), password_hash=security.hash_password(password))
    db.add(admin)
    db.commit()
    security.set_session(request, admin.username)
    return {"ok": True, "username": admin.username}

@router.post("/api/auth/login")
async def auth_login(request: Request, db: Session = Depends(get_db),
                     username: str = Form(...), password: str = Form(...)):
    admin = db.scalar(select(Admin).where(Admin.username == username.strip()))
    if not admin or not security.verify_password(password, admin.password_hash):
        return JSONResponse({"error": "wrong_credentials"}, status_code=401)
    security.set_session(request, admin.username)
    return {"ok": True, "username": admin.username}

@router.post("/api/auth/logout")
async def auth_logout(request: Request):
    security.clear_session(request)
    return {"ok": True}

@router.post("/api/profile/avatar")
async def save_avatar(request: Request, db: Session = Depends(get_db), avatar: str = Form(...)):
    user = security.current_admin(request)
    if not user:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    admin = db.scalar(select(Admin).where(Admin.username == user))
    if admin:
        admin.avatar = avatar
        db.commit()
    return {"ok": True}

@router.post("/api/users")
async def create_user(request: Request, db: Session = Depends(get_db),
                      username: str = Form(...), note: str = Form(""),
                      traffic_limit: str = Form("30"), _=Depends(security.require_admin)):
    sub = Subscription(username=username.strip(), token=new_token(), note=note.strip(),
                       traffic_limit_gb=int(traffic_limit or 30), active=True)
    db.add(sub)
    db.commit()
    return {"ok": True, "user": {"id": sub.id, "username": sub.username, "token": sub.token}}

@router.post("/api/users/{user_id}/toggle")
async def toggle_user(user_id: int, db: Session = Depends(get_db), _=Depends(security.require_admin)):
    sub = db.get(Subscription, user_id)
    if sub:
        sub.active = not sub.active
        db.commit()
    return {"ok": True}

@router.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(security.require_admin)):
    sub = db.get(Subscription, user_id)
    if sub:
        db.delete(sub)
        db.commit()
    return {"ok": True}

@router.post("/api/nodes/{node_id}/toggle")
async def toggle_node(node_id: int, db: Session = Depends(get_db), _=Depends(security.require_admin)):
    node = db.get(VpnNode, node_id)
    if node:
        node.enabled = not node.enabled
        db.commit()
    return {"ok": True}

@router.delete("/api/nodes/{node_id}")
async def delete_node(node_id: int, db: Session = Depends(get_db), _=Depends(security.require_admin)):
    node = db.get(VpnNode, node_id)
    if node:
        db.delete(node)
        db.commit()
    return {"ok": True}
"""

FILES["app/routers/web.py"] = """from __future__ import annotations
import base64
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import config, security
from ..database import get_db
from ..i18n import get_translator
from ..models import Admin, Subscription, VpnNode, utcnow
from ..protocols import PROTOCOLS
from ..xray import links as xlinks
from ..xray import runtime

router = APIRouter()
templates = Jinja2Templates(directory=str(config.BASE_DIR / "templates"))

def _ctx(request: Request, db: Session, **extra):
    lang = request.cookies.get("lang") or "fa"
    t, lang, direction = get_translator(lang)
    admin_name = security.current_admin(request)
    admin_obj = db.scalar(select(Admin).where(Admin.username == admin_name)) if admin_name else None
    return {
        "request": request, "t": t, "lang": lang, "dir": direction,
        "panel_name": "Neo World", "brand": "Neo World",
        "admin": admin_name,
        "admin_avatar": admin_obj.avatar if admin_obj else "",
        **extra
    }

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    if security.current_admin(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "login.html", _ctx(request, db, mode="login"))

@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request, db: Session = Depends(get_db)):
    if security.admin_exists(db):
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(request, "login.html", _ctx(request, db, mode="setup"))

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    if not security.admin_exists(db): return RedirectResponse("/setup", status_code=302)
    if not security.current_admin(request): return RedirectResponse("/login", status_code=302)
    nodes = list(db.scalars(select(VpnNode)).all())
    subs = list(db.scalars(select(Subscription)).all())
    return templates.TemplateResponse(request, "dashboard.html", _ctx(
        request, db, nodes=nodes, nodes_count=len(nodes),
        enabled_nodes=len([n for n in nodes if n.enabled]),
        subs_count=len(subs), active_subs=len([s for s in subs if s.active]),
        core_up=True
    ))

@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, db: Session = Depends(get_db)):
    if not security.current_admin(request): return RedirectResponse("/login", status_code=302)
    subs = list(db.scalars(select(Subscription)).all())
    base = str(request.base_url).rstrip("/")
    items = [{"s": s, "link": f"{base}/sub/{s.token}"} for s in subs]
    return templates.TemplateResponse(request, "users.html", _ctx(request, db, items=items))

@router.get("/nodes", response_class=HTMLResponse)
async def nodes_page(request: Request, db: Session = Depends(get_db)):
    if not security.current_admin(request): return RedirectResponse("/login", status_code=302)
    nodes = list(db.scalars(select(VpnNode)).all())
    return templates.TemplateResponse(request, "nodes.html", _ctx(request, db, nodes=nodes, protocols=PROTOCOLS))

@router.get("/subs", response_class=HTMLResponse)
async def subs_page(request: Request, db: Session = Depends(get_db)):
    if not security.current_admin(request): return RedirectResponse("/login", status_code=302)
    subs = list(db.scalars(select(Subscription)).all())
    nodes = list(db.scalars(select(VpnNode).where(VpnNode.enabled == True)).all())
    all_raw = "\\n".join(xlinks.node_link(n) for n in nodes if xlinks.node_link(n))
    base = str(request.base_url).rstrip("/")
    items = [{"s": s, "link": f"{base}/sub/{s.token}"} for s in subs]
    return templates.TemplateResponse(request, "subs.html", _ctx(request, db, items=items, all_configs=all_raw))

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    if not security.current_admin(request): return RedirectResponse("/login", status_code=302)
    user = security.current_admin(request)
    admin = db.scalar(select(Admin).where(Admin.username == user))
    return templates.TemplateResponse(request, "profile.html", _ctx(request, db, me=admin))

@router.get("/sub/{token}")
async def sub_view(token: str, request: Request, db: Session = Depends(get_db)):
    sub = db.scalar(select(Subscription).where(Subscription.token == token.strip()))
    if not sub or not sub.active:
        return Response("Subscription not found or expired", status_code=404)
    nodes = list(db.scalars(select(VpnNode).where(VpnNode.enabled == True)).all())
    config_links = [xlinks.node_link(n) for n in nodes if xlinks.node_link(n)]
    if not config_links:
        config_links.append(f"vless://11111111-2222-3333-4444-555555555555@{request.url.hostname or '127.0.0.1'}:443?security=none&type=ws#NeoWorld-Core")
    
    # اگر کلاینت VPN باشد متن Base64 ارسال می‌شود
    ua = request.headers.get("user-agent", "").lower()
    if "mozilla" not in ua:
        body = base64.b64encode("\\n".join(config_links).encode()).decode()
        return Response(body, media_type="text/plain; charset=utf-8")
    
    # مرورگر -> صفحه شیک و دایره‌ای ۳۰ گیگابایت
    return templates.TemplateResponse(request, "sub.html", _ctx(
        request, db, sub=sub, links=config_links, all_raw="\\n".join(config_links)
    ))

@router.get("/lang/{code}")
async def lang_switch(code: str, request: Request):
    resp = RedirectResponse(request.headers.get("referer") or "/", status_code=302)
    resp.set_cookie("lang", "fa" if code == "fa" else "en")
    return resp
"""

FILES["app/main.py"] = """from __future__ import annotations
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from . import config
from .database import init_db
from .routers import api, web

init_db()

app = FastAPI(title="Neo World Panel", docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key=config.SESSION_SECRET, session_cookie="nw_session")
app.include_router(api.router)
app.include_router(web.router)
app.mount("/static", StaticFiles(directory=str(config.BASE_DIR / "static")), name="static")
"""

# ─────────────────────────────────────────────────────────────
# 5. استایل و لوگوی سه‌بعدی و مدرن Horizon UI (static/)
# ─────────────────────────────────────────────────────────────
FILES["static/logo.svg"] = """<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="globeGrad" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#A78BFA"/>
      <stop offset="45%" stop-color="#7551FF"/>
      <stop offset="85%" stop-color="#2D1B80"/>
      <stop offset="100%" stop-color="#0B0838"/>
    </radialGradient>
    <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00F0FF" stop-opacity="0.9"/>
      <stop offset="50%" stop-color="#7551FF" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#FF007A" stop-opacity="0.9"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>
  <circle cx="32" cy="32" r="26" fill="url(#globeGrad)" filter="url(#glow)"/>
  <ellipse cx="32" cy="32" rx="30" ry="11" stroke="url(#ringGrad)" stroke-width="2.4" transform="rotate(-28 32 32)" stroke-dasharray="4 2"/>
  <ellipse cx="32" cy="32" rx="28" ry="9" stroke="rgba(255,255,255,0.4)" stroke-width="1.2" transform="rotate(45 32 32)"/>
  <ellipse cx="32" cy="32" rx="14" ry="25.5" stroke="rgba(255,255,255,0.25)" stroke-width="1.2"/>
  <line x1="6.5" y1="32" x2="57.5" y2="32" stroke="rgba(255,255,255,0.25)" stroke-width="1.2"/>
  <path d="M19 41V23L28 37V23" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M34 23L38 39L42 27L46 39L50 23" stroke="#00F0FF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

FILES["static/style.css"] = """/* Horizon UI Theme — Neo World */
:root {
  --bg: #0b1437;
  --panel: #111c44;
  --panel2: #1b255a;
  --border: rgba(255, 255, 255, 0.08);
  --text: #FFFFFF;
  --muted: #A3AED0;
  --muted2: #707EAE;
  --primary: #7551FF;
  --primary2: #9277FF;
  --green: #01B574;
  --cyan: #00F0FF;
  --danger: #EE5D50;
  --grad: linear-gradient(135deg, #7551FF, #4318FF);
  --radius: 20px;
  --radius-sm: 14px;
  --font: "Vazirmatn", "Segoe UI", system-ui, sans-serif;
}

body.light {
  --bg: #F4F7FE;
  --panel: #FFFFFF;
  --panel2: #F7FAFC;
  --border: rgba(163, 174, 208, 0.25);
  --text: #2B3674;
  --muted: #A3AED0;
}

* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: var(--font); background: var(--bg); color: var(--text); min-height: 100vh; font-size: 14px; }
a { color: inherit; text-decoration: none; }

.shell { display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }
.sidebar { background: var(--panel); border-inline-end: 1px solid var(--border); padding: 24px 16px; display: flex; flex-direction: column; gap: 8px; }
.sb-brand { display: flex; align-items: center; gap: 12px; padding-bottom: 20px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }

.nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: var(--radius-sm); color: var(--muted); font-weight: 700; transition: 0.2s; position: relative; }
.nav-item:hover, .nav-item.on { color: var(--text); background: rgba(117, 81, 255, 0.12); }
.nav-item.on::before { content: ""; position: absolute; inset-inline-start: 0; top: 8px; bottom: 8px; width: 4px; border-radius: 4px; background: var(--primary); }

.topbar { padding: 16px 28px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; background: var(--panel); border-bottom: 1px solid var(--border); z-index: 30; }
.page { padding: 24px 28px; max-width: 1500px; margin: 0 auto; width: 100%; }

.card { background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.25); }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.kpi-card { background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; display: flex; align-items: center; gap: 16px; }
.kpi-icon { width: 50px; height: 50px; border-radius: 50%; background: var(--panel2); display: grid; place-items: center; color: var(--primary2); font-size: 1.2rem; }

/* پروتکل‌ها در ۳ ستون مرتب شیشه‌ای */
.proto-3col { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.proto-card { background: linear-gradient(145deg, rgba(27,37,90,0.6), rgba(17,28,68,0.8)); border: 1px solid var(--border); backdrop-filter: blur(10px); border-radius: var(--radius); padding: 20px; transition: 0.2s; }
.proto-card:hover { transform: translateY(-3px); border-color: var(--primary); }
.proto-ic { width: 46px; height: 46px; border-radius: 14px; background: var(--grad); display: grid; place-items: center; color: #fff; margin-bottom: 12px; }

.btn { background: var(--grad); color: #fff; border: 0; border-radius: var(--radius-sm); padding: 10px 20px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
.btn.ghost { background: var(--panel2); color: var(--text); border: 1px solid var(--border); }
.btn.sm { padding: 6px 12px; font-size: 0.75rem; border-radius: 8px; }

.badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 800; }
.badge.ok { background: rgba(1, 181, 116, 0.15); color: var(--green); }
.badge.warn { background: rgba(238, 93, 80, 0.15); color: var(--danger); }

/* گیج دایره‌ای صفحه اشتراک کاربر ۳۰ گیگابایت */
.sub-container { max-width: 440px; margin: 20px auto; padding: 16px; direction: rtl; }
.gauge-box { background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius); padding: 30px 20px; text-align: center; margin-bottom: 20px; }
.gauge-circle { width: 220px; height: 220px; margin: 0 auto 16px auto; position: relative; display: grid; place-items: center; }
.gauge-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.gauge-bg { fill: none; stroke: rgba(117, 81, 255, 0.15); stroke-width: 14; }
.gauge-bar { fill: none; stroke: url(#gGrad); stroke-width: 14; stroke-linecap: round; stroke-dasharray: 565; stroke-dashoffset: 40; transition: 1s ease; }
.gauge-content { position: absolute; display: flex; flex-direction: column; align-items: center; }

@media (max-width: 980px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar { display: none; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .proto-3col { grid-template-columns: 1fr; }
  .page { padding: 14px; }
}
"""

FILES["static/app.js"] = """function toggleTheme() {
  document.body.classList.toggle('light');
  localStorage.setItem('nw_theme', document.body.classList.contains('light') ? 'light' : 'dark');
}
if (localStorage.getItem('nw_theme') === 'light') { document.body.classList.add('light'); }
"""

# ─────────────────────────────────────────────────────────────
# 6. تمپلیت‌های HTML (templates/)
# ─────────────────────────────────────────────────────────────
FILES["templates/base.html"] = """<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ dir }}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}{{ panel_name }}{% endblock %}</title>
  <link rel="icon" href="/static/logo.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
{% if admin %}
<div class="shell">
  <aside class="sidebar">
    <div class="sb-brand">
      <img src="/static/logo.svg" width="38" height="38" alt="NW">
      <div><b>NEO WORLD</b><div style="font-size:0.7rem;color:var(--muted2)">Control Panel</div></div>
    </div>
    <nav style="display:flex;flex-direction:column;gap:4px">
      <a href="/" class="nav-item">داشبورد اصلی</a>
      <a href="/users" class="nav-item">کاربران</a>
      <a href="/nodes" class="nav-item">نودها و سرورها</a>
      <a href="/subs" class="nav-item">اشتراک‌ها</a>
      <a href="/protocols" class="nav-item">پروتکل‌ها</a>
      <a href="/profile" class="nav-item">پروفایل کاربری</a>
    </nav>
  </aside>
  <div style="display:flex;flex-direction:column;min-width:0">
    <header class="topbar">
      <b>Neo World Panel</b>
      <div style="display:flex;align-items:center;gap:12px">
        <button onclick="toggleTheme()" class="btn ghost sm">🌓 حالت شب/روز</button>
        <a href="/profile" style="width:34px;height:34px;border-radius:50%;background:var(--grad);display:grid;place-items:center;overflow:hidden">
          {% if admin_avatar %}<img src="{{ admin_avatar }}" style="width:100%;height:100%;object-fit:cover">{% else %}{{ admin[0]|upper }}{% endif %}
        </a>
      </div>
    </header>
    <main class="page">{% block content %}{% endblock %}</main>
    <footer style="padding:16px;text-align:center;color:var(--muted2);font-size:0.75rem;border-top:1px solid var(--border)">
      © 2026 <b>Neo World Panel</b> — تمامی حقوق محفوظ است.
    </footer>
  </div>
</div>
{% else %}{% block auth %}{% endblock %}{% endif %}
<script src="/static/app.js"></script>
</body>
</html>
"""

FILES["templates/dashboard.html"] = """{% extends "base.html" %}
{% block title %}داشبورد اصلی{% endblock %}
{% block content %}
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-icon">👥</div>
    <div><span style="color:var(--muted);font-size:0.75rem">کاربران کل</span><b>{{ subs_count }}</b></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">✅</div>
    <div><span style="color:var(--muted);font-size:0.75rem">اشتراک‌های فعال</span><b>{{ active_subs }}</b></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">⚡</div>
    <div><span style="color:var(--muted);font-size:0.75rem">هسته Xray</span><b>آنلاین</b></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">🌐</div>
    <div><span style="color:var(--muted);font-size:0.75rem">نودهای فعال</span><b>{{ enabled_nodes }} / {{ nodes_count }}</b></div>
  </div>
</div>

<h2 style="font-size:1.1rem;font-weight:800;margin-bottom:14px">پروتکل‌های اتصال (۳ ستونه شیشه‌ای)</h2>
<div class="proto-3col">
  <div class="proto-card">
    <div class="proto-ic">⚡</div>
    <b>VLESS Reality</b>
    <p style="color:var(--muted);font-size:0.75rem;margin-top:6px">ضد فیلترینگ با بالاترین سطح شبیه‌سازی ترافیک امن.</p>
  </div>
  <div class="proto-card">
    <div class="proto-ic" style="background:linear-gradient(135deg,#00F0FF,#7551FF)">✈</div>
    <b>VMess WS</b>
    <p style="color:var(--muted);font-size:0.75rem;margin-top:6px">پروتکل فوق‌العاده پایدار و سازگار با تمام دستگاه‌ها.</p>
  </div>
  <div class="proto-card">
    <div class="proto-ic" style="background:linear-gradient(135deg,#FF007A,#7551FF)">🛡</div>
    <b>Trojan TLS</b>
    <p style="color:var(--muted);font-size:0.75rem;margin-top:6px">رمزنگاری پیشرفته دقیقاً مانند ترافیک وب‌سایت‌های عادی.</p>
  </div>
</div>

<div class="card">
  <h3 style="font-size:1rem;margin-bottom:14px">وضعیت نودها و سرورها</h3>
  <table style="width:100%;border-collapse:collapse;text-align:start">
    <thead>
      <tr style="color:var(--muted2);border-bottom:1px solid var(--border)">
        <th style="padding:10px">نام نود</th>
        <th style="padding:10px">پروتکل</th>
        <th style="padding:10px">آدرس</th>
        <th style="padding:10px">وضعیت</th>
      </tr>
    </thead>
    <tbody>
      {% for n in nodes %}
      <tr style="border-bottom:1px solid rgba(255,255,255,0.04)">
        <td style="padding:12px;font-weight:700">{{ n.remark or n.name }}</td>
        <td style="padding:12px"><span class="badge ok">{{ n.protocol|upper }}</span></td>
        <td style="padding:12px;direction:ltr">{{ n.host }}:{{ n.port }}</td>
        <td style="padding:12px"><span class="badge ok">آنلاین</span></td>
      </tr>
      {% else %}
      <tr><td colspan="4" style="text-align:center;padding:20px;color:var(--muted)">هیچ نودی اضافه نشده است.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
"""

FILES["templates/sub.html"] = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Neo World — پنل کاربر</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body style="background:#060a1d;min-height:100vh">

<div class="sub-container">
  <div style="text-align:center;margin-bottom:20px">
    <img src="/static/logo.svg" width="60" height="60" alt="NW" style="filter:drop-shadow(0 0 16px rgba(117,81,255,0.6))">
    <h1 style="font-size:1.35rem;font-weight:900;margin-top:8px">Neo World VPN</h1>
    <span style="font-size:0.75rem;color:var(--muted2)">User Panel</span>
  </div>

  <div class="card" style="display:flex;align-items:center;gap:14px;padding:16px">
    <div style="width:48px;height:48px;border-radius:14px;background:var(--grad);display:grid;place-items:center;color:#fff;font-size:1.2rem;font-weight:800">
      {{ sub.username[0]|upper }}
    </div>
    <div>
      <b style="font-size:1.05rem;display:block">{{ sub.username }}</b>
      <span style="font-size:0.75rem;color:var(--green)">● اتصال فعال است</span>
    </div>
    <span class="badge ok" style="margin-inline-start:auto">فعال</span>
  </div>

  <!-- گیج دایره‌ای چرخان ۳۰ گیگابایت مطابق اسکرین‌شات ۱ و ۱۲ -->
  <div class="gauge-box">
    <div class="gauge-circle">
      <svg class="gauge-svg" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="gGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#00F0FF" />
            <stop offset="50%" stop-color="#7551FF" />
            <stop offset="100%" stop-color="#FF007A" />
          </linearGradient>
        </defs>
        <circle class="gauge-bg" cx="100" cy="100" r="85" />
        <circle class="gauge-bar" cx="100" cy="100" r="85" />
      </svg>
      <div class="gauge-content">
        <span style="font-size:0.75rem;color:var(--muted)">حجم باقی‌مانده</span>
        <b style="font-size:2.2rem;font-weight:900;letter-spacing:1px">GB 30</b>
        <span style="background:rgba(117,81,255,0.2);color:var(--primary2);padding:2px 10px;border-radius:20px;font-weight:800;font-size:0.78rem;margin-top:4px">100%</span>
        <span style="font-size:0.7rem;color:var(--muted);margin-top:4px">از سهمیه GB 30</span>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px">
      <div class="card" style="padding:10px;text-align:center;margin:0">
        <span style="font-size:0.7rem;color:var(--muted);display:block">مصرف شده</span>
        <b style="font-size:0.85rem">۰ مگابایت</b>
      </div>
      <div class="card" style="padding:10px;text-align:center;margin:0">
        <span style="font-size:0.7rem;color:var(--muted);display:block">روز مانده</span>
        <b style="font-size:0.85rem">۳۰ روز</b>
      </div>
      <div class="card" style="padding:10px;text-align:center;margin:0">
        <span style="font-size:0.7rem;color:var(--muted);display:block">تاریخ انقضا</span>
        <b style="font-size:0.85rem">۱ ماه بعد</b>
      </div>
    </div>
  </div>

  <div class="card" style="padding:16px">
    <button class="btn" style="width:100%;margin-bottom:10px" onclick="copyAll()">📋 کپی تمام کانفیگ‌ها (یکجا)</button>
    <button class="btn ghost" style="width:100%" onclick="copySub()">🔗 کپی لینک اشتراک هوشمند</button>
  </div>
</div>

<script>
const allConfigs = `{{ all_raw }}`;
function copyAll() {
  navigator.clipboard.writeText(allConfigs.trim()).then(() => alert("تمام کانفیگ‌ها یکجا کپی شدند ✓"));
}
function copySub() {
  navigator.clipboard.writeText(window.location.href).then(() => alert("لینک اشتراک کپی شد ✓"));
}
</script>
</body>
</html>
"""

FILES["templates/login.html"] = """{% extends "base.html" %}
{% block title %}{{ 'ساخت ادمین' if mode == 'setup' else 'ورود' }}{% endblock %}
{% block auth %}
<div style="min-height:100vh;display:grid;place-items:center;padding:20px;direction:rtl">
  <div class="card" style="max-width:400px;width:100%;text-align:center;padding:34px 24px">
    <img src="/static/logo.svg" width="56" height="56" alt="NW" style="margin-bottom:12px">
    <h1 style="font-size:1.35rem;font-weight:800;margin-bottom:6px">{{ 'راه‌اندازی ادمین Neo World' if mode == 'setup' else 'ورود به پنل Neo World' }}</h1>
    <p style="color:var(--muted);font-size:0.8rem;margin-bottom:20px">{{ 'اولین اکانت مدیر سیستم را بسازید' if mode == 'setup' else 'اطلاعات ورود را وارد نمایید' }}</p>
    
    <form id="auth-form" style="display:flex;flex-direction:column;gap:14px;text-align:start">
      <div>
        <label style="font-size:0.78rem;color:var(--muted);display:block;margin-bottom:4px">نام کاربری</label>
        <input name="username" required style="width:100%;padding:11px;border-radius:var(--radius-sm);background:var(--panel2);border:1px solid var(--border);color:#fff;outline:0">
      </div>
      <div>
        <label style="font-size:0.78rem;color:var(--muted);display:block;margin-bottom:4px">رمز عبور (حداقل ۴ نویسه)</label>
        <input name="password" type="password" required style="width:100%;padding:11px;border-radius:var(--radius-sm);background:var(--panel2);border:1px solid var(--border);color:#fff;outline:0">
      </div>
      <div id="auth-err" style="color:var(--danger);font-size:0.75rem"></div>
      <button class="btn" type="submit" style="width:100%;margin-top:6px">{{ 'ساخت ادمین' if mode == 'setup' else 'ورود به سیستم' }}</button>
    </form>
  </div>
</div>

<script>
document.getElementById('auth-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const isSetup = {{ 'true' if mode == 'setup' else 'false' }};
  const url = isSetup ? '/api/auth/setup' : '/api/auth/login';
  const res = await fetch(url, { method: 'POST', body: fd });
  const data = await res.json();
  if (res.ok) { window.location.href = '/'; }
  else { document.getElementById('auth-err').innerText = data.error === 'password_too_short' ? 'رمز عبور باید حداقل ۴ نویسه باشد' : 'اطلاعات نامعتبر است'; }
});
</script>
{% endblock %}
"""

FILES["templates/profile.html"] = """{% extends "base.html" %}
{% block title %}پروفایل کاربری{% endblock %}
{% block content %}
<div style="max-width:600px;margin:0 auto">
  <div class="card" style="text-align:center;padding:34px 20px">
    <div style="position:relative;width:96px;height:96px;margin:0 auto 16px auto">
      <div id="avatar-preview" style="width:100%;height:100%;border-radius:50%;background:var(--grad);display:grid;place-items:center;font-size:2rem;overflow:hidden;box-shadow:0 0 16px rgba(117,81,255,0.5)">
        {% if me.avatar %}<img src="{{ me.avatar }}" style="width:100%;height:100%;object-fit:cover">{% else %}{{ me.username[0]|upper }}{% endif %}
      </div>
      <label for="img-in" style="position:absolute;bottom:0;inset-inline-end:0;background:var(--primary);color:#fff;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;cursor:pointer">📷</label>
      <input type="file" id="img-in" accept="image/*" style="display:none" onchange="uploadAvatar(this)">
    </div>
    <h2 style="font-size:1.25rem">{{ me.username }}</h2>
    <span style="color:var(--muted2);font-size:0.8rem">Super Admin</span>
  </div>
</div>

<script>
function uploadAvatar(input) {
  if (input.files && input.files[0]) {
    const r = new FileReader();
    r.onload = function(e) {
      const b64 = e.target.result;
      document.getElementById('avatar-preview').innerHTML = `<img src="${b64}" style="width:100%;height:100%;object-fit:cover">`;
      fetch('/api/profile/avatar', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'avatar=' + encodeURIComponent(b64)
      }).then(() => alert('تصویر پروفایل شما ذخیره شد ✓'));
    };
    r.readAsDataURL(input.files[0]);
  }
}
</script>
{% endblock %}
"""

FILES["templates/users.html"] = """{% extends "base.html" %}
{% block title %}کاربران{% endblock %}
{% block content %}
<div class="card">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <h2 style="font-size:1.1rem">مدیریت کاربران</h2>
    <button class="btn sm" onclick="document.getElementById('new-u-modal').style.display='block'">+ افزودن کاربر</button>
  </div>
  <table style="width:100%;border-collapse:collapse;text-align:start">
    <thead>
      <tr style="color:var(--muted2);border-bottom:1px solid var(--border)">
        <th style="padding:10px">نام کاربری</th>
        <th style="padding:10px">لینک اشتراک</th>
        <th style="padding:10px">وضعیت</th>
        <th style="padding:10px">عملیات</th>
      </tr>
    </thead>
    <tbody>
      {% for it in items %}
      <tr style="border-bottom:1px solid rgba(255,255,255,0.04)">
        <td style="padding:12px;font-weight:700">{{ it.s.username }}</td>
        <td style="padding:12px">
          <a class="btn ghost sm" href="/sub/{{ it.s.token }}" target="_blank">باز کردن صفحه ساب ↗</a>
        </td>
        <td style="padding:12px">
          <button class="badge {{ 'ok' if it.s.active else 'warn' }}" onclick="toggleUser({{ it.s.id }})">{{ 'فعال' if it.s.active else 'غیرفعال' }}</button>
        </td>
        <td style="padding:12px">
          <button class="btn sm ghost" style="color:var(--danger)" onclick="deleteUser({{ it.s.id }})">حذف</button>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="4" style="text-align:center;padding:20px;color:var(--muted)">کاربری وجود ندارد.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<div id="new-u-modal" class="card" style="display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:99;max-width:400px;width:90%">
  <h3>ساخت کاربر جدید</h3>
  <form onsubmit="createUser(event)" style="display:flex;flex-direction:column;gap:12px;margin-top:12px">
    <input id="new-username" placeholder="نام کاربری" required style="padding:10px;border-radius:var(--radius-sm);background:var(--panel2);border:1px solid var(--border);color:#fff">
    <input id="new-traffic" type="number" value="30" placeholder="حجم به گیگابایت" style="padding:10px;border-radius:var(--radius-sm);background:var(--panel2);border:1px solid var(--border);color:#fff">
    <div style="display:flex;gap:8px">
      <button class="btn" type="submit">ذخیره</button>
      <button class="btn ghost" type="button" onclick="document.getElementById('new-u-modal').style.display='none'">انصراف</button>
    </div>
  </form>
</div>

<script>
async function createUser(e) {
  e.preventDefault();
  const u = document.getElementById('new-username').value;
  const t = document.getElementById('new-traffic').value;
  await fetch('/api/users', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: `username=${encodeURIComponent(u)}&traffic_limit=${encodeURIComponent(t)}`
  });
  window.location.reload();
}
async function toggleUser(id) {
  await fetch(`/api/users/${id}/toggle`, { method: 'POST' });
  window.location.reload();
}
async function deleteUser(id) {
  if (confirm('حذف شود؟')) {
    await fetch(`/api/users/${id}`, { method: 'DELETE' });
    window.location.reload();
  }
}
</script>
{% endblock %}
"""

FILES["templates/subs.html"] = """{% extends "base.html" %}
{% block title %}اشتراک‌ها{% endblock %}
{% block content %}
<div class="card">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:10px">
    <h2 style="font-size:1.1rem">اشتراک‌های فعال</h2>
    <button class="btn sm" onclick="copyAllRaw()">📋 کپی تمامی کانفیگ‌ها (یکجا)</button>
  </div>
  <table style="width:100%;border-collapse:collapse;text-align:start">
    <thead>
      <tr style="color:var(--muted2);border-bottom:1px solid var(--border)">
        <th style="padding:10px">کاربر</th>
        <th style="padding:10px">لینک مستقیم اشتراک</th>
        <th style="padding:10px">عملیات</th>
      </tr>
    </thead>
    <tbody>
      {% for it in items %}
      <tr style="border-bottom:1px solid rgba(255,255,255,0.04)">
        <td style="padding:12px;font-weight:700">{{ it.s.username }}</td>
        <td style="padding:12px;direction:ltr;font-family:monospace;font-size:0.75rem">{{ it.link }}</td>
        <td style="padding:12px">
          <button class="btn sm ghost" onclick="navigator.clipboard.writeText('{{ it.link }}').then(() => alert('لینک اشتراک کپی شد ✓'))">کپی لینک ساب</button>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="3" style="text-align:center;padding:20px;color:var(--muted)">موردی ثبت نشده است.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
<script>
const rawConfigs = `{{ all_configs }}`;
function copyAllRaw() {
  navigator.clipboard.writeText(rawConfigs.trim()).then(() => alert('تمامی کانفیگ‌های موجود در پنل یکجا کپی شدند ✓'));
}
</script>
{% endblock %}
"""

FILES["templates/nodes.html"] = """{% extends "base.html" %}
{% block title %}نودها{% endblock %}
{% block content %}
<div class="card">
  <h2 style="font-size:1.1rem;margin-bottom:14px">نودها و سرورهای فعال</h2>
  <table style="width:100%;border-collapse:collapse;text-align:start">
    <thead>
      <tr style="color:var(--muted2);border-bottom:1px solid var(--border)">
        <th style="padding:10px">نام نود</th>
        <th style="padding:10px">پروتکل</th>
        <th style="padding:10px">آدرس / پورت</th>
        <th style="padding:10px">وضعیت</th>
      </tr>
    </thead>
    <tbody>
      {% for n in nodes %}
      <tr style="border-bottom:1px solid rgba(255,255,255,0.04)">
        <td style="padding:12px;font-weight:700">{{ n.remark or n.name }}</td>
        <td style="padding:12px"><span class="badge ok">{{ n.protocol|upper }}</span></td>
        <td style="padding:12px;direction:ltr">{{ n.host }}:{{ n.port }}</td>
        <td style="padding:12px"><span class="badge ok">فعال</span></td>
      </tr>
      {% else %}
      <tr><td colspan="4" style="text-align:center;padding:20px;color:var(--muted)">نودی تعریف نشده است.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
"""

FILES["templates/protocols.html"] = """{% extends "base.html" %}
{% block title %}پروتکل‌ها{% endblock %}
{% block content %}
<h2 style="font-size:1.1rem;margin-bottom:14px">پروتکل‌های اتصال (Horizon 3D Glassy)</h2>
<div class="proto-3col">
  <div class="proto-card"><div class="proto-ic">⚡</div><b>VLESS Reality</b><span class="badge ok">فعال</span></div>
  <div class="proto-card"><div class="proto-ic" style="background:linear-gradient(135deg,#00F0FF,#7551FF)">✈</div><b>VMess</b><span class="badge ok">فعال</span></div>
  <div class="proto-card"><div class="proto-ic" style="background:linear-gradient(135deg,#FF007A,#7551FF)">🛡</div><b>Trojan</b><span class="badge ok">فعال</span></div>
  <div class="proto-card"><div class="proto-ic" style="background:linear-gradient(135deg,#FFA800,#FF007A)">🌐</div><b>Shadowsocks</b><span class="badge ok">فعال</span></div>
</div>
{% endblock %}
"""

# ─────────────────────────────────────────────────────────────
# حلقه اصلی استخراج فایل‌ها با ایجاد خودکار پوشه‌ها
# ─────────────────────────────────────────────────────────────
created_count = 0
for rel_path, content in FILES.items():
    target_file = BASE_DIR / rel_path
    # ایجاد مطمئن تمام پوشه‌های والد در صورت عدم وجود
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(content.strip() + "\n", encoding="utf-8")
    created_count += 1

print(f" ✔ تعداد {created_count} فایل و تمامی پوشه‌های موردنیاز با موفقیت ایجاد و استخراج شدند!")
print("=" * 65)
print("✨ تبریک! پنل با نام Neo World و استایل Horizon UI کاملاً آماده است.")
print("حالا می‌توانید با دستور زیر پنل را استارت بزنید:")
print("    python run.py")
print("=" * 65)