"""Server-side verification for Google Identity Services ID tokens."""

import os
from collections import namedtuple

from google.auth import exceptions as google_auth_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from src.utils.constants import GOOGLE_ALLOWED_HOSTED_DOMAIN


class GoogleTokenVerificationError(Exception):
    """Raised when a Google ID token cannot be trusted for this application."""


class GoogleAuthUnavailableError(Exception):
    """Raised when Google's signing certificates cannot be fetched."""


def verify_google_id_token(raw_token):
    """Return verified Google claims or raise ``GoogleTokenVerificationError``.

    The token is verified against the web client ID configured for this backend.
    The hosted-domain check is intentionally required: this app is for Cornell
    accounts, not arbitrary Google accounts.
    """
    client_id = os.environ.get("GOOGLE_WEB_CLIENT_ID")

    if not client_id:
        raise RuntimeError("GOOGLE_WEB_CLIENT_ID must be configured.")

    if not raw_token:
        raise GoogleTokenVerificationError("Missing Google ID token.")

    try:
        claims = id_token.verify_oauth2_token(raw_token, google_requests.Request(), client_id)
    except google_auth_exceptions.TransportError as error:
        raise GoogleAuthUnavailableError("Could not reach Google to verify the ID token.") from error
    except (ValueError, google_auth_exceptions.GoogleAuthError) as error:
        raise GoogleTokenVerificationError("Invalid Google ID token.") from error

    if claims.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise GoogleTokenVerificationError("Invalid Google ID token issuer.")

    if claims.get("hd") != GOOGLE_ALLOWED_HOSTED_DOMAIN:
        raise GoogleTokenVerificationError("Google account is not in the allowed domain.")

    if claims.get("email_verified") is not True:
        raise GoogleTokenVerificationError("Google account email is not verified.")

    if not claims.get("sub") or not claims.get("email"):
        raise GoogleTokenVerificationError("Google ID token is missing required claims.")

    return claims


GoogleIdentity = namedtuple("GoogleIdentity", ["sub", "email", "net_id"])


def verify_google_identity(raw_token):
    """Return the ``GoogleIdentity`` for a verified token.

    The NetID and email are derived from verified claims only, never from
    caller-supplied arguments.
    """
    claims = verify_google_id_token(raw_token)
    email = claims["email"].strip().lower()
    return GoogleIdentity(sub=claims["sub"], email=email, net_id=email.split("@", 1)[0])
