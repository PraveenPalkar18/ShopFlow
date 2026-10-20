import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

from app.config import settings


def hash_password(password: str) -> str:
    salt = urlsafe_b64encode(__import__("secrets").token_bytes(16)).decode()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180_000)
    return f"{salt}${urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
        actual = urlsafe_b64encode(
            hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180_000)
        ).decode()
        return hmac.compare_digest(actual, expected)
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    payload = urlsafe_b64encode(
        json.dumps({"sub": user_id, "exp": int(time.time()) + 3600}).encode()
    ).decode().rstrip("=")
    signature = hmac.new(settings.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def read_access_token(token: str) -> int | None:
    try:
        payload, signature = token.split(".", 1)
        expected = hmac.new(
            settings.secret_key.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        decoded = urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        data = json.loads(decoded)
        if int(data["exp"]) < int(time.time()):
            return None
        return int(data["sub"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None
