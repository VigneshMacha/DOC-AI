import os
import time
from typing import Optional
import httpx
from fastapi import Request
from backend.database import supabase

ACCESS_COOKIE = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")    
AUTH_RETRIES = max(0, int(os.getenv("AUTH_RETRIES", "2")))
AUTH_RETRY_DELAY = max(0.0, float(os.getenv("AUTH_RETRY_DELAY", "0.35")))


class AuthServiceUnavailable(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class EmailNotConfirmed(Exception):
    pass


def _is_email_not_confirmed(exc: Exception) -> bool:
    message = str(exc).lower()
    return "email not confirmed" in message or "email_not_confirmed" in message


def _is_network_error(exc: Exception) -> bool:
    if isinstance(exc, (httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout)):
        return True
    current = exc
    for _ in range(4):
        current = getattr(current, "__cause__", None) or getattr(current, "__context__", None)
        if current is None:
            break
        if isinstance(current, (httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout)):
            return True
    return False


def _with_retry(operation):
    last_error = None
    for attempt in range(AUTH_RETRIES + 1):
        try:
            return operation()
        except Exception as exc:
            if not _is_network_error(exc):
                raise
            last_error = exc
            if attempt >= AUTH_RETRIES:
                break
            time.sleep(AUTH_RETRY_DELAY * (2 ** attempt))
    raise AuthServiceUnavailable from last_error


def signup_user(email: str, password: str):
    email = email.strip().lower()
    return _with_retry(lambda: supabase.auth.sign_up({"email": email, "password": password}))


def login_user(email: str, password: str):
    email = email.strip().lower()
    try:
        response = _with_retry(lambda: supabase.auth.sign_in_with_password({"email": email, "password": password}))
    except AuthServiceUnavailable:
        raise
    except Exception as exc:
        if _is_email_not_confirmed(exc):
            raise EmailNotConfirmed from exc
        if "invalid login credentials" in str(exc).lower() or "invalid credentials" in str(exc).lower():
            raise InvalidCredentials from exc
        raise

    if response.session is None:
        raise InvalidCredentials
    return response


def logout_user(access_token: Optional[str] = None):
    return None


def get_current_user(request: Request):
    access_token = request.cookies.get(ACCESS_COOKIE)
    if not access_token:
        return None
    try:
        response = supabase.auth.get_user(access_token)
        return response.user
    except Exception:
        return None


def set_auth_cookie(response, access_token: str):
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=60 * 60,
        path="/",
    )


def clear_auth_cookie(response):
    response.delete_cookie(ACCESS_COOKIE, path="/")