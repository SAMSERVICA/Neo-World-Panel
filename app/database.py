from __future__ import annotations
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
