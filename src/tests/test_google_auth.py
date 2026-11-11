import os
import unittest
from unittest.mock import patch

# src.utils.constants reads these at import time.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_PATH", "service-account-key.json")

from google.auth import exceptions as google_auth_exceptions  # noqa: E402

from src.utils.google_auth import (  # noqa: E402
    GoogleAuthUnavailableError,
    GoogleTokenVerificationError,
    verify_google_id_token,
    verify_google_identity,
)

VALID_CLAIMS = {
    "sub": "google-user-id",
    "email": "test-user@cornell.edu",
    "email_verified": True,
    "hd": "cornell.edu",
    "iss": "https://accounts.google.com",
}


class TestGoogleIdTokenVerification(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(
            os.environ, {"GOOGLE_WEB_CLIENT_ID": "test-client.apps.googleusercontent.com"}, clear=False
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @patch("src.utils.google_auth.id_token.verify_oauth2_token")
    def test_accepts_verified_cornell_token(self, verify_token):
        verify_token.return_value = VALID_CLAIMS

        claims = verify_google_id_token("valid-token")

        self.assertEqual(claims, VALID_CLAIMS)
        verify_token.assert_called_once()

    @patch("src.utils.google_auth.id_token.verify_oauth2_token")
    def test_rejects_token_from_another_hosted_domain(self, verify_token):
        verify_token.return_value = {**VALID_CLAIMS, "hd": "example.com"}

        with self.assertRaises(GoogleTokenVerificationError):
            verify_google_id_token("wrong-domain-token")

    @patch("src.utils.google_auth.id_token.verify_oauth2_token")
    def test_rejects_invalid_token(self, verify_token):
        verify_token.side_effect = ValueError("bad signature")

        with self.assertRaises(GoogleTokenVerificationError):
            verify_google_id_token("forged-token")

    @patch("src.utils.google_auth.id_token.verify_oauth2_token")
    def test_identity_is_derived_from_verified_email(self, verify_token):
        verify_token.return_value = {**VALID_CLAIMS, "email": " Abc123@Cornell.edu "}

        identity = verify_google_identity("valid-token")

        self.assertEqual(identity.sub, "google-user-id")
        self.assertEqual(identity.email, "abc123@cornell.edu")
        self.assertEqual(identity.net_id, "abc123")

    @patch("src.utils.google_auth.id_token.verify_oauth2_token")
    def test_google_unreachable_raises_unavailable(self, verify_token):
        verify_token.side_effect = google_auth_exceptions.TransportError("timeout")

        with self.assertRaises(GoogleAuthUnavailableError):
            verify_google_id_token("valid-token")

    @patch("src.utils.google_auth.id_token.verify_oauth2_token")
    def test_other_google_auth_errors_are_invalid_tokens(self, verify_token):
        verify_token.side_effect = google_auth_exceptions.GoogleAuthError("bad cert")

        with self.assertRaises(GoogleTokenVerificationError):
            verify_google_id_token("forged-token")
