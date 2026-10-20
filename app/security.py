from __future__ import annotations
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
