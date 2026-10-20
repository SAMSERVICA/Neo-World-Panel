from __future__ import annotations
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
