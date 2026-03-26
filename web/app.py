#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Dict

import requests
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="Golf Meadows Web")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

if load_dotenv:
    load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))

THEMES = {"classic", "bold", "calm"}
CAROUSEL_IMAGES = [
    "/static/images/hero-1.svg",
    "/static/images/hero-2.svg",
    "/static/images/hero-3.svg",
]
DOWNLOAD_ITEMS = [
    {"name": "Society By-Laws (PDF)", "href": "#"},
    {"name": "Resident Handbook", "href": "#"},
    {"name": "Emergency Contacts Sheet", "href": "#"},
]
EVENTS = [
    {"title": "Monthly Committee Meeting", "date": "First Sunday, 10:00 AM"},
    {"title": "Community Clean-Up Drive", "date": "Second Saturday, 8:30 AM"},
    {"title": "Kids Sports Evening", "date": "Last Friday, 6:00 PM"},
]


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


def _theme_or_default(theme: str) -> str:
    return theme if theme in THEMES else "classic"


def _render(request: Request, template_name: str, context: Dict[str, Any]) -> HTMLResponse:
    payload = {"request": request, **context}
    # Starlette 1.0+ expects (request, name, context)
    # Earlier versions accepted (name, context). Keep compatibility for both.
    try:
        return templates.TemplateResponse(request, template_name, payload)
    except TypeError:
        return templates.TemplateResponse(template_name, payload)


def _infra_status_data() -> list[Dict[str, str]]:
    return [
        {"name": "Lifts", "status": os.getenv("INFRA_LIFTS_STATUS", "green"), "note": "Operational"},
        {"name": "Water Supply", "status": os.getenv("INFRA_WATER_STATUS", "green"), "note": "Normal pressure"},
        {"name": "Electricity", "status": os.getenv("INFRA_POWER_STATUS", "amber"), "note": "DG backup on standby"},
        {"name": "Security Systems", "status": os.getenv("INFRA_SECURITY_STATUS", "green"), "note": "All gates monitored"},
        {"name": "STP / Drainage", "status": os.getenv("INFRA_STP_STATUS", "red"), "note": "Maintenance in progress"},
    ]


@app.get("/", response_class=HTMLResponse)
def home(request: Request, theme: str = "classic") -> HTMLResponse:
    selected_theme = _theme_or_default(theme)
    return _render(
        request,
        "home.html",
        {
            "theme": selected_theme,
            "page": "home",
            "carousel_images": CAROUSEL_IMAGES,
        },
    )


@app.get("/downloads", response_class=HTMLResponse)
def downloads(request: Request, theme: str = "classic") -> HTMLResponse:
    return _render(
        request,
        "downloads.html",
        {
            "theme": _theme_or_default(theme),
            "page": "downloads",
            "download_items": DOWNLOAD_ITEMS,
        },
    )


@app.get("/feedback", response_class=HTMLResponse)
def feedback(request: Request, theme: str = "classic") -> HTMLResponse:
    return _render(
        request,
        "feedback.html",
        {
            "theme": _theme_or_default(theme),
            "page": "feedback",
            "message": None,
        },
    )


@app.post("/feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    theme: str = Form("classic"),
    resident_name: str = Form(...),
    unit: str = Form(...),
    feedback_text: str = Form(...),
) -> HTMLResponse:
    # Phase 1: keep feedback lightweight without persistence.
    _ = (resident_name, unit, feedback_text)
    return _render(
        request,
        "feedback.html",
        {
            "theme": _theme_or_default(theme),
            "page": "feedback",
            "message": "Thank you. Your feedback has been recorded for committee review.",
        },
    )


@app.get("/events", response_class=HTMLResponse)
def events(request: Request, theme: str = "classic") -> HTMLResponse:
    return _render(
        request,
        "events.html",
        {
            "theme": _theme_or_default(theme),
            "page": "events",
            "events": EVENTS,
        },
    )


@app.get("/infra-status", response_class=HTMLResponse)
def infra_status(request: Request, theme: str = "classic") -> HTMLResponse:
    return _render(
        request,
        "infra_status.html",
        {
            "theme": _theme_or_default(theme),
            "page": "infra-status",
            "infra_items": _infra_status_data(),
        },
    )


@app.get("/report-issue", response_class=HTMLResponse)
def report_issue(request: Request, theme: str = "classic") -> HTMLResponse:
    return _render(
        request,
        "report_issue.html",
        {
            "theme": _theme_or_default(theme),
            "page": "report-issue",
            "message": None,
            "error": None,
        },
    )


@app.post("/report-issue", response_class=HTMLResponse)
def submit_issue(
    request: Request,
    theme: str = Form("classic"),
    resident_name: str = Form(...),
    unit: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    resident_email: str = Form(""),
    resident_phone: str = Form(""),
    block: str = Form(""),
    priority: str = Form("Medium"),
    title: str = Form(""),
) -> HTMLResponse:
    selected_theme = _theme_or_default(theme)
    normalized_title = title.strip() or f"{category} issue in unit {unit}"

    try:
        payload = _build_work_order_payload(
            resident_name=resident_name,
            resident_email=resident_email,
            resident_phone=resident_phone,
            block=block,
            unit=unit,
            category=category,
            priority=priority,
            title=normalized_title,
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
        message = f"Issue submitted. Reference: {reference}"
        error = None
    except HTTPException as exc:
        message = None
        error = exc.detail
    except requests.RequestException as exc:
        message = None
        error = f"Failed to send issue to ADDA: {exc}"
    except Exception as exc:  # safety for schema mismatch during first integration
        message = None
        error = f"Unexpected integration error: {exc}"

    return _render(
        request,
        "report_issue.html",
        {
            "theme": selected_theme,
            "page": "report-issue",
            "message": message,
            "error": error,
        },
    )


@app.post("/complaints", response_class=HTMLResponse)
def submit_complaint_compat(
    request: Request,
    theme: str = Form("classic"),
    resident_name: str = Form(...),
    resident_email: str = Form(""),
    resident_phone: str = Form(""),
    block: str = Form(""),
    unit: str = Form(...),
    category: str = Form(...),
    priority: str = Form("Medium"),
    title: str = Form(""),
    description: str = Form(...),
) -> HTMLResponse:
    # Backward-compat alias for old form action.
    return submit_issue(
        request=request,
        theme=theme,
        resident_name=resident_name,
        unit=unit,
        category=category,
        description=description,
        resident_email=resident_email,
        resident_phone=resident_phone,
        block=block,
        priority=priority,
        title=title,
    )
