import os
import unittest
from unittest.mock import patch

# src.schema reads these at import time.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_PATH", "service-account-key.json")
os.environ.setdefault("FLASK_ENV", "test")

from graphql import GraphQLError  # noqa: E402

from src.schema import CreateUser  # noqa: E402
from src.utils.google_auth import (
    GoogleIdentity,
    GoogleTokenVerificationError,
)  # noqa: E402

IDENTITY = GoogleIdentity(
    sub="google-user-id", email="abc123@cornell.edu", net_id="abc123"
)


@patch("src.schema.db_session")
@patch("src.schema.verify_google_identity")
class TestCreateUser(unittest.TestCase):
    def test_uses_net_id_and_email_from_verified_token(
        self, verify_identity, db_session
    ):
        verify_identity.return_value = IDENTITY
        db_session.query.return_value.filter.return_value.first.return_value = None

        user = CreateUser().mutate(None, id_token="valid-token", name="Test User")

        verify_identity.assert_called_once_with("valid-token")
        db_session.add.assert_called_once_with(user)
        self.assertEqual(user.net_id, "abc123")
        self.assertEqual(user.email, "abc123@cornell.edu")
        self.assertEqual(user.google_sub, "google-user-id")

    def test_rejects_unverified_token(self, verify_identity, db_session):
        verify_identity.side_effect = GoogleTokenVerificationError("bad token")

        with self.assertRaises(GraphQLError):
            CreateUser().mutate(None, id_token="forged-token", name="Test User")

        db_session.add.assert_not_called()

    def test_rejects_existing_account(self, verify_identity, db_session):
        verify_identity.return_value = IDENTITY
        db_session.query.return_value.filter.return_value.first.return_value = object()

        with self.assertRaises(GraphQLError):
            CreateUser().mutate(None, id_token="valid-token", name="Test User")

        db_session.add.assert_not_called()
