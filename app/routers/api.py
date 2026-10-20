from __future__ import annotations
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
