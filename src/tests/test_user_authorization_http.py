"""Real-route authorization checks using synthetic accounts and verified JWTs."""

from datetime import datetime, timedelta, timezone

from unittest.mock import patch

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token

from src.models.friends import Friendship
from src.models.giveaway import Giveaway, GiveawayInstance
from src.models.token_blacklist import TokenBlocklist
from src.models.user import User
from src.models.workout import Workout
from src.tests.workout_test_db import local
from src.tests.workout_http_test import WorkoutHTTPTest
from src.utils.google_auth import GoogleIdentity, GoogleTokenVerificationError


class UserAuthorizationHTTPTests(WorkoutHTTPTest):
    """Exercise public documents, nested ORM results and account ownership."""

    def execute(self, query, variables=None, authenticated=True):
        response = self.client.post(
            "/graphql",
            json={"query": query, "variables": variables or {}},
            headers=self.headers if authenticated else {},
        )
        self.assertIn(response.status_code, (200, 400), response.get_data(as_text=True))
        return response.get_json()

    def setUp(self):
        super().setUp()
        for table in (Friendship.__table__, Giveaway.__table__, GiveawayInstance.__table__):
            table.create(self.engine, checkfirst=True)
        self.owner.email = "tester@cornell.edu"
        self.bob = User(name="Bob", net_id="bob", email="bob@cornell.edu", workout_goal=2)
        self.eve = User(name="Eve", net_id="eve", email="eve@cornell.edu")
        self.session.add_all([self.bob, self.eve])
        self.session.commit()

    def tearDown(self):
        self.session.rollback()
        for table in (GiveawayInstance.__table__, Giveaway.__table__, Friendship.__table__):
            table.drop(self.engine, checkfirst=True)
        super().tearDown()

    def as_user(self, user, refresh=False, expires_delta=None):
        with self.client.application.app_context():
            issuer = create_refresh_token if refresh else create_access_token
            token = issuer(identity=str(user.id), expires_delta=expires_delta)
        self.headers = {"Authorization": "Bearer " + token}
        return token

    def assert_rejected(self, document, variables=None, authenticated=True):
        result = self.execute(document, variables, authenticated)
        self.assertIn("errors", result, result)
        return result

    def test_google_signup_login_and_me_isolate_public_response(self):
        identity = GoogleIdentity(sub="new-google", net_id="newuser", email="newuser@cornell.edu")
        signup = (
            "mutation Signup($idToken: String!, $name: String!) { "
            "createUser(idToken: $idToken, name: $name) { id netId name encodedImage } }"
        )
        with patch("src.schema.verify_google_identity", return_value=identity):
            result = self.execute(signup, {"idToken": "google", "name": "New"}, False)
            self.assertNotIn("errors", result, result)
            self.assertEqual(result["data"]["createUser"]["netId"], "newuser")
            for _ in range(2):
                login = self.execute(
                    'mutation { loginWithGoogle(idToken: "google") { accessToken refreshToken } }', authenticated=False
                )
                self.assertNotIn("errors", login, login)
            self.headers = {"Authorization": "Bearer " + login["data"]["loginWithGoogle"]["accessToken"]}
            me = self.execute("{ me { email workoutGoal activeStreak workoutHistory { id } } }")
            self.assertEqual(
                me.get("data", {}).get("me"),
                dict(email="newuser@cornell.edu", workoutGoal=1, activeStreak=0, workoutHistory=[]),
                me,
            )
            self.assert_rejected(signup, {"idToken": "google", "name": "Duplicate"}, False)
        self.assertEqual(self.session.query(User).filter_by(net_id="newuser").count(), 1)
        with patch("src.schema.verify_google_identity", side_effect=GoogleTokenVerificationError("bad")):
            self.assert_rejected(signup, {"idToken": "bad", "name": "Bad"}, False)
        self.assert_rejected(
            'mutation { createUser(netId: "forged", email: "forged@cornell.edu", name: "Bad") { id } }',
            authenticated=False,
        )
        self.assert_rejected('mutation { loginUser(netId: "tester") { accessToken } }', authenticated=False)
        private_identity = GoogleIdentity(sub="private-google", net_id="private", email="private@cornell.edu")
        with patch("src.schema.verify_google_identity", return_value=private_identity):
            self.assert_rejected(
                'mutation { createUser(idToken: "google", name: "Private") { email } }', authenticated=False
            )
        self.assert_rejected("{ me { email } }", authenticated=False)
        failed_identity = GoogleIdentity(sub="failed-google", net_id="failed", email="failed@cornell.edu")
        with patch("src.schema.verify_google_identity", return_value=failed_identity), patch(
            "src.schema.db_session.commit", side_effect=RuntimeError("synthetic transaction failure")
        ):
            self.assert_rejected(signup, {"idToken": "google", "name": "Failed"}, False)
        self.assertEqual(self.session.query(User).filter_by(net_id="failed").count(), 0)

    def test_optional_actor_arguments_and_old_required_variable_documents(self):
        for argument in ("", "(id: %s)" % self.owner.id):
            result = self.execute("{ getWeeklyWorkoutDays%s getWorkoutsById%s { id } }" % (argument, argument))
            self.assertEqual(result.get("data"), dict(getWeeklyWorkoutDays=[], getWorkoutsById=[]), result)
        result = self.execute(
            "query Nullable($id: Int) { getWeeklyWorkoutDays(id: $id) getWorkoutsById(id: $id) { id } }", {"id": None}
        )
        self.assertNotIn("errors", result, result)
        result = self.execute(
            'mutation Nullable($id: Int) { editUser(userId: $id, name: "Updated") { name } }', {"id": None}
        )
        self.assertNotIn("errors", result, result)
        result = self.execute(
            "query Old($id: Int!) { getWeeklyWorkoutDays(id: $id) getWorkoutsById(id: $id) { id } }",
            {"id": self.owner.id},
        )
        self.assertNotIn("errors", result, result)
        for supplied in (str(self.bob.id), "0", '"wrong"'):
            self.assert_rejected("{ getWorkoutsById(id: %s) { id } }" % supplied)
        for argument in ("", "userId: %s, " % self.owner.id):
            result = self.execute('mutation { editUser(%sname: "Updated") { id name email } }' % argument)
            self.assertEqual(result.get("data", {}).get("editUser", {}).get("name"), "Updated", result)
        for operation in (
            'editUser(userId: %s, name: "Stolen") { id }',
            "deleteUser(userId: %s) { id }",
            "setWorkoutGoals(userId: %s, workoutGoal: 5) { id }",
            "logWorkout(userId: %s, facilityId: 1) { id }",
            "addFriend(userId: %s, friendId: 1) { id }",
            "getPendingFriendRequests(userId: %s) { pendingRequests { id } }",
        ):
            self.assert_rejected("mutation { " + operation % self.bob.id + " }")
        self.session.refresh(self.bob)
        self.assertEqual((self.bob.name, self.bob.workout_goal), ("Bob", 2))
        self.assertEqual(self.session.query(Workout).count(), 0)
        self.assertEqual(self.session.query(Friendship).count(), 0)

    def test_token_derived_workout_writes_and_netid_reads(self):
        for supplied in ({}, {"netId": None}, {"netId": "tester"}):
            result = self.execute("query Owner($netId: String) { getUserByNetId(netId: $netId) { email } }", supplied)
            self.assertEqual(result.get("data", {}).get("getUserByNetId"), [{"email": "tester@cornell.edu"}], result)
        for net_id in ("bob", ""):
            self.assert_rejected(
                "query Owner($netId: String) { getUserByNetId(netId: $netId) { id } }", {"netId": net_id}
            )
        for arguments, variables in (("", {}), ("userId: $id, ", {"id": None})):
            declaration = "($id: Int)" if arguments else ""
            result = self.execute(
                "mutation%s { logWorkout(%sfacilityId: 1) { userId } }" % (declaration, arguments), variables
            )
            self.assertEqual(result.get("data", {}).get("logWorkout"), {"userId": self.owner.id}, result)
        # First selection is the only immediate change; test null and omission
        # separately on fresh accounts to preserve real cooldown behavior.
        for user, argument in ((self.owner, ""), (self.bob, "userId: $id, ")):
            self.as_user(user)
            declaration = "($id: Int)" if argument else ""
            result = self.execute(
                "mutation%s { setWorkoutGoals(%sworkoutGoal: 4) { workoutGoal } }" % (declaration, argument),
                {"id": None} if argument else {},
            )
            self.assertEqual(result.get("data", {}).get("setWorkoutGoals"), {"workoutGoal": 4}, result)

    def test_nested_privacy_aliases_fragments_and_orm_relationships(self):
        self.session.add(Friendship(user_id=self.owner.id, friend_id=self.bob.id, is_accepted=True))
        self.session.add(Workout(user_id=self.bob.id, facility_id=1, workout_time=local("2026-10-28")))
        self.session.commit()
        public = self.execute("{ me { friends { id netId name encodedImage } } }")
        self.assertEqual(public.get("data", {}).get("me", {}).get("friends", [])[0]["name"], "Bob", public)
        for document in (
            "{ me { friends { alias: email } } }",
            "query { me { friends { ...Private } } } fragment Private on User { workoutGoal }",
            "{ me { friendRequestsSent { friend { email } } } }",
            '{ getUserByNetId(netId: "bob") { email } }',
            "{ getWorkoutsById(id: %s) { workoutTime user { email } } }" % self.bob.id,
        ):
            self.assert_rejected(document)
        # A request by Bob must not reuse Alice's verified identity or loader state.
        self.as_user(self.bob)
        result = self.execute("{ me { email workoutGoal } }")
        self.assertEqual(result.get("data", {}).get("me"), dict(email="bob@cornell.edu", workoutGoal=2), result)

    def test_friend_recipient_acceptance_participant_removal_and_giveaway_actor(self):
        row = Friendship(user_id=self.owner.id, friend_id=self.bob.id)
        giveaway = Giveaway(name="Synthetic")
        self.session.add_all([row, giveaway])
        self.session.commit()
        accept = "mutation { acceptFriendRequest(friendshipId: %s) { id isAccepted } }" % row.id
        self.assert_rejected(accept)
        self.as_user(self.eve)
        self.assert_rejected(accept)
        self.assert_rejected(
            "mutation { removeFriend(userId: %s, friendId: %s) { success } }" % (self.owner.id, self.bob.id)
        )
        self.session.refresh(row)
        self.assertFalse(row.is_accepted)
        self.as_user(self.bob)
        self.assertNotIn("errors", self.execute(accept))
        result = self.execute("mutation { removeFriend(friendId: %s) { success } }" % self.owner.id)
        self.assertEqual(result.get("data", {}).get("removeFriend"), dict(success=True), result)
        self.assertEqual(self.session.query(Friendship).count(), 0)
        self.session.add(Friendship(user_id=self.owner.id, friend_id=self.bob.id))
        self.session.commit()
        self.as_user(self.owner)
        result = self.execute("mutation { removeFriend(friendId: %s) { success } }" % self.bob.id)
        self.assertEqual(result.get("data", {}).get("removeFriend"), dict(success=True), result)
        self.as_user(self.bob)
        self.assert_rejected('mutation { enterGiveaway(userNetId: "tester", giveawayId: %s) { id } }' % giveaway.id)
        self.assertEqual(self.session.query(GiveawayInstance).count(), 0)
        for actor in ("", 'userNetId: "bob", '):
            result = self.execute("mutation { enterGiveaway(%sgiveawayId: %s) { numEntries } }" % (actor, giveaway.id))
            self.assertNotIn("errors", result, result)
        result = self.execute(
            "mutation Nullable($id: String, $giveaway: Int!) { "
            "enterGiveaway(userNetId: $id, giveawayId: $giveaway) { numEntries } }",
            {"id": None, "giveaway": giveaway.id},
        )
        self.assertNotIn("errors", result, result)
        self.assertEqual(self.session.query(GiveawayInstance).one().num_entries, 3)

    def test_credentials_and_deleted_owner_response(self):
        for refresh, expiry in ((True, None), (False, timedelta(seconds=-1))):
            self.as_user(self.owner, refresh=refresh, expires_delta=expiry)
            self.assert_rejected("{ me { email } }")
        self.headers = {"Authorization": "Bearer invalid"}
        self.assert_rejected("{ me { email } }")
        token = self.as_user(self.owner)
        with self.client.application.app_context():
            jti = decode_token(token)["jti"]
        self.session.add(TokenBlocklist(jti=jti, expires_at=datetime.now(timezone.utc) + timedelta(hours=1)))
        self.session.commit()
        self.assert_rejected("{ me { email } }")
        self.session.query(TokenBlocklist).delete()
        self.session.commit()
        self.as_user(self.eve)
        result = self.execute("mutation { deleteUser { id name email } }")
        self.assertEqual(result.get("data", {}).get("deleteUser", {}).get("email"), "eve@cornell.edu", result)
        self.assertIsNone(self.session.query(User).filter_by(id=self.eve.id).first())
        self.assert_rejected("{ me { email } }")
