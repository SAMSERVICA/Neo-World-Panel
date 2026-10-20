from __future__ import annotations
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
