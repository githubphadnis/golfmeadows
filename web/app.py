#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Dict

import requests
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="Golf Meadows Web")

if load_dotenv:
    load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))


def _clean_slashes(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().strip("/")


def _adda_base_url() -> str:
    env_url = os.getenv("ADDA_BASE_URL", "https://indiaapi.adda.io")
    return f"https://{_clean_slashes(env_url.replace('https://', '').replace('http://', ''))}"


def _adda_update_work_order_path() -> str:
    # Keep configurable because ADDA docs are gated and endpoint path can vary by account.
    return os.getenv("ADDA_WORK_ORDER_UPDATE_PATH", "/api/lattice/update-work-order")


def _adda_login_path() -> str:
    return os.getenv("ADDA_LOGIN_PATH", "/api/auth/login")


def _adda_token() -> str:
    static_token = os.getenv("ADDA_BEARER_TOKEN")
    if static_token:
        return static_token

    email = os.getenv("ADDA_EMAIL")
    password = os.getenv("ADDA_PASSWORD")
    if not email or not password:
        raise HTTPException(
            status_code=500,
            detail=(
                "ADDA auth is not configured. Set ADDA_BEARER_TOKEN or ADDA_EMAIL and "
                "ADDA_PASSWORD in environment."
            ),
        )

    login_url = f"{_adda_base_url()}{_adda_login_path()}"
    try:
        response = requests.post(
            login_url,
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"ADDA login failed: {exc}") from exc

    data = response.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(
            status_code=502, detail="ADDA login succeeded but no access_token was returned."
        )
    return token


def _build_work_order_payload(
    resident_name: str,
    resident_email: str,
    resident_phone: str,
    block: str,
    unit: str,
    category: str,
    priority: str,
    title: str,
    description: str,
) -> Dict[str, Any]:
    apt_id = os.getenv("ADDA_APT_ID")
    if not apt_id:
        raise HTTPException(
            status_code=500,
            detail="ADDA_APT_ID is required for work-order submission.",
        )

    # Keep payload generic and configurable-friendly; exact schema can vary per ADDA account.
    return {
        "apt_id": apt_id,
        "work_order": {
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "resident": {
                "name": resident_name,
                "email": resident_email,
                "phone": resident_phone,
                "block": block,
                "unit": unit,
            },
            "source": "golfmeadows-web",
        },
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request, theme: str = "classic") -> HTMLResponse:
    allowed = {"classic", "bold", "calm"}
    selected_theme = theme if theme in allowed else "classic"
    context = {
        "request": request,
        "theme": selected_theme,
        "message": None,
        "error": None,
    }
    # Starlette 1.0+ expects (request, name, context)
    # Earlier versions accepted (name, context). Keep compatibility for both.
    try:
        return templates.TemplateResponse(request, "index.html", context)
    except TypeError:
        return templates.TemplateResponse("index.html", context)


@app.post("/complaints", response_class=HTMLResponse)
def submit_complaint(
    request: Request,
    theme: str = Form("classic"),
    resident_name: str = Form(...),
    resident_email: str = Form(...),
    resident_phone: str = Form(...),
    block: str = Form(...),
    unit: str = Form(...),
    category: str = Form(...),
    priority: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
) -> HTMLResponse:
    allowed = {"classic", "bold", "calm"}
    selected_theme = theme if theme in allowed else "classic"

    try:
        payload = _build_work_order_payload(
            resident_name=resident_name,
            resident_email=resident_email,
            resident_phone=resident_phone,
            block=block,
            unit=unit,
            category=category,
            priority=priority,
            title=title,
            description=description,
        )

        endpoint = f"{_adda_base_url()}{_adda_update_work_order_path()}"
        token = _adda_token()
        response = requests.post(
            endpoint,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        reference = body.get("work_order_id") or body.get("id") or "Submitted"
        message = f"Complaint submitted to ADDA. Reference: {reference}"
        error = None
    except HTTPException as exc:
        message = None
        error = exc.detail
    except requests.RequestException as exc:
        message = None
        error = f"Failed to send complaint to ADDA: {exc}"
    except Exception as exc:  # safety for schema mismatch during first integration
        message = None
        error = f"Unexpected integration error: {exc}"

    context = {
        "request": request,
        "theme": selected_theme,
        "message": message,
        "error": error,
    }
    try:
        return templates.TemplateResponse(request, "index.html", context)
    except TypeError:
        return templates.TemplateResponse("index.html", context)
