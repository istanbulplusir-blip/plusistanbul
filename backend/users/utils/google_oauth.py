from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings


def verify_google_id_token(token: str) -> dict:
    """Verify Google ID token and return payload.

    Raises google.auth.exceptions if invalid. Audience must match GOOGLE_CLIENT_ID.
    """
    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        settings.GOOGLE_CLIENT_ID,
    )


