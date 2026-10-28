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

    def test_legacy_net_id_signup_still_works(self, verify_identity, db_session):
        db_session.query.return_value.filter.return_value.first.return_value = None

        user = CreateUser().mutate(None, name="Test User", net_id="abc123", email="abc123@cornell.edu")

        verify_identity.assert_not_called()
        db_session.add.assert_called_once_with(user)
        self.assertEqual(user.net_id, "abc123")
        self.assertEqual(user.email, "abc123@cornell.edu")
        self.assertIsNone(user.google_sub)

    def test_requires_token_or_legacy_fields(self, verify_identity, db_session):
        with self.assertRaises(GraphQLError):
            CreateUser().mutate(None, name="Test User")

        db_session.add.assert_not_called()

    def test_google_unreachable_returns_graphql_error(self, verify_identity, db_session):
        verify_identity.side_effect = GoogleAuthUnavailableError("timeout")

        with self.assertRaises(GraphQLError):
            CreateUser().mutate(None, id_token="valid-token", name="Test User")

        db_session.add.assert_not_called()
