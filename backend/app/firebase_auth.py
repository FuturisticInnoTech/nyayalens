from __future__ import annotations

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

_app: firebase_admin.App | None = None


def _get_app() -> firebase_admin.App:
    global _app
    if _app is not None:
        return _app
    try:
        _app = firebase_admin.get_app()
    except ValueError:
        try:
            _app = firebase_admin.initialize_app(credentials.ApplicationDefault())
        except Exception as error:
            raise RuntimeError("Firebase Admin credentials are not configured") from error
    return _app


def verify_id_token(token: str) -> dict[str, object]:
    _get_app()
    return firebase_auth.verify_id_token(token)
