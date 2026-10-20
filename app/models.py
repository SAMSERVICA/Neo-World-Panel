from __future__ import annotations
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
