import graphene
import os
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required
from functools import wraps
from datetime import datetime, timedelta, timezone
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
from src.models.enums import DayOfWeekGraphQLEnum, CapacityReminderGymGraphQLEnum
from src.models.giveaway import Giveaway as GiveawayModel
from src.models.giveaway import GiveawayInstance as GiveawayInstanceModel
from src.models.workout import Workout as WorkoutModel
from src.models.report import Report as ReportModel
from src.models.hourly_average_capacity import HourlyAverageCapacity as HourlyAverageCapacityModel
from src.database import db_session
import requests
import json
import os
from firebase_admin import messaging

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


# MARK: - User


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel

    workout_goal = graphene.List(DayOfWeekGraphQLEnum)


class UserInput(graphene.InputObjectType):
    net_id = graphene.String(required=True)
    giveaway_id = graphene.Int(required=True)


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


# MARK: - Report


class Report(SQLAlchemyObjectType):
    class Meta:
        model = ReportModel

    gym = graphene.Field(lambda: Gym)

    def resolve_gym(self, info):
        query = Gym.get_query(info).filter(GymModel.id == self.gym_id).first()
        return query

    
# MARK: - Capacity Reminder


class CapacityReminder(SQLAlchemyObjectType):
    class Meta:
        model = CapacityReminderModel


# MARK: - Query


class Query(graphene.ObjectType):
    get_all_gyms = graphene.List(Gym, description="Get all gyms.")
    get_user_by_net_id = graphene.List(User, net_id=graphene.String(), description="Get user by Net ID.")
    get_users_by_giveaway_id = graphene.List(User, id=graphene.Int(), description="Get all users given a giveaway ID.")
    get_weekly_workout_days = graphene.List(
        graphene.String, id=graphene.Int(), description="Get the days a user worked out for the current week."
    )
    get_workouts_by_id = graphene.List(Workout, id=graphene.Int(), description="Get all of a user's workouts by ID.")
    activities = graphene.List(Activity)
    get_all_reports = graphene.List(Report, description="Get all reports.")
    get_workout_goals = graphene.List(graphene.String, id=graphene.Int(required=True),
                                      description="Get the workout goals of a user by ID.")
    get_user_streak = graphene.Field(graphene.JSONString, id=graphene.Int(
        required=True), description="Get the current and max workout streak of a user.")
    get_hourly_average_capacities_by_facility_id = graphene.List(
        HourlyAverageCapacity, facility_id=graphene.Int(), description="Get all facility hourly average capacities."
    )

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

        # Get the date 7 days ago
        one_week_ago = datetime.utcnow() - timedelta(days=7)

        # Query distinct workout dates for the user in the past week. Workouts must never be logged for a future date.
        workout_days = (
            Workout.get_query(info)
            .filter(
                WorkoutModel.user_id == user.id, WorkoutModel.workout_time >= one_week_ago  # Use 'workout_time' here
            )
            .all()
        )

        # Extract days of the week from the workout times (use a set to avoid duplicates)
        workout_days_set = {workout.workout_time.strftime("%A") for workout in workout_days}

        return list(workout_days_set)

    def resolve_get_all_reports(self, info):
        query = ReportModel.query.all()
        return query

    @jwt_required()
    def resolve_get_workout_goals(self, info, id):
        user = User.get_query(info).filter(UserModel.id == id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")

        return [day.value for day in user.workout_goal] if user.workout_goal else []

    @jwt_required()
    def resolve_get_user_streak(self, info, id):
        user = User.get_query(info).filter(UserModel.id == id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")

        workouts = (
            Workout.get_query(info)
            .filter(WorkoutModel.user_id == user.id)
            .order_by(WorkoutModel.workout_time.desc())
            .all()
        )

        if not workouts:
            return {"active_streak": 0, "max_streak": 0}

        workout_dates = {workout.workout_time.date() for workout in workouts}
        sorted_dates = sorted(workout_dates, reverse=True)

        today = datetime.utcnow().date()
        active_streak = 0
        max_streak = 0
        streak = 0
        prev_date = None

        for date in sorted_dates:
            if prev_date and (prev_date - date).days > 1:
                max_streak = max(max_streak, streak)
                streak = 0

            streak += 1
            prev_date = date

            if date == today or (date == today - timedelta(days=1) and active_streak == 0):
                active_streak = streak

        max_streak = max(max_streak, streak)

        return {"active_streak": active_streak, "max_streak": max_streak}


    def resolve_get_hourly_average_capacities_by_facility_id(self, info, facility_id):
        valid_facility_ids = [14492437, 8500985, 7169406, 10055021, 2323580, 16099753, 15446768, 12572681]
        if facility_id not in valid_facility_ids:
            raise GraphQLError("Invalid facility ID.")
        query = HourlyAverageCapacity.get_query(info).filter(HourlyAverageCapacityModel.facility_id == facility_id)
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
        final_photo_url = None
        if existing_user:
            raise GraphQLError("NetID already exists.")

        if encoded_image:
            upload_url = os.getenv("DIGITAL_OCEAN_URL")
            payload = {
                "bucket": os.getenv("BUCKET_NAME"),
                "image": encoded_image  # Base64-encoded image string
            }
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(upload_url, json=payload, headers=headers)
                response.raise_for_status()
                json_response = response.json()
                final_photo_url = json_response.get("data")
                if not final_photo_url:
                    raise GraphQLError("No URL returned from upload service.")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                raise GraphQLError("Failed to upload photo.")

        new_user = UserModel(name=name, net_id=net_id, email=email, encoded_image=final_photo_url)
        db_session.add(new_user)
        db_session.commit()

        return new_user
    
class EditUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=False)
        net_id = graphene.String(required=True)
        email = graphene.String(required=False)
        encoded_image = graphene.String(required=False)

    Output = User

    def mutate(self, info, net_id, name=None, email=None, encoded_image=None):
        existing_user = db_session.query(UserModel).filter(UserModel.net_id == net_id).first()
        if not existing_user:
            raise GraphQLError("User with given net id does not exist.")
        
        if name is not None:
            existing_user.name = name
        if email is not None:
            existing_user.email = email
        if encoded_image is not None:
            upload_url = os.getenv("DIGITAL_OCEAN_URL")  # Base URL for upload endpoint
            if not upload_url:
                raise GraphQLError("Upload URL not configured.")

            payload = {
                "bucket": os.getenv("BUCKET_NAME", "DEV_BUCKET"),
                "image": encoded_image  # Base64-encoded image string
            }
            headers = {"Content-Type": "application/json"}
            
            print(f"Uploading image with payload: {payload}")
            
            try:
                response = requests.post(upload_url, json=payload, headers=headers)
                response.raise_for_status()
                json_response = response.json()
                print(f"Upload API response: {json_response}")
                final_photo_url = json_response.get("data")
                if not final_photo_url:
                    raise GraphQLError("No URL returned from upload service.")
                existing_user.encoded_image = final_photo_url
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                raise GraphQLError("Failed to upload photo.")

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


class SetWorkoutGoals(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True, description="The ID of the user.")
        workout_goal = graphene.List(
            graphene.String,
            required=True,
            description="The new workout goal for the user in terms of days of the week.",
        )

    Output = User

    @jwt_required()
    def mutate(self, info, user_id, workout_goal):
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")

        # Validate that all workout days are valid
        validated_workout_goal = []
        for day in workout_goal:
            try:
                # Convert string to enum
                validated_workout_goal.append(DayOfWeekGraphQLEnum[day.upper()].value)
            except KeyError:
                raise GraphQLError(f"Invalid day of the week: {day}")

        user.workout_goal = validated_workout_goal

        db_session.commit()

        return user


class logWorkout(graphene.Mutation):
    class Arguments:
        workout_time = graphene.DateTime(required=True)
        user_id = graphene.Int(required=True)
        facility_id = graphene.Int(required=True)

    Output = Workout

    @jwt_required()
    def mutate(self, info, workout_time, user_id):
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")
        facility = Facility.get_query(info).filter(FacilityModel.id == facility_id).first()
        if not facility:
            raise GraphQLError("Facility with given ID does not exist.")

        workout = WorkoutModel(workout_time=workout_time, user_id=user.id, facility_id=facility.id)

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
        report = ReportModel(description=description, issue=issue, created_at=created_at, gym_id=gym_id)
        db_session.add(report)
        db_session.commit()
        return CreateReport(report=report)


class DeleteUserById(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    Output = User

    def mutate(self, info, user_id):
        # Check if user exists
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")
        db_session.delete(user)
        db_session.commit()
        return user


class CreateCapacityReminder(graphene.Mutation):
    class Arguments:
        fcm_token = graphene.String(required=True)
        gyms = graphene.List(graphene.String, required=True)
        days_of_week = graphene.List(graphene.String, required=True)
        capacity_percent = graphene.Int(required=True)

    Output = CapacityReminder  # Use the renamed GraphQL type

    def mutate(self, info, fcm_token, days_of_week, gyms, capacity_percent):
        if capacity_percent < 0:
            raise GraphQLError("Capacity percent must be a non-negative integer.")

        # Validate days of the week
        validated_workout_days = []
        for day in days_of_week:
            try:
                validated_workout_days.append(DayOfWeekGraphQLEnum[day.upper()].value)
            except KeyError:
                raise GraphQLError(f"Invalid day of the week: {day}")

        # Validate gym existence
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
                    messaging.subscribe_to_topic(fcm_token, topic_name)
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
        print(reminder.gyms)

        return reminder


class ToggleCapacityReminder(graphene.Mutation):
    class Arguments:
        reminder_id = graphene.Int(required=True)

    Output = CapacityReminder

    def mutate(self, info, reminder_id):
        reminder = db_session.query(CapacityReminderModel).filter_by(id=reminder_id).first()
        if not reminder:
            raise GraphQLError("CapacityReminder not found.")

        # Prepare topics based on reminder's gym_id and days_of_week
        topics = [
            f"{gym}_{day}_{reminder.capacity_threshold}" for gym in reminder.gyms for day in reminder.days_of_week
        ]

        if reminder.is_active:
            # Toggle to inactive and unsubscribe
            for topic in topics:
                try:
                    messaging.unsubscribe_from_topic(reminder.fcm_token, topic)
                except Exception as error:
                    raise GraphQLError(f"Error unsubscribing from topic: {error}")
        else:
            # Toggle to active and resubscribe
            for topic in topics:
                try:
                    messaging.subscribe_to_topic(reminder.fcm_token, topic)
                except Exception as error:
                    raise GraphQLError(f"Error subscribing to topic: {error}")

        reminder.is_active = not reminder.is_active
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
            f"{gym}_{day}_{reminder.capacity_threshold}" for gym in reminder.gyms for day in reminder.days_of_week
        ]

        for topic in topics:
            try:
                messaging.unsubscribe_from_topic(reminder.fcm_token, topic)
            except Exception as error:
                raise GraphQLError(f"Error unsubscribing from topic {topic}: {error}")

        db_session.delete(reminder)
        db_session.commit()

        return reminder


class Mutation(graphene.ObjectType):
    create_giveaway = CreateGiveaway.Field(description="Creates a new giveaway.")
    create_user = CreateUser.Field(description="Creates a new user.")
    edit_user = EditUser.Field(description="Edit a new user.")
    enter_giveaway = EnterGiveaway.Field(description="Enters a user into a giveaway.")
    set_workout_goals = SetWorkoutGoals.Field(description="Set a user's workout goals.")
    log_workout = logWorkout.Field(description="Log a user's workout.")
    login_user = LoginUser.Field(description="Login a user.")
    logout_user = LogoutUser.Field(description="Logs out a user.")
    refresh_access_token = RefreshAccessToken.Field(description="Refreshes the access token.")
    create_report = CreateReport.Field(description="Creates a new report.")
    delete_user = DeleteUserById.Field(description="Deletes a user by ID.")
    create_capacity_reminder = CreateCapacityReminder.Field(description="Create a new capacity reminder.")
    toggle_capacity_reminder = ToggleCapacityReminder.Field(description="Toggle a capacity reminder on or off.")
    delete_capacity_reminder = DeleteCapacityReminder.Field(description="Delete a capacity reminder")


schema = graphene.Schema(query=Query, mutation=Mutation)
