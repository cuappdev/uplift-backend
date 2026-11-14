"""Shared isolated fixture for tests against the production GraphQL route."""

from contextlib import ExitStack
from unittest.mock import patch

import sqlalchemy as sa
from flask_jwt_extended import create_access_token
from sqlalchemy.orm import scoped_session

from src.database import Base
from src.models.token_blacklist import TokenBlocklist
from src.tests.workout_test_db import WorkoutDatabaseTest, local


class WorkoutHTTPTest(WorkoutDatabaseTest):
    """Bind the real app route to synthetic database sessions."""

    def setUp(self):
        """Prepare an isolated database and controlled mutation dependencies."""
        super().setUp()
        import app_factory

        self.owner = self.user(local("2026-10-26"), goal=1)
        with self.engine.begin() as conn:
            for name, kind in (("name", "VARCHAR"), ("gym_id", "INTEGER"), ("facility_type", "VARCHAR")):
                conn.execute(sa.text("ALTER TABLE facility ADD COLUMN " + name + " " + kind))
            conn.execute(sa.text("INSERT INTO facility VALUES (1, 'Test gym', 1, 'fitness')"))
        TokenBlocklist.__table__.create(self.engine, checkfirst=True)
        sessions = scoped_session(self.Session)
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.addCleanup(sessions.remove)
        # Keep the real route and JWT callback; isolate external startup services.
        for target, value in (("app_factory.db_session", sessions), ("src.schema.db_session", sessions)):
            stack.enter_context(patch(target, value))
        stack.enter_context(patch.object(Base, "query", sessions.query_property()))
        with patch.multiple(
            app_factory,
            db_user="test",
            db_password="test",
            db_name="local_streak_test",
            db_host="localhost",
            db_port="5432",
        ), patch.object(app_factory, "initialize_firebase"), patch.object(app_factory, "init_db"), patch(
            "app_factory.open", create=True
        ):
            app = app_factory.create_app(run_migrations=True)
        app.config["JWT_SECRET_KEY"] = "isolated-http-test-secret-at-least-32-characters"
        with app.app_context():
            token = create_access_token(identity=str(self.owner.id))
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer " + token}

    def execute(self, query, variables=None, authenticated=True):
        """Send a GraphQL request through the real HTTP route."""
        response = self.client.post(
            "/graphql",
            json={"query": query, "variables": variables or {}},
            headers=self.headers if authenticated else {},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        return response.get_json()
