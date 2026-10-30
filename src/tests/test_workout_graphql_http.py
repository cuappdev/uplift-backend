"""Exercise the production GraphQL route using isolated DB sessions and real JWTs."""
from datetime import datetime, timezone
from unittest.mock import patch

import sqlalchemy as sa
from sqlalchemy.orm import scoped_session
from flask_jwt_extended import create_access_token

from src.tests.workout_test_db import WorkoutDatabaseTest
from src.tests.test_workout_streaks import local
from src.database import Base
from src.models.user import User
from src.models.workout import Workout
from src.models.user_workout_goal_history import UserWorkoutGoalHistory
from src.models.user_workout_week import UserWorkoutWeek
from src.models.token_blacklist import TokenBlocklist
from src.utils.workout_streaks import run_weekly_rollover, current_week, as_utc


class WorkoutGraphQLHTTPTests(WorkoutDatabaseTest):
    def test_authenticated_http_workout_flow_and_rollover(self):
        import app_factory
        owner = self.user(local('2026-10-26'), goal=1)
        other = self.user(local('2026-10-26'), goal=3, streak=8)
        owner_id, other_id = owner.id, other.id
        owner.net_id, other.net_id = 'http-owner', 'http-other'
        self.session.commit()
        with self.engine.begin() as conn:
            conn.execute(sa.text('ALTER TABLE facility ADD COLUMN name VARCHAR'))
            conn.execute(sa.text('ALTER TABLE facility ADD COLUMN gym_id INTEGER'))
            conn.execute(sa.text('ALTER TABLE facility ADD COLUMN facility_type VARCHAR'))
            conn.execute(sa.text("INSERT INTO facility VALUES (1, 'Test gym', 1, 'fitness')"))
        TokenBlocklist.__table__.create(self.engine, checkfirst=True)
        sessions = scoped_session(self.Session)
        self.addCleanup(sessions.remove)
        # Redirect all DB access, including the real JWT revocation callback.
        with patch.object(app_factory, 'db_session', sessions), patch('src.schema.db_session', sessions), patch.object(Base, 'query', sessions.query_property()), patch.multiple(app_factory, db_user='test', db_password='test', db_name='local_streak_test', db_host='localhost', db_port='5432'):
            # Isolate API behavior from startup/migration configuration so this
            # test also runs before the separate migration-startup repair.
            with patch.object(app_factory, 'initialize_firebase'), patch.object(app_factory, 'init_db'), patch('app_factory.open', create=True):
                app = app_factory.create_app(run_migrations=True)
            app.config['JWT_SECRET_KEY'] = 'isolated-http-test-secret-at-least-32-characters'
            with app.app_context():
                token = create_access_token(identity=str(owner_id))
            client = app.test_client()
            headers = {'Authorization': 'Bearer ' + token}
            def execute(query, variables=None, authenticated=True):
                response = client.post('/graphql', json={'query': query, 'variables': variables or {}}, headers=headers if authenticated else {})
                self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
                return response.get_json()
            def snapshot():
                with self.engine.connect() as conn:
                    return [conn.execute(model.__table__.select().order_by(*model.__table__.primary_key.columns)).fetchall()
                            for model in (User, Workout, UserWorkoutWeek, UserWorkoutGoalHistory)]
            log = '''mutation($id: Int!, $time: DateTime!) {
                logWorkout(userId: $id, facilityId: 1, workoutTime: $time) { id userId workoutTime }
            }'''
            goal = '''mutation($id: Int!, $goal: Int!) {
                setWorkoutGoals(userId: $id, workoutGoal: $goal) { workoutGoal }
            }'''
            query = '{ getUserByNetId(netId: "http-owner") { activeStreak maxStreak workoutGoal currentWeekActiveDays } }'
            with patch('src.schema.datetime') as clock:
                clock.now.return_value = local('2026-10-28', 14)
                clock.side_effect = datetime
                before = snapshot()
                for mutation, variables in (
                    (log, {'id': other_id, 'time': local('2026-10-28').isoformat()}),
                    (goal, {'id': other_id, 'goal': 5}),
                ):
                    result = execute(mutation, variables)
                    self.assertIn('own workout data', result['errors'][0]['message'])
                result = execute(log, {'id': owner_id, 'time': local('2026-10-28').isoformat()}, authenticated=False)
                self.assertIn('errors', result)
                self.assertEqual(snapshot(), before)
                self.assertEqual(execute(goal, {'id': owner_id, 'goal': 5})['data']['setWorkoutGoals']['workoutGoal'], 5)
                for hour in (12, 13):
                    result = execute(log, {'id': owner_id, 'time': local('2026-10-28', hour).isoformat()})
                    self.assertNotIn('errors', result, result)
                # Older clients may still supply DateTime!, while new clients
                # can omit the argument. All forms must save server time.
                for timestamp in ('2026-09-01T12:00:00Z', '2099-01-01T12:00:00Z'):
                    result = execute(log, {'id': owner_id, 'time': timestamp})
                    self.assertNotIn('errors', result, result)
                    self.assertEqual(as_utc(datetime.fromisoformat(result['data']['logWorkout']['workoutTime'])), as_utc(local('2026-10-28', 14)))
                for operation, variables in (
                    ('mutation { logWorkout(userId: %s, facilityId: 1) { id workoutTime } }' % owner_id, {}),
                    ('mutation($time: DateTime) { logWorkout(userId: %s, facilityId: 1, workoutTime: $time) { id workoutTime } }' % owner_id, {'time': None}),
                ):
                    result = execute(operation, variables)
                    self.assertNotIn('errors', result, result)
                    self.assertEqual(as_utc(datetime.fromisoformat(result['data']['logWorkout']['workoutTime'])), as_utc(local('2026-10-28', 14)))
                result = execute(query)
                self.assertEqual(result['data']['getUserByNetId'][0], {
                    'activeStreak': 1, 'maxStreak': 1, 'workoutGoal': 5, 'currentWeekActiveDays': 1})
                self.session.expire_all()
                self.assertEqual(current_week(self.session, owner, local('2026-10-28')).workout_goal, 1)
                history = self.session.query(UserWorkoutGoalHistory).filter_by(user_id=owner_id).order_by(UserWorkoutGoalHistory.effective_at).all()
                self.assertEqual(as_utc(history[-1].effective_at), datetime(2026, 11, 2, 5, tzinfo=timezone.utc))
                self.assertEqual(self.session.query(Workout).filter_by(user_id=owner_id).count(), 6)
                self.session.rollback()
                self.assertEqual(run_weekly_rollover(sessions, local('2026-11-02')), 2)
                sessions.remove()
                clock.now.return_value = local('2026-11-02')
                result = execute(query)
                self.assertEqual(result['data']['getUserByNetId'][0]['activeStreak'], 1)
                self.assertEqual(result['data']['getUserByNetId'][0]['currentWeekActiveDays'], 0)
                self.assertEqual(run_weekly_rollover(sessions, local('2026-11-09')), 2)
                sessions.remove()
                clock.now.return_value = local('2026-11-09')
                result = execute(query)
                self.assertEqual(result['data']['getUserByNetId'][0]['activeStreak'], 0)
