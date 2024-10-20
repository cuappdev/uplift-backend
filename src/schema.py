import graphene
from src.models.enums import DayOfWeekGraphQLEnum
from datetime import datetime, timedelta
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError
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
from src.database import db_session


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


# MARK: - Capacity Reminder


class CapacityReminder(SQLAlchemyObjectType):
    class Meta:
        model = CapacityReminderModel


# MARK: - Capacity Reminder


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


# MARK: - Query


class Query(graphene.ObjectType):
    get_all_gyms = graphene.List(Gym, description="Get all gyms.")
    get_users_by_giveaway_id = graphene.List(User, id=graphene.Int(), description="Get all users given a giveaway ID.")
    get_weekly_workout_days = graphene.List(
        graphene.String, id=graphene.Int(), description="Get the days a user worked out for the current week."
    )
    get_workouts_by_id = graphene.List(Workout, id=graphene.Int(), description="Get all of a user's workouts by ID.")
    activities = graphene.List(Activity)

    def resolve_get_all_gyms(self, info):
        query = Gym.get_query(info)
        return query.all()

    def resolve_activities(self, info):
        query = Activity.get_query(info)
        return query.all()

    def resolve_get_users_by_giveaway_id(self, info, id):
        entries = GiveawayInstance.get_query(info).filter(GiveawayInstanceModel.giveaway_id == id).all()
        users = [User.get_query(info).filter(UserModel.id == entry.user_id).first() for entry in entries]
        return users

    def resolve_get_workouts_by_id(self, info, id):
        user = User.get_query(info).filter(UserModel.id == id).first()
        if not user:
            raise GraphQLError("User with the given ID does not exist.")
        workouts = Workout.get_query(info).filter(WorkoutModel.user_id == user.id).all()
        return workouts

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

    Output = User

    def mutate(self, info, name, net_id, email):
        # Check if a user with the given NetID already exists
        existing_user = db_session.query(UserModel).filter(UserModel.net_id == net_id).first()
        if existing_user:
            raise GraphQLError("NetID already exists.")

        new_user = UserModel(name=name, net_id=net_id, email=email)
        db_session.add(new_user)
        db_session.commit()

        return new_user


class EnterGiveaway(graphene.Mutation):
    class Arguments:
        user_net_id = graphene.String(required=True)
        giveaway_id = graphene.Int(required=True)

    Output = GiveawayInstance

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

    def mutate(self, info, workout_time, user_id):
        user = User.get_query(info).filter(UserModel.id == user_id).first()
        if not user:
            raise GraphQLError("User with given ID does not exist.")

        workout = WorkoutModel(workout_time=workout_time, user_id=user.id)

        db_session.add(workout)
        db_session.commit()
        return workout


class Mutation(graphene.ObjectType):
    create_giveaway = CreateGiveaway.Field(description="Creates a new giveaway.")
    create_user = CreateUser.Field(description="Creates a new user.")
    enter_giveaway = EnterGiveaway.Field(description="Enters a user into a giveaway.")
    set_workout_goals = SetWorkoutGoals.Field(description="Set a user's workout goals.")
    log_workout = logWorkout.Field(description="Log a user's workout.")


schema = graphene.Schema(query=Query, mutation=Mutation)
