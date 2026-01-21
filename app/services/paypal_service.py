from __future__ import annotations

import base64
import requests
from typing import Any, Dict, Optional

from app.core.config import settings

def _base_url() -> str:
    return "https://api-m.sandbox.paypal.com" if settings.PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

def get_access_token() -> str:
    url = f"{_base_url()}/v1/oauth2/token"
    auth = base64.b64encode(f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    r = requests.post(url, headers=headers, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def create_order(*, amount: str, currency: str = "USD", reference_id: str) -> Dict[str, Any]:
    token = get_access_token()
    url = f"{_base_url()}/v2/checkout/orders"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": reference_id,
                "amount": {"currency_code": currency, "value": amount},
            }
        ],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def capture_order(order_id: str) -> Dict[str, Any]:
    token = get_access_token()
    url = f"{_base_url()}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, json={}, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_approve_url(order_json: Dict[str, Any]) -> Optional[str]:
    for link in order_json.get("links", []):
        if link.get("rel") == "approve":
            return link.get("href")
    return None

def extract_capture_id(capture_json: Dict[str, Any]) -> Optional[str]:
    # capture_json.purchase_units[0].payments.captures[0].id
    pus = capture_json.get("purchase_units", [])
    if not pus:
        return None
    payments = pus[0].get("payments", {})
    captures = payments.get("captures", [])
    if not captures:
        return None
    return captures[0].get("id")
