import os
import unittest
from unittest.mock import patch

from src.utils.google_auth import (
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
            os.environ,
            {
                "GOOGLE_WEB_CLIENT_ID": "test-client.apps.googleusercontent.com",
                "GOOGLE_ALLOWED_HOSTED_DOMAIN": "cornell.edu",
            },
            clear=False,
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
