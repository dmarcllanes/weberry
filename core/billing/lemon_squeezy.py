import hmac
import hashlib
import json
import urllib.request
import urllib.error
from config.settings import (
    LEMON_SQUEEZY_API_KEY,
    LEMON_SQUEEZY_WEBHOOK_SECRET,
    LEMON_SQUEEZY_STORE_ID,
    LEMON_SQUEEZY_VARIANTS,
    APP_HOST,
    APP_PORT,
)

API_BASE = "https://api.lemonsqueezy.com/v1"

def create_checkout_url(user_email: str, plan_type: str, redirect_url: str | None = None) -> str:
    """
    Create a checkout URL for a specific plan variant.
    """
    variant_id = LEMON_SQUEEZY_VARIANTS.get(plan_type)
    if not variant_id:
        raise ValueError(f"No variant ID found for plan: {plan_type}")

    # Default redirect back to billing page if not specified
    if not redirect_url:
        protocol = "https" if "localhost" not in APP_HOST else "http"
        host = f"{APP_HOST}:{APP_PORT}" if APP_PORT else APP_HOST
        redirect_url = f"{protocol}://{host}/billing"

    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "checkout_data": {
                    "email": user_email,
                    "custom": {
                        "user_email": user_email 
                    }
                },
                "product_options": {
                    "redirect_url": redirect_url,
                }
            },
            "relationships": {
                "store": {
                    "data": {
                        "type": "stores",
                        "id": str(LEMON_SQUEEZY_STORE_ID)
                    }
                },
                "variant": {
                    "data": {
                        "type": "variants",
                        "id": str(variant_id)
                    }
                }
            }
        }
    }

    headers = {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {LEMON_SQUEEZY_API_KEY}",
    }

    req = urllib.request.Request(
        f"{API_BASE}/checkouts",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            if response.status not in (200, 201):
                raise Exception(f"Lemon Squeezy API Error: {response.status} {response.read().decode('utf-8')}")
            
            response_body = response.read().decode("utf-8")
            data = json.loads(response_body)
            return data["data"]["attributes"]["url"]
    except urllib.error.HTTPError as e:
         raise Exception(f"Lemon Squeezy API Error: {e.code} {e.read().decode('utf-8')}")


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify the X-Signature header from Lemon Squeezy.
    """
    if not signature or not LEMON_SQUEEZY_WEBHOOK_SECRET:
        return False

    digest = hmac.new(
        LEMON_SQUEEZY_WEBHOOK_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(digest, signature)
