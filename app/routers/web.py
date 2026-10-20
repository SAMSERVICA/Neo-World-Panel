from __future__ import annotations
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
    all_raw = "\n".join(xlinks.node_link(n) for n in nodes if xlinks.node_link(n))
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
        body = base64.b64encode("\n".join(config_links).encode()).decode()
        return Response(body, media_type="text/plain; charset=utf-8")
    
    # مرورگر -> صفحه شیک و دایره‌ای ۳۰ گیگابایت
    return templates.TemplateResponse(request, "sub.html", _ctx(
        request, db, sub=sub, links=config_links, all_raw="\n".join(config_links)
    ))

@router.get("/lang/{code}")
async def lang_switch(code: str, request: Request):
    resp = RedirectResponse(request.headers.get("referer") or "/", status_code=302)
    resp.set_cookie("lang", "fa" if code == "fa" else "en")
    return resp
