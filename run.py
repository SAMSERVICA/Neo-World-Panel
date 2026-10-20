#!/usr/bin/env python3
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
