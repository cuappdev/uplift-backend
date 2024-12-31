import graphene
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from functools import wraps
from datetime import datetime, timedelta
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError
from src.models.enums import DayOfWeekGraphQLEnum, CapacityReminderGymGraphQLEnum
from src.models.capacity import Capacity as CapacityModel
from src.models.capacity_reminder import CapacityReminder as CapacityReminderModel
from src.models.workout_reminder import WorkoutReminder as WorkoutReminderModel
from src.models.facility import Facility as FacilityModel
from src.models.gym import Gym as GymModel
from src.models.openhours import OpenHours as OpenHoursModel
from src.models.amenity import Amenity as AmenityModel
from src.models.equipment import Equipment as EquipmentModel
from src.models.activity import Activity as ActivityModel, Price as PriceModel
from src.models.classes import Class as ClassModel
from src.models.classes import ClassInstance as ClassInstanceModel
from src.models.user import User as UserModel
from src.models.giveaway import Giveaway as GiveawayModel
from src.models.giveaway import GiveawayInstance as GiveawayInstanceModel
from src.models.workout import Workout as WorkoutModel
from src.models.hourly_average_capacity import HourlyAverageCapacity as HourlyAverageCapacityModel
from src.database import db_session
from firebase_admin import messaging


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)

    return decorated_function


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


# MARK: - Workout Reminder


class WorkoutReminder(SQLAlchemyObjectType):
    class Meta:
        model = WorkoutReminderModel


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


# MARK: - Giveaway


class Giveaway(SQLAlchemyObjectType):
    class Meta:
        model = GiveawayModel


# MARK: - Giveaway


class GiveawayInstance(SQLAlchemyObjectType):
    class Meta:
        model = GiveawayInstanceModel


# MARK: - Workout


class Workout(SQLAlchemyObjectType):
    class Meta:
        model = WorkoutModel


# MARK: - Hourly Average Capacity


class HourlyAverageCapacity(SQLAlchemyObjectType):
    class Meta:
        model = HourlyAverageCapacityModel

    day_of_week = graphene.Field(DayOfWeekGraphQLEnum)


# MARK: - Capacity Reminder


class CapacityReminder(SQLAlchemyObjectType):
    class Meta:
        model = CapacityReminderModel


# MARK: - Capacity Reminder


class WorkoutReminder(SQLAlchemyObjectType):
    class Meta:
        model = WorkoutReminderModel

    days_of_week = graphene.List(DayOfWeekGraphQLEnum)


# MARK: - Query


class Query(graphene.ObjectType):
    get_all_gyms = graphene.List(Gym, description="Get all gyms.")
    get_users_by_giveaway_id = graphene.List(User, id=graphene.Int(), description="Get all users given a giveaway ID.")
    get_user_by_net_id = graphene.List(User, net_id=graphene.String(), description="Get user by Net ID.")
    get_weekly_workout_days = graphene.List(
        graphene.String, id=graphene.Int(), description="Get the days a user worked out for the current week."
    )
    get_workouts_by_id = graphene.List(Workout, id=graphene.Int(), description="Get all of a user's workouts by ID.")
    get_average_hourly_capacities = graphene.List(
        HourlyAverageCapacity, facility_id=graphene.Int(), description="Get all facility hourly average capacities."
    )
    activities = graphene.List(Activity)

    def resolve_get_all_gyms(self, info):
        query = Gym.get_query(info)
        return query.all()

    def resolve_activities(self, info):
        query = Activity.get_query(info)
        return query.all()

    def resolve_get_average_hourly_capacities(self, info, facility_id):
        query = HourlyAverageCapacity.get_query(info).filter(HourlyAverageCapacityModel.facility_id == facility_id)
        return query.all()

    def resolve_get_users_by_giveaway_id(self, info, id):
        entries = GiveawayInstance.get_query(info).filter(GiveawayInstanceModel.giveaway_id == id).all()
        users = [User.get_query(info).filter(UserModel.id == entry.user_id).first() for entry in entries]
        return users

    def resolve_get_user_by_net_id(self, info, net_id):
        user = User.get_query(info).filter(UserModel.net_id == net_id).all()
        if not user:
            raise GraphQLError("User with the given Net ID does not exist.")
        return user

    @jwt_required
    def resolve_get_workouts_by_id(self, info, id):
        user = User.get_query(info).filter(UserModel.id == id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")
        workouts = Workout.get_query(info).filter(WorkoutModel.user_id == user.id).all()
        return workouts

    @jwt_required
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


# MARK: - Mutation


class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        net_id = graphene.String(required=True)
        email = graphene.String(required=True)
        fcm_token = graphene.String(required=True)

    Output = User

    def mutate(self, info, name, net_id, email, fcm_token):
        # Check if a user with the given NetID already exists
        existing_user = db_session.query(UserModel).filter(UserModel.net_id == net_id).first()
        if existing_user:
            raise GraphQLError("NetID already exists.")

        new_user = UserModel(name=name, net_id=net_id, email=email, fcm_token=fcm_token)
        db_session.add(new_user)
        db_session.commit()

        return new_user


class LoginUser(graphene.Mutation):
    class Arguments:
        net_id = graphene.String(required=True)

    token = graphene.String()

    def mutate(self, info, net_id):
        user = db_session.query(UserModel).filter(UserModel.net_id == net_id).first()
        if not user:
            return GraphQLError("No user with those credentials. Please create an account and try again.")

        # Generate JWT token
        token = create_access_token(identity=user.id)
        return LoginUser(token=token)


class EnterGiveaway(graphene.Mutation):
    class Arguments:
        user_net_id = graphene.String(required=True)
        giveaway_id = graphene.Int(required=True)

    Output = GiveawayInstance

    @jwt_required
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

    @jwt_required
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

    Output = Workout

    @jwt_required
    def mutate(self, info, workout_time, user_id):
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")

        workout = WorkoutModel(workout_time=workout_time, user_id=user.id)

        db_session.add(workout)
        db_session.commit()
        return workout


class CreateWorkoutReminder(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        reminder_time = graphene.Time(required=True)
        days_of_week = graphene.List(graphene.String, required=True)

    Output = WorkoutReminder

    def mutate(self, info, user_id, reminder_time, days_of_week):
        # Validate user existence
        user = db_session.query(UserModel).filter_by(id=user_id).first()
        if not user:
            raise GraphQLError("User not found.")

        # Validate days of the week
        validated_workout_days = []
        for day in days_of_week:
            try:
                validated_workout_days.append(DayOfWeekGraphQLEnum[day.upper()].value)
            except KeyError:
                raise GraphQLError(f"Invalid day of the week: {day}")

        try:
            reminder = WorkoutReminderModel(
                user_id=user_id, reminder_time=reminder_time, days_of_week=validated_workout_days
            )
            db_session.add(reminder)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise GraphQLError(f"Error creating workout reminder: {str(e)}")

        return reminder


class ToggleWorkoutReminder(graphene.Mutation):
    class Arguments:
        reminder_id = graphene.Int(required=True)

    Output = WorkoutReminder

    def mutate(self, info, reminder_id):
        reminder = db_session.query(WorkoutReminderModel).filter_by(id=reminder_id).first()
        if not reminder:
            raise GraphQLError("Workout reminder not found.")

        reminder.is_active = not reminder.is_active
        db_session.commit()

        return reminder


class DeleteWorkoutReminder(graphene.Mutation):
    class Arguments:
        reminder_id = graphene.Int(required=True)

    Output = WorkoutReminder

    def mutate(self, info, reminder_id):
        reminder = db_session.query(WorkoutReminderModel).filter_by(id=reminder_id).first()
        if not reminder:
            raise GraphQLError("Workout reminder not found.")

        db_session.delete(reminder)
        db_session.commit()

        return reminder


class CreateCapacityReminder(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        gyms = graphene.List(graphene.String, required=True)
        days_of_week = graphene.List(graphene.String, required=True)
        capacity_percent = graphene.Int(required=True)

    Output = CapacityReminder  # Use the renamed GraphQL type

    def mutate(self, info, user_id, days_of_week, gyms, capacity_percent):
        user = db_session.query(UserModel).filter_by(id=user_id).first()
        if not user:
            raise GraphQLError("User not found.")

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
                    messaging.subscribe_to_topic(user.fcm_token, topic_name)
                except Exception as error:
                    raise GraphQLError(f"Error subscribing to topic for {topic_name}: {error}")

        reminder = CapacityReminderModel(
            user_id=user_id,
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

        user = db_session.query(UserModel).filter_by(id=reminder.user_id).first()
        if not user:
            raise GraphQLError("User not found for this reminder.")

        # Prepare topics based on reminder's gym_id and days_of_week
        topics = [
            f"{gym}_{day}_{reminder.capacity_threshold}" for gym in reminder.gyms for day in reminder.days_of_week
        ]

        if reminder.is_active:
            # Toggle to inactive and unsubscribe
            for topic in topics:
                try:
                    messaging.unsubscribe_from_topic(user.fcm_token, topic)
                except Exception as error:
                    raise GraphQLError(f"Error unsubscribing from topic: {error}")
        else:
            # Toggle to active and resubscribe
            for topic in topics:
                try:
                    messaging.subscribe_to_topic(user.fcm_token, topic)
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

        user = db_session.query(UserModel).filter_by(id=reminder.user_id).first()
        if not user:
            raise GraphQLError("User not found for this reminder.")

        topics = [
            f"{gym}_{day}_{reminder.capacity_threshold}" for gym in reminder.gyms for day in reminder.days_of_week
        ]

        for topic in topics:
            try:
                messaging.unsubscribe_from_topic(user.fcm_token, topic)
            except Exception as error:
                raise GraphQLError(f"Error unsubscribing from topic {topic}: {error}")

        db_session.delete(reminder)
        db_session.commit()

        return reminder


class Mutation(graphene.ObjectType):
    create_giveaway = CreateGiveaway.Field(description="Creates a new giveaway.")
    create_user = CreateUser.Field(description="Creates a new user.")
    enter_giveaway = EnterGiveaway.Field(description="Enters a user into a giveaway.")
    set_workout_goals = SetWorkoutGoals.Field(description="Set a user's workout goals.")
    log_workout = logWorkout.Field(description="Log a user's workout.")
    login_user = LoginUser.Field(description="Login an existing user.")
    create_workout_reminder = CreateWorkoutReminder.Field(description="Create a new workout reminder.")
    toggle_workout_reminder = ToggleWorkoutReminder.Field(description="Toggle a workout reminder on or off.")
    delete_workout_reminder = DeleteWorkoutReminder.Field(description="Delete a workout reminder.")
    create_capacity_reminder = CreateCapacityReminder.Field(description="Create a new capacity reminder.")
    toggle_capacity_reminder = ToggleCapacityReminder.Field(description="Toggle a capacity reminder on or off.")
    delete_capacity_reminder = DeleteCapacityReminder.Field(description="Delete a capacity reminder")


schema = graphene.Schema(query=Query, mutation=Mutation)
