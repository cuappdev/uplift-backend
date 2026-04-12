import binascii

import graphene
import base64
import os
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required
from functools import wraps
from datetime import datetime, timedelta, time, timezone
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError
from src.models.capacity import Capacity as CapacityModel
from src.models.capacity_reminder import CapacityReminder as CapacityReminderModel
from src.models.facility import Facility as FacilityModel
from src.models.gym import Gym as GymModel
from src.models.openhours import OpenHours as OpenHoursModel
from src.models.amenity import Amenity as AmenityModel
from src.models.equipment import Equipment as EquipmentModel
from src.models.activity import Activity as ActivityModel, Price as PriceModel
from src.models.classes import Class as ClassModel
from src.models.classes import ClassInstance as ClassInstanceModel
from src.models.token_blacklist import TokenBlocklist
from src.models.user import User as UserModel
from src.models.friends import Friendship as FriendshipModel
from src.models.enums import DayOfWeekGraphQLEnum, CapacityReminderGymGraphQLEnum
from src.models.giveaway import Giveaway as GiveawayModel
from src.models.giveaway import GiveawayInstance as GiveawayInstanceModel
from src.models.workout import Workout as WorkoutModel
from src.models.report import Report as ReportModel
from src.models.hourly_average_capacity import HourlyAverageCapacity as HourlyAverageCapacityModel
from src.models.user_workout_goal_history import UserWorkoutGoalHistory as UserWorkoutGoalHistoryModel
from src.database import db_session
import requests
from firebase_admin import messaging
import logging
from zoneinfo import ZoneInfo
from sqlalchemy import func, cast, Date
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

local_tz = ZoneInfo("America/New_York")

def resolve_enum_value(entry):
    """Return the raw value for Enum objects while leaving plain strings untouched."""
    return getattr(entry, "value", entry)


def ensure_utc(dt):
    """
    Normalize a datetime to UTC.
    - If dt is None, return None.
    - If dt is naive, assume it is already in UTC and attach UTC tzinfo.
    - If dt is timezone-aware, convert it to UTC.
    """
    if dt is None:
        return None
    if getattr(dt, "tzinfo", None) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_local_time(dt):
    """
    Convert a UTC datetime to the server's local timezone for output.
    - If dt is None, return None.
    - If dt is naive, assume it is UTC first.
    - If dt is timezone-aware, convert from UTC to local.
    """
    if dt is None:
        return None

    dt_utc = ensure_utc(dt)
    if dt_utc is None:
        return None

    # Convert to local timezone (server-local)
    return dt_utc.astimezone(local_tz)


def goal_at(goal_history, window_start_date):
    """
    Determine the workout goal for a given window start date from the goal history.
    Parameters:
        - `window_start_date` (datetime.date): The start date of the window.
        - `goal_history` (list[tuple[int, datetime.datetime]]): The list of workout goal history entries.
    Returns:
        - The workout goal for the given window start date.
    """
    for workout_goal, effective_at in goal_history:
        if effective_at.date() <= window_start_date:
            return workout_goal

    return goal_history[-1][0]


# MARK: - Gym


class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel

    amenities = graphene.List(lambda: Amenity)
    facilities = graphene.List(lambda: Facility)
    hours = graphene.List(lambda: OpenHours)
    activities = graphene.List(lambda: Activity)

    def resolve_amenities(self, info):
        query = Amenity.get_query(info=info).filter(AmenityModel.gym_id == self.id)
        return query

    def resolve_facilities(self, info):
        query = Facility.get_query(info=info).filter(FacilityModel.gym_id == self.id)
        return query

    def resolve_hours(self, info):
        query = OpenHours.get_query(info=info).filter(OpenHoursModel.gym_id == self.id)
        return query

    def resolve_activities(self, info):
        query = Activity.get_query(info=info).filter(ActivityModel.gym_id == self.id)
        return query


# MARK: - Facility


class Facility(SQLAlchemyObjectType):
    class Meta:
        model = FacilityModel

    capacity = graphene.Field(lambda: Capacity)
    hours = graphene.List(lambda: OpenHours)
    equipment = graphene.List(lambda: Equipment)
    activities = graphene.List(lambda: Activity)

    def resolve_capacity(self, info):
        query = (
            Capacity.get_query(info=info)
            .filter(CapacityModel.facility_id == self.id)
            .order_by(CapacityModel.updated.desc())
            .first()
        )
        return query

    def resolve_hours(self, info):
        query = OpenHours.get_query(info=info).filter(OpenHoursModel.facility_id == self.id)
        return query

    def resolve_equipment(self, info):
        query = Equipment.get_query(info=info).filter(EquipmentModel.facility_id == self.id)
        return query

    def resolve_activities(self, info):
        query = Activity.get_query(info=info).filter(ActivityModel.facility_id == self.id)
        return query


# MARK: - Open Hours


class OpenHours(SQLAlchemyObjectType):
    class Meta:
        model = OpenHoursModel


# MARK: - Equipment


class Equipment(SQLAlchemyObjectType):
    class Meta:
        model = EquipmentModel


# MARK: - Amenity


class Amenity(SQLAlchemyObjectType):
    class Meta:
        model = AmenityModel


# MARK: - Capacity


class Capacity(SQLAlchemyObjectType):
    class Meta:
        model = CapacityModel


# MARK - Hourly Average Capacity
class HourlyAverageCapacity(SQLAlchemyObjectType):
    class Meta:
        model = HourlyAverageCapacityModel

    day_of_week = graphene.Field(DayOfWeekGraphQLEnum)


# MARK: - Price


class Price(SQLAlchemyObjectType):
    class Meta:
        model = PriceModel


# MARK: - Class


class Class(SQLAlchemyObjectType):
    class Meta:
        model = ClassModel

    class_instances = graphene.List(lambda: ClassInstance)

    def resolve_class_instances(self, info):
        query = ClassInstance.get_query(info=info).filter(ClassInstanceModel.class_id == self.id)
        return query


# MARK: - Class Instance


class ClassInstance(SQLAlchemyObjectType):
    class Meta:
        model = ClassInstanceModel

    gym = graphene.Field(lambda: Gym)
    class_ = graphene.Field(lambda: Class)

    def resolve_gym(self, info):
        query = Gym.get_query(info=info).filter(GymModel.id == self.gym_id).first()
        return query

    def resolve_class_(self, info):
        query = Class.get_query(info=info).filter(ClassModel.id == self.class_id).first()
        return query


# MARK: - Activity


class Activity(SQLAlchemyObjectType):
    class Meta:
        model = ActivityModel

    pricing = graphene.List(lambda: Price)

    def resolve_pricing(self, info):
        query = Price.get_query(info=info).filter(PriceModel.activity_id == self.id)
        return query


class WorkoutGoalHistory(SQLAlchemyObjectType):
    class Meta:
        model = UserWorkoutGoalHistoryModel

    def resolve_effective_at(self, info):
        return to_local_time(self.effective_at)


# MARK: - User


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel

    friendships = graphene.List(lambda: Friendship)
    friends = graphene.List(lambda: User)
    total_gym_days = graphene.Int(
        required=True, description="Get the total number of gym days (unique workout days) for user."
    )
    streak_start = graphene.DateTime(
        description="The start datetime of the most recent active streak (midnight of the day in local timezone), up until the current date."
    )
    workout_history = graphene.List(lambda: Workout)

    def resolve_workout_history(self, info):
        query = Workout.get_query(info).filter(WorkoutModel.user_id == self.id).order_by(WorkoutModel.workout_time.desc())
        return query.all()

    def resolve_total_gym_days(self, info):
        return (
            Workout.get_query(info)
            .filter(WorkoutModel.user_id == self.id)
            .with_entities(
                func.count(func.distinct(cast(WorkoutModel.workout_time, Date)))
            )  # We cast the datetiem object as a Date object to get the unique days
            .scalar()
        )

    def resolve_active_streak(self, info):
        user = User.get_query(info).filter(UserModel.id == self.id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")

        workout_date_rows = (
            Workout.get_query(info)
            .filter(WorkoutModel.user_id == user.id)
            .with_entities(cast(WorkoutModel.workout_time, Date).label("workout_date"))
            .distinct()
            .order_by(cast(WorkoutModel.workout_time, Date).desc())
            .all()
        )

        if not workout_date_rows:
            return 0

        workout_dates = [row[0] for row in workout_date_rows]

        goal_hist = (
            db_session.query(UserWorkoutGoalHistoryModel.workout_goal, UserWorkoutGoalHistoryModel.effective_at)
            .filter(UserWorkoutGoalHistoryModel.user_id == user.id)
            .order_by(UserWorkoutGoalHistoryModel.effective_at.desc())
            .all()
        )

        if not goal_hist:
            if not self.workout_goal:
                return 0
            goal_hist = [(self.workout_goal, datetime.min)]

        today = datetime.now(timezone.utc).date()

        day_pointer, total_workout_days = 0, len(workout_dates)
        window_end = today

        streak = 0

        while day_pointer < total_workout_days:
            window_start = window_end - timedelta(days=6)

            day_iterator = day_pointer
            count_in_window = 0

            while day_iterator < total_workout_days and workout_dates[day_iterator] >= window_start:
                count_in_window += 1
                day_iterator += 1

            goal_days = goal_at(goal_hist, window_start)

            if count_in_window == 0:
                break
            elif count_in_window >= goal_days:
                streak += 1
            else:
                pass

            window_end -= timedelta(days=7)
            day_pointer = day_iterator

        return streak

    def resolve_streak_start(self, info):
        user = User.get_query(info).filter(UserModel.id == self.id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")

        workout_date_rows = (
            Workout.get_query(info)
            .filter(WorkoutModel.user_id == user.id)
            .with_entities(cast(WorkoutModel.workout_time, Date).label("workout_date"))
            .distinct()
            .order_by(cast(WorkoutModel.workout_time, Date).desc())
            .all()
        )

        if not workout_date_rows:
            return None

        workout_dates = [row[0] for row in workout_date_rows]
        if not workout_dates:
            return None

        goal_hist = (
            db_session.query(UserWorkoutGoalHistoryModel.workout_goal, UserWorkoutGoalHistoryModel.effective_at)
            .filter(UserWorkoutGoalHistoryModel.user_id == user.id)
            .order_by(UserWorkoutGoalHistoryModel.effective_at.desc())
            .all()
        )

        if not goal_hist:
            return None

        goal_values = [goal for goal, _ in goal_hist]
        goal_effective_dates = []
        for _, eff_at in goal_hist:
            if eff_at.tzinfo is None:
                eff_at = eff_at.replace(tzinfo=timezone.utc)
            goal_effective_dates.append(eff_at.date())

        if not goal_effective_dates:
            return None

        goal_index = 0

        def goal_for_window_start(ws_date):
            nonlocal goal_index

            while goal_index < len(goal_values) - 1 and ws_date < goal_effective_dates[goal_index]:
                goal_index += 1

            if ws_date < goal_effective_dates[-1]:
                return None

            return goal_values[goal_index]

        today = datetime.now(timezone.utc).date()
        window_end = today

        day_pointer = 0
        total = len(workout_dates)

        idx_last_streak_start = None

        while day_pointer < total:
            while day_pointer < total and workout_dates[day_pointer] > today:
                day_pointer += 1

            window_start = window_end - timedelta(days=6)

            window_goal = goal_for_window_start(window_start)
            if window_goal is None:
                break

            i = day_pointer
            while i < total and workout_dates[i] >= window_start:
                i += 1

            count_in_window = i - day_pointer

            if count_in_window == 0:
                break

            if count_in_window >= window_goal:
                if i - 1 >= 0:
                    idx_last_streak_start = i - 1

            window_end -= timedelta(days=7)
            day_pointer = i

        if idx_last_streak_start is None:
            return None

        last_streak_start_date = workout_dates[idx_last_streak_start]
        local_midnight = datetime.combine(last_streak_start_date, time.min, tzinfo=local_tz)
        return local_midnight

    def resolve_max_streak(self, info):
        user = User.get_query(info).filter(UserModel.id == self.id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")

        workout_date_rows = (
            Workout.get_query(info)
            .filter(WorkoutModel.user_id == user.id)
            .with_entities(cast(WorkoutModel.workout_time, Date).label("workout_date"))
            .distinct()
            .order_by(cast(WorkoutModel.workout_time, Date).desc())
            .all()
        )

        if not workout_date_rows:
            return 0

        workout_dates = [row[0] for row in workout_date_rows]

        goal_hist = (
            db_session.query(UserWorkoutGoalHistoryModel.workout_goal, UserWorkoutGoalHistoryModel.effective_at)
            .filter(UserWorkoutGoalHistoryModel.user_id == user.id)
            .order_by(UserWorkoutGoalHistoryModel.effective_at.desc())
            .all()
        )

        if not goal_hist:
            if not self.workout_goal:
                return 0
            goal_hist = [(self.workout_goal, datetime.min)]

        today = datetime.now(timezone.utc).date()
        day_pointer, total_workout_dates = 0, len(workout_dates)
        window_end = today

        run_met_goal = 0
        max_met_goal = 0

        while day_pointer < total_workout_dates:
            while day_pointer < total_workout_dates and workout_dates[day_pointer] > today:
                day_pointer += 1

            window_start = window_end - timedelta(days=6)

            day_iterator = day_pointer
            count_in_window = 0

            while day_iterator < total_workout_dates and workout_dates[day_iterator] >= window_start:
                count_in_window += 1
                day_iterator += 1

            goal_days = goal_at(goal_hist, window_start)

            if count_in_window == 0:
                max_met_goal = max(max_met_goal, run_met_goal)
                run_met_goal = 0
            elif goal_days and count_in_window >= goal_days:
                run_met_goal += 1
            else:
                pass

            window_end -= timedelta(days=7)

            day_pointer = day_iterator

        max_met_goal = max(max_met_goal, run_met_goal)
        return max_met_goal

    def resolve_friendships(self, info):
        # Return all friendship relationships for this user
        query = Friendship.get_query(info).filter(
            (FriendshipModel.user_id == self.id) | (FriendshipModel.friend_id == self.id)
        )
        return query.all()

    def resolve_friends(self, info):
        # Return all friend users for this user
        direct_friendships = Friendship.get_query(info).filter(FriendshipModel.user_id == self.id).all()
        reverse_friendships = Friendship.get_query(info).filter(FriendshipModel.friend_id == self.id).all()

        friend_ids = set()
        # Add friend_ids from direct friendships
        for friendship in direct_friendships:
            if friendship.is_accepted:  # Only include accepted friendships
                friend_ids.add(friendship.friend_id)

        # Add user_ids from reverse friendships
        for friendship in reverse_friendships:
            if friendship.is_accepted:  # Only include accepted friendships
                friend_ids.add(friendship.user_id)

        # Query for all the users at once
        return User.get_query(info).filter(UserModel.id.in_(friend_ids)).all()


class UserInput(graphene.InputObjectType):
    net_id = graphene.String(required=True)
    giveaway_id = graphene.Int(required=True)


# MARK: - Friendship


class Friendship(SQLAlchemyObjectType):
    class Meta:
        model = FriendshipModel

    user = graphene.Field(lambda: User)
    friend = graphene.Field(lambda: User)

    def resolve_user(self, info):
        query = User.get_query(info).filter(UserModel.id == self.user_id).first()
        return query

    def resolve_friend(self, info):
        query = User.get_query(info).filter(UserModel.id == self.friend_id).first()
        return query

    def resolve_accepted_at(self, info):
        return to_local_time(self.accepted_at)


# MARK: - Giveaway


class Giveaway(SQLAlchemyObjectType):
    class Meta:
        model = GiveawayModel


# MARK: - Giveaway Instance


class GiveawayInstance(SQLAlchemyObjectType):
    class Meta:
        model = GiveawayInstanceModel


# MARK: - Workout


class Workout(SQLAlchemyObjectType):
    class Meta:
        model = WorkoutModel

    gym_name = graphene.String(required=True)

    def resolve_gym_name(self, info):
        facility = Facility.get_query(info).filter(FacilityModel.id == self.facility_id).first()
        if not facility:
            raise GraphQLError("Facility for workout not found.")
        gym = Gym.get_query(info).filter(GymModel.id == facility.gym_id).first()
        if not gym:
            raise GraphQLError("Gym for workout not found.")
        return gym.name

    def resolve_workout_time(self, info):
        return to_local_time(self.workout_time)


# MARK: - Report


class Report(SQLAlchemyObjectType):
    class Meta:
        model = ReportModel

    gym = graphene.Field(lambda: Gym)

    def resolve_gym(self, info):
        query = Gym.get_query(info).filter(GymModel.id == self.gym_id).first()
        return query

    def resolve_created_at(self, info):
        return to_local_time(self.created_at)


# MARK: - Capacity Reminder


class CapacityReminder(SQLAlchemyObjectType):
    class Meta:
        model = CapacityReminderModel
        exclude_fields = ("fcm_token",)
        

# MARK: - Query


class Query(graphene.ObjectType):
    get_all_gyms = graphene.List(Gym, description="Get all gyms.")
    get_user_by_net_id = graphene.List(User, net_id=graphene.String(), description="Get user by Net ID.")
    get_users_friends = graphene.List(User, id=graphene.Int(), description="Get all friends of a user by ID.")
    get_users_by_giveaway_id = graphene.List(User, id=graphene.Int(), description="Get all users given a giveaway ID.")
    get_weekly_workout_days = graphene.List(
        graphene.String, id=graphene.Int(), description="Get the days a user worked out for the current week."
    )
    get_workouts_by_id = graphene.List(Workout, id=graphene.Int(), description="Get all of a user's workouts by ID.")
    activities = graphene.List(Activity)
    get_all_reports = graphene.List(Report, description="Get all reports.")
    get_hourly_average_capacities_by_facility_id = graphene.List(
        HourlyAverageCapacity, facility_id=graphene.Int(), description="Get all facility hourly average capacities."
    )
    get_user_friends = graphene.List(
        User, user_id=graphene.Int(required=True), description="Get all friends for a user."
    )
    get_capacity_reminder_by_id = graphene.Field(
        CapacityReminder, id=graphene.Int(required=True), description="Get a specific capacity reminder by its ID."
    )
    get_all_capacity_reminders = graphene.List(CapacityReminder, description="Get all capacity reminders.")

    def resolve_get_all_gyms(self, info):
        query = Gym.get_query(info)
        return query.all()

    def resolve_activities(self, info):
        query = Activity.get_query(info)
        return query.all()

    def resolve_get_user_by_net_id(self, info, net_id):
        user = User.get_query(info).filter(UserModel.net_id == net_id).all()
        if not user:
            raise GraphQLError("User with the given Net ID does not exist.")
        return user

    def resolve_get_users_friends(self, info, id):
        user = User.get_query(info).filter(UserModel.id == id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")
        friends = user.get_friends()
        return friends

    def resolve_get_users_by_giveaway_id(self, info, id):
        entries = GiveawayInstance.get_query(info).filter(GiveawayInstanceModel.giveaway_id == id).all()
        users = [User.get_query(info).filter(UserModel.id == entry.user_id).first() for entry in entries]
        return users

    @jwt_required()
    def resolve_get_workouts_by_id(self, info, id):
        user = User.get_query(info).filter(UserModel.id == id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")
        workouts = Workout.get_query(info).filter(WorkoutModel.user_id == user.id).all()
        return workouts

    @jwt_required()
    def resolve_get_weekly_workout_days(self, info, id):
        user = User.get_query(info).filter(UserModel.id == id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")

        # Get the date 7 days ago in UTC
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        # Query distinct workout dates for the user in the past week. Workouts must never be logged for a future date.
        workout_days = (
            Workout.get_query(info)
            .filter(
                WorkoutModel.user_id == user.id, WorkoutModel.workout_time >= one_week_ago  # Use 'workout_time' here
            )
            .all()
        )

        # Extract days of the week from the workout times (use a set to avoid duplicates)
        # Convert workout_time to local time so the weekday reflects the user's local date.
        workout_days_set = {to_local_time(workout.workout_time).strftime("%A") for workout in workout_days}

        return list(workout_days_set)

    def resolve_get_all_reports(self, info):
        query = ReportModel.query.all()
        return query

    def resolve_get_hourly_average_capacities_by_facility_id(self, info, facility_id):
        valid_facility_ids = [14492437, 8500985, 7169406, 10055021, 2323580, 16099753, 15446768, 12572681]
        if facility_id not in valid_facility_ids:
            raise GraphQLError("Invalid facility ID.")
        query = HourlyAverageCapacity.get_query(info).filter(HourlyAverageCapacityModel.facility_id == facility_id)
        return query.all()

    @jwt_required()
    def resolve_get_user_friends(self, info, user_id):
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")

        # Direct friendships where user is the initiator
        direct_friendships = (
            Friendship.get_query(info)
            .filter((FriendshipModel.user_id == user_id) & (FriendshipModel.is_accepted == True))
            .all()
        )

        # Reverse friendships where user is the recipient
        reverse_friendships = (
            Friendship.get_query(info)
            .filter((FriendshipModel.friend_id == user_id) & (FriendshipModel.is_accepted == True))
            .all()
        )

        friend_ids = set()
        for friendship in direct_friendships:
            friend_ids.add(friendship.friend_id)

        for friendship in reverse_friendships:
            friend_ids.add(friendship.user_id)

        # Query for all friends at once
        return User.get_query(info).filter(UserModel.id.in_(friend_ids)).all()

    @jwt_required()
    def resolve_get_capacity_reminder_by_id(self, info, id):
        reminder = CapacityReminder.get_query(info).filter(CapacityReminderModel.id == id).first()

        if not reminder:
            raise GraphQLError("Capacity reminder with the given ID does not exist.")

        return reminder

    @jwt_required()
    def resolve_get_all_capacity_reminders(self, info):
        query = CapacityReminder.get_query(info)
        return query.all()


# MARK: - Mutation


class LoginUser(graphene.Mutation):
    class Arguments:
        net_id = graphene.String(required=True)

    access_token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, net_id):
        user = db_session.query(UserModel).filter(UserModel.net_id == net_id).first()
        if not user:
            return GraphQLError("No user with those credentials. Please create an account and try again.")

        # Generate JWT token
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        db_session.commit()

        return LoginUser(access_token=access_token, refresh_token=refresh_token)


class RefreshAccessToken(graphene.Mutation):
    new_access_token = graphene.String()

    @jwt_required(refresh=True)
    def mutate(self, info):
        identity = get_jwt_identity()

        new_access_token = create_access_token(identity=identity)
        return RefreshAccessToken(new_access_token=new_access_token)


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()

    @jwt_required(verify_type=False)  # Allows both access and refresh tokens
    def mutate(self, info):
        token = get_jwt()
        jti = token["jti"]  # Unique identifier for the token

        # Get expiration time from JWT itself
        expires_at = datetime.fromtimestamp(token["exp"], tz=timezone.utc)

        # Store in blocklist
        token = TokenBlocklist(jti=jti, expires_at=expires_at)
        db_session.add(token)
        db_session.commit()

        return LogoutUser(success=True)


class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        net_id = graphene.String(required=True)
        email = graphene.String(required=True)
        encoded_image = graphene.String(required=False)

    Output = User

    def mutate(self, info, name, net_id, email, encoded_image=None):
        # Check if a user with the given NetID already exists
        existing_user = db_session.query(UserModel).filter(UserModel.net_id == net_id).first()
        if existing_user:
            raise GraphQLError("NetID already exists.")

        final_photo_url = None
        
        if encoded_image:
            
            s3 = boto3.client(
                "s3",
                endpoint_url=os.getenv("DIGITAL_OCEAN_URL"),
                aws_access_key_id=os.getenv("DIGITAL_OCEAN_ACCESS"),
                aws_secret_access_key=os.getenv("DIGITAL_OCEAN_SECRET_ACCESS"),
                config=Config(s3={"addressing_style": "path"}),
            )
            
            try:
                image_data = base64.b64decode(encoded_image, validate=True)
            except (binascii.Error, ValueError) as err:
                raise GraphQLError("Invalid profile image encoding.") 

            try:
                bucket = "appdev-upload"
                path = f"uplift-dev/user-profile/{net_id}-profile.png"
                region = "nyc3"
                
                s3.put_object(
                    Bucket=bucket,
                    Key=path, 
                    Body=image_data,
                    ContentType="image/png",
                    ACL="public-read"
                )
                
                final_photo_url = f"https://{bucket}.{region}.digitaloceanspaces.com/{path}"
            except ClientError as e:
                print("Upload error:", e)
                raise GraphQLError("Error uploading user profile picture.")        
        
        new_user = UserModel(name=name, net_id=net_id, email=email, encoded_image=final_photo_url)
        db_session.add(new_user)
        db_session.commit()

        return new_user


class EditUserById(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        name = graphene.String(required=False)
        email = graphene.String(required=False)
        encoded_image = graphene.String(required=False)

    Output = User

    @jwt_required()
    def mutate(self, info, user_id, name=None, email=None, encoded_image=None):
        existing_user = db_session.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not existing_user:
            raise GraphQLError("User with given id does not exist.")
        if int(get_jwt_identity()) != user_id:
            raise GraphQLError("Unauthorized operation")
        if name is not None:
            existing_user.name = name
        if email is not None:
            existing_user.email = email
        if encoded_image is not None:
            final_photo_url = None
            s3 = boto3.client(
                "s3",
                endpoint_url=os.getenv("DIGITAL_OCEAN_URL"),
                aws_access_key_id=os.getenv("DIGITAL_OCEAN_ACCESS"),
                aws_secret_access_key=os.getenv("DIGITAL_OCEAN_SECRET_ACCESS"),
                config=Config(s3={"addressing_style": "path"}),
            )
            
            try:
                image_data = base64.b64decode(encoded_image, validate=True)
            except (binascii.Error, ValueError) as err:
                raise GraphQLError("Invalid profile image encoding.")

            try:
                bucket = "appdev-upload"
                path = f"uplift-dev/user-profile/{existing_user.net_id}-profile.png"
                region = "nyc3"
                
                s3.put_object(
                    Bucket=bucket,
                    Key=path, 
                    Body=image_data,
                    ContentType="image/png",
                    ACL="public-read"
                )
                
                final_photo_url = f"https://{bucket}.{region}.digitaloceanspaces.com/{path}"
                existing_user.encoded_image = final_photo_url
            except ClientError as e:
                print("Upload error:", e)
                raise GraphQLError("Error adding new user profile picture.")        

        db_session.commit()
        return existing_user


class EnterGiveaway(graphene.Mutation):
    class Arguments:
        user_net_id = graphene.String(required=True)
        giveaway_id = graphene.Int(required=True)

    Output = GiveawayInstance

    @jwt_required()
    def mutate(self, info, user_net_id, giveaway_id):
        # Check if NetID and Giveaway ID exists
        user = User.get_query(info).filter(UserModel.net_id == user_net_id).first()
        if not user:
            raise GraphQLError("User with given NetID does not exist.")

        giveaway = Giveaway.get_query(info).filter(GiveawayModel.id == giveaway_id).first()
        if not giveaway:
            raise GraphQLError("Giveaway does not exist.")

        # Compute number of entries
        giveaway_instance = (
            GiveawayInstance.get_query(info)
            .filter(GiveawayInstanceModel.giveaway_id == giveaway_id)
            .filter(GiveawayInstanceModel.user_id == user.id)
            .first()
        )
        if not giveaway_instance:
            # Giveaway does not exist
            giveaway_instance = GiveawayInstanceModel(user_id=user.id, giveaway_id=giveaway_id, num_entries=1)
            db_session.add(giveaway_instance)
        else:
            # Giveaway exists
            giveaway_instance.num_entries += 1

        db_session.commit()
        return giveaway_instance


class CreateGiveaway(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    Output = Giveaway

    def mutate(self, info, name):
        giveaway = GiveawayModel(name=name)
        db_session.add(giveaway)
        db_session.commit()
        return giveaway


class AddFriend(graphene.Mutation):
    class Arguments:
        user_net_id = graphene.String(required=True, description="The Net ID of the user.")
        friend_net_id = graphene.String(required=True, description="The Net ID of the friend to add.")

    Output = User

    def mutate(self, info, user_net_id, friend_net_id):
        user = User.get_query(info).filter(UserModel.net_id == user_net_id).first()
        if not user:
            raise GraphQLError("User with given NetID does not exist.")

        friend = User.get_query(info).filter(UserModel.net_id == friend_net_id).first()
        if not friend:
            raise GraphQLError("Friend with given NetID does not exist.")

        # Add friend
        if friend not in user.friends:
            user.add_friend(friend)

        db_session.commit()
        return user


class RemoveFriend(graphene.Mutation):
    class Arguments:
        user_net_id = graphene.String(required=True, description="The Net ID of the user.")
        friend_net_id = graphene.String(required=True, description="The Net ID of the friend to remove.")

    Output = User

    def mutate(self, info, user_net_id, friend_net_id):
        user = User.get_query(info).filter(UserModel.net_id == user_net_id).first()
        if not user:
            raise GraphQLError("User with given NetID does not exist.")

        friend = User.get_query(info).filter(UserModel.net_id == friend_net_id).first()
        if not friend:
            raise GraphQLError("Friend with given NetID does not exist.")

        # Remove friend
        if friend in user.friends:
            user.remove_friend(friend)

        db_session.commit()
        return user


class SetWorkoutGoals(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True, description="The ID of the user.")
        workout_goal = graphene.Int(
            required=True, description="The new workout goal for the user in terms of number of days per week."
        )

    Output = User

    @jwt_required()
    def mutate(self, info, user_id, workout_goal):
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")

        if user.workout_goal == workout_goal:
            return user

        last_change_dt = user.last_goal_change
        latest_history_entry = (
            db_session.query(UserWorkoutGoalHistoryModel)
            .filter(UserWorkoutGoalHistoryModel.user_id == user.id)
            .order_by(UserWorkoutGoalHistoryModel.effective_at.desc())
            .first()
        )
        has_history = latest_history_entry is not None

        if last_change_dt is None and latest_history_entry is not None:
            last_change_dt = latest_history_entry.effective_at

        if last_change_dt is not None:
            now_utc = datetime.now(timezone.utc)
            last_change_utc = ensure_utc(last_change_dt)
            if last_change_utc is not None and now_utc - last_change_utc < timedelta(days=30):
                raise GraphQLError("Workout goal can only be updated once every 30 days.")

        if not has_history:
            effective_at = datetime.now(timezone.utc)
        else:
            next_start_date = datetime.now(timezone.utc).date() + timedelta(days=1)
            effective_at = datetime.combine(next_start_date, datetime.min.time()).replace(tzinfo=timezone.utc)

        user.last_goal_change = effective_at
        user.last_streak = user.active_streak
        user.workout_goal = workout_goal

        db_session.add(
            UserWorkoutGoalHistoryModel(user_id=user.id, workout_goal=workout_goal, effective_at=effective_at)
        )

        db_session.commit()
        return user
    
class logWorkout(graphene.Mutation):
    class Arguments:
        workout_time = graphene.DateTime(required=True)
        user_id = graphene.Int(required=True)
        facility_id = graphene.Int(required=True)

    Output = Workout

    @jwt_required()
    def mutate(self, info, workout_time, user_id, facility_id):
        if not workout_time:
            raise GraphQLError("Workout time is required.")
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")
        facility = Facility.get_query(info).filter(FacilityModel.id == facility_id).first()
        if not facility:
            raise GraphQLError("Facility with given ID does not exist.")

        workout_time_utc = ensure_utc(workout_time)

        workout = WorkoutModel(workout_time=workout_time_utc, user_id=user.id, facility_id=facility.id)

        db_session.add(workout)
        db_session.commit()
        return workout


class CreateReport(graphene.Mutation):
    class Arguments:
        issue = graphene.String(required=True)
        description = graphene.String(required=True)
        created_at = graphene.DateTime(required=True)
        gym_id = graphene.Int(required=True)

    report = graphene.Field(Report)

    def mutate(self, info, description, issue, created_at, gym_id):
        # Check if gym exists
        gym = Gym.get_query(info).filter(GymModel.id == gym_id).first()
        if not gym:
            raise GraphQLError("Gym with given ID does not exist.")
        # Check if issue is a valid enumeration
        if issue not in [
            "INACCURATE_EQUIPMENT",
            "INCORRECT_HOURS",
            "INACCURATE_DESCRIPTION",
            "WAIT_TIMES_NOT_UPDATED",
            "OTHER",
        ]:
            raise GraphQLError("Issue is not a valid enumeration.")
        created_at_utc = ensure_utc(created_at)
        report = ReportModel(description=description, issue=issue, created_at=created_at_utc, gym_id=gym_id)
        db_session.add(report)
        db_session.commit()

        try:
            sh.worksheet(SHEET_REPORTS).append_row([report.id, issue, gym.name, description, created_at.isoformat()])
        except Exception as e:
            print(f"Error logging report to sheet: {e}")

        return CreateReport(report=report)


class DeleteReport(graphene.Mutation):
    class Arguments:
        report_id = graphene.Int(required=True)

    Output = Report

    def mutate(self, info, report_id):
        # Check if report exists
        report = Report.get_query(info).filter(ReportModel.id == report_id).first()
        if not report:
            raise GraphQLError("Report with given ID does not exist.")

        try:
            worksheet = sh.worksheet(SHEET_REPORTS)
            cell = worksheet.find(str(report_id), in_column=1)
            worksheet.delete_rows(cell.row)
        except Exception as e:
            print(f"Error deleting report from sheet: {e}")

        db_session.delete(report)
        db_session.commit()
        return report


class DeleteUserById(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    Output = User

    @jwt_required()
    def mutate(self, info, user_id):
        # Check if user exists
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        
        if not user:
            raise GraphQLError("User with given ID does not exist.")

        if int(get_jwt_identity()) != user_id:
            raise GraphQLError("Unauthorized operation")

        logging.info(f"DIGITAL_OCEAN_URL: {os.getenv('DIGITAL_OCEAN_URL')}")
        logging.info(f"User encoded_image: {user.encoded_image}")

        if user.encoded_image:
            try:
                logging.info("Attempting S3 delete...")
                s3 = boto3.client(
                    "s3",
                    endpoint_url=os.getenv("DIGITAL_OCEAN_URL"),
                    aws_access_key_id=os.getenv("DIGITAL_OCEAN_ACCESS"),
                    aws_secret_access_key=os.getenv("DIGITAL_OCEAN_SECRET_ACCESS"),
                    config=Config(s3={"addressing_style": "path"}),
                )
                s3.delete_object(
                    Bucket="appdev-upload",
                    Key=f"uplift-dev/user-profile/{user.net_id}-profile.png",
                )
                logging.info("S3 delete succeeded")
            except Exception as e:
                logging.error(f"S3 delete failed: {type(e).__name__}: {e}")
                raise GraphQLError(f"S3 error: {type(e).__name__}: {e}")

        db_session.delete(user)
        db_session.commit()
        return user


class CreateCapacityReminder(graphene.Mutation):
    class Arguments:
        fcm_token = graphene.String(required=True)
        gyms = graphene.List(graphene.String, required=True)
        days_of_week = graphene.List(graphene.String, required=True)
        capacity_percent = graphene.Int(required=True)

    Output = CapacityReminder

    def mutate(self, info, fcm_token, days_of_week, gyms, capacity_percent):
        if capacity_percent not in range(0, 91, 10):
            raise GraphQLError("Capacity percent must be an interval of 10 from 0-90.")

        # Validate days of the week
        validated_workout_days = []
        for day in days_of_week:
            try:
                validated_workout_days.append(DayOfWeekGraphQLEnum[day.upper()].value)
            except KeyError:
                raise GraphQLError(f"Invalid day of the week: {day}")

        # Validate gyms
        valid_gyms = []
        for gym in gyms:
            try:
                valid_gyms.append(CapacityReminderGymGraphQLEnum[gym].value)
            except KeyError:
                raise GraphQLError(f"Invalid gym: {gym}")

        # Subscribe to Firebase topics for each gym and day
        for gym in valid_gyms:
            for day in validated_workout_days:
                topic_name = f"{gym}_{day}_{capacity_percent}"
                try:
                    response = messaging.subscribe_to_topic(fcm_token, topic_name)
                    if response.success_count == 0:
                        raise Exception(response.errors[0].reason)
                except Exception as error:
                    raise GraphQLError(f"Error subscribing to topic for {topic_name}: {error}")

        reminder = CapacityReminderModel(
            fcm_token=fcm_token,
            gyms=valid_gyms,
            capacity_threshold=capacity_percent,
            days_of_week=validated_workout_days,
        )
        db_session.add(reminder)
        db_session.commit()

        return reminder


class EditCapacityReminder(graphene.Mutation):
    class Arguments:
        reminder_id = graphene.Int(required=True)
        new_gyms = graphene.List(graphene.String, required=True)
        days_of_week = graphene.List(graphene.String, required=True)
        new_capacity_threshold = graphene.Int(required=True)

    Output = CapacityReminder

    def mutate(self, info, reminder_id, new_gyms, days_of_week, new_capacity_threshold):
        reminder = db_session.query(CapacityReminderModel).filter_by(id=reminder_id).first()
        if not reminder:
            raise GraphQLError("CapacityReminder not found.")

        # Validate days of the week
        validated_workout_days = []
        for day in days_of_week:
            try:
                validated_workout_days.append(DayOfWeekGraphQLEnum[day.upper()].value)
            except KeyError:
                raise GraphQLError(f"Invalid day of the week: {day}")

        # Validate gyms
        new_valid_gyms = []
        for gym in new_gyms:
            try:
                new_valid_gyms.append(CapacityReminderGymGraphQLEnum[gym].value)
            except KeyError:
                raise GraphQLError(f"Invalid gym: {gym}")

        # Unsubscribe from old reminders
        topics = [
            f"{resolve_enum_value(gym)}_{resolve_enum_value(day)}_{reminder.capacity_threshold}"
            for gym in reminder.gyms
            for day in reminder.days_of_week
        ]

        for topic in topics:
            try:
                response = messaging.unsubscribe_from_topic(reminder.fcm_token, topic)
                logging.info("Unsubscribe %s from %s", reminder.fcm_token[:12], topic)
                for error in response.errors:
                    logging.warning(
                        "Error unsubscribing %s from %s -> reason: %s", reminder.fcm_token[:12], topic, error.reason
                    )
                if response.success_count == 0:
                    raise Exception(response.errors[0].reason)
            except Exception as error:
                raise GraphQLError(f"Error subscribing to topic: {error}")

        # Subscribe to new reminders
        topics = [f"{gym}_{day}_{new_capacity_threshold}" for gym in new_valid_gyms for day in validated_workout_days]

        for topic in topics:
            try:
                response = messaging.subscribe_to_topic(reminder.fcm_token, topic)
                logging.info("Resubscribing %s to %s", reminder.fcm_token[:12], topic)
                if response.success_count == 0:
                    raise Exception(response.errors[0].reason)
            except Exception as error:
                raise GraphQLError(f"Error subscribing to topic: {error}")

        reminder.gyms = new_valid_gyms
        reminder.days_of_week = validated_workout_days
        reminder.capacity_threshold = new_capacity_threshold

        db_session.commit()
        return reminder


class DeleteCapacityReminder(graphene.Mutation):
    class Arguments:
        reminder_id = graphene.Int(required=True)

    Output = CapacityReminder

    def mutate(self, info, reminder_id):
        reminder = db_session.query(CapacityReminderModel).filter_by(id=reminder_id).first()
        if not reminder:
            raise GraphQLError("CapacityReminder not found.")

        topics = [
            f"{resolve_enum_value(gym)}_{resolve_enum_value(day)}_{reminder.capacity_threshold}"
            for gym in reminder.gyms
            for day in reminder.days_of_week
        ]

        for topic in topics:
            try:
                response = messaging.unsubscribe_from_topic(reminder.fcm_token, topic)
                logging.info("Unsubscribe %s from %s", reminder.fcm_token[:12], topic)
                if response.success_count == 0:
                    raise Exception(response.errors[0].reason)
            except Exception as error:
                raise GraphQLError(f"Error unsubscribing from topic {topic}: {error}")

        db_session.delete(reminder)
        db_session.commit()

        return reminder


class AddFriend(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        friend_id = graphene.Int(required=True)

    Output = Friendship

    @jwt_required()
    def mutate(self, info, user_id, friend_id):
        # Check if users exist
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")

        friend = User.get_query(info).filter(UserModel.id == friend_id).first()
        if not friend:
            raise GraphQLError("Friend with given ID does not exist.")

        # Check if friendship already exists
        existing = (
            Friendship.get_query(info)
            .filter(
                ((FriendshipModel.user_id == user_id) & (FriendshipModel.friend_id == friend_id))
                | ((FriendshipModel.user_id == friend_id) & (FriendshipModel.friend_id == user_id))
            )
            .first()
        )

        if existing:
            raise GraphQLError("Friendship already exists.")

        # Create new friendship (not automatically accepted)
        friendship = FriendshipModel(user_id=user_id, friend_id=friend_id)
        db_session.add(friendship)
        db_session.commit()

        return friendship


class AcceptFriendRequest(graphene.Mutation):
    class Arguments:
        friendship_id = graphene.Int(required=True)

    Output = Friendship

    @jwt_required()
    def mutate(self, info, friendship_id):
        # Find the friendship
        friendship = Friendship.get_query(info).filter(FriendshipModel.id == friendship_id).first()
        if not friendship:
            raise GraphQLError("Friendship not found.")

        # Check if already accepted
        if friendship.is_accepted:
            raise GraphQLError("Friendship already accepted.")

        # Accept friendship
        friendship.is_accepted = True
        friendship.accepted_at = datetime.now(timezone.utc)
        db_session.commit()

        return friendship


class RemoveFriend(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        friend_id = graphene.Int(required=True)

    success = graphene.Boolean()

    @jwt_required()
    def mutate(self, info, user_id, friend_id):
        # Find the friendship
        friendship = (
            Friendship.get_query(info)
            .filter(
                ((FriendshipModel.user_id == user_id) & (FriendshipModel.friend_id == friend_id))
                | ((FriendshipModel.user_id == friend_id) & (FriendshipModel.friend_id == user_id))
            )
            .first()
        )

        if not friendship:
            raise GraphQLError("Friendship not found.")

        # Delete friendship
        db_session.delete(friendship)
        db_session.commit()

        return RemoveFriend(success=True)


class GetPendingFriendRequests(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    pending_requests = graphene.List(Friendship)

    @jwt_required()
    def mutate(self, info, user_id):
        # Check if user exists
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")

        # Get pending friend requests (where this user is the friend)
        pending = (
            Friendship.get_query(info)
            .filter((FriendshipModel.friend_id == user_id) & (FriendshipModel.is_accepted == False))
            .all()
        )

        return GetPendingFriendRequests(pending_requests=pending)


class Mutation(graphene.ObjectType):
    create_giveaway = CreateGiveaway.Field(description="Creates a new giveaway.")
    create_user = CreateUser.Field(description="Creates a new user.")
    edit_user = EditUserById.Field(description="Edit a new user by id.")
    enter_giveaway = EnterGiveaway.Field(description="Enters a user into a giveaway.")
    set_workout_goals = SetWorkoutGoals.Field(description="Set a user's workout goals.")
    log_workout = logWorkout.Field(description="Log a user's workout.")
    login_user = LoginUser.Field(description="Login a user.")
    logout_user = LogoutUser.Field(description="Logs out a user.")
    refresh_access_token = RefreshAccessToken.Field(description="Refreshes the access token.")
    create_report = CreateReport.Field(description="Creates a new report.")
    delete_report = DeleteReport.Field(description="Deletes a report by ID.")
    delete_user = DeleteUserById.Field(description="Deletes a user by ID.")
    add_friend = AddFriend.Field(description="Adds a friend to a user.")
    remove_friend = RemoveFriend.Field(description="Removes a friend from a user.")
    create_capacity_reminder = CreateCapacityReminder.Field(description="Create a new capacity reminder.")
    edit_capacity_reminder = EditCapacityReminder.Field(description="Edit capacity reminder.")
    delete_capacity_reminder = DeleteCapacityReminder.Field(description="Delete a capacity reminder")
    add_friend = AddFriend.Field(description="Send a friend request to another user.")
    accept_friend_request = AcceptFriendRequest.Field(description="Accept a friend request.")
    remove_friend = RemoveFriend.Field(description="Remove a friendship.")
    get_pending_friend_requests = GetPendingFriendRequests.Field(
        description="Get all pending friend requests for a user."
    )


schema = graphene.Schema(query=Query, mutation=Mutation)
