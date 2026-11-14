import os
import unittest
from unittest.mock import patch

# src.schema reads these at import time.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_PATH", "service-account-key.json")
os.environ.setdefault("FLASK_ENV", "test")

from graphql import GraphQLError  # noqa: E402

from src.schema import CreateUser  # noqa: E402
from src.utils.google_auth import GoogleAuthUnavailableError, GoogleIdentity, GoogleTokenVerificationError  # noqa: E402

IDENTITY = GoogleIdentity(sub="google-user-id", email="abc123@cornell.edu", net_id="abc123")


@patch("src.schema.db_session")
@patch("src.schema.verify_google_identity")
class TestCreateUser(unittest.TestCase):
    def test_uses_net_id_and_email_from_verified_token(self, verify_identity, db_session):
        verify_identity.return_value = IDENTITY
        db_session.query.return_value.filter.return_value.first.return_value = None

        user = CreateUser().mutate(None, id_token="valid-token", name="Test User")

        verify_identity.assert_called_once_with("valid-token")
        db_session.add.assert_called_once_with(user)
        self.assertEqual(user.net_id, "abc123")
        self.assertEqual(user.email, "abc123@cornell.edu")
        self.assertEqual(user.google_sub, "google-user-id")

    def test_rejects_invalid_signup_without_writes(self, verify_identity, db_session):
        cases = (
            ({"id_token": "forged"}, GoogleTokenVerificationError("bad token"), None),
            ({"id_token": "unavailable"}, GoogleAuthUnavailableError("timeout"), None),
            ({"id_token": "valid"}, None, object()),
            ({"id_token": None}, GoogleTokenVerificationError("missing token"), None),
            ({"net_id": "abc123", "email": "abc123@cornell.edu"}, None, None),
        )
        for arguments, error, existing in cases:
            with self.subTest(arguments=arguments):
                verify_identity.reset_mock()
                db_session.reset_mock()
                verify_identity.return_value = IDENTITY
                verify_identity.side_effect = error
                db_session.query.return_value.filter.return_value.first.return_value = existing
                with self.assertRaises((GraphQLError, TypeError)):
                    CreateUser().mutate(None, name="Test User", **arguments)
                db_session.add.assert_not_called()
                db_session.commit.assert_not_called()
                if "net_id" in arguments:
                    verify_identity.assert_not_called()
