import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.capacity import Capacity as CapacityModel
from src.models.facility import Facility as FacilityModel
from src.models.gym import Gym as GymModel
from src.models.openhours import OpenHours as OpenHoursModel
from src.models.amenity import Amenity as AmenityModel
from src.models.equipment import Equipment as EquipmentModel
from src.models.classes import Class as ClassModel
from src.models.classes import ClassInstance as ClassInstanceModel
from src.models.user import User as UserModel
from src.models.giveaway import Giveaway as GiveawayModel
from src.models.giveaway import GiveawayInstance as GiveawayInstanceModel
from src.database import db_session


# MARK: - Gym


class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel

    amenities = graphene.List(lambda: Amenity)
    facilities = graphene.List(lambda: Facility)
    hours = graphene.List(lambda: OpenHours)

    def resolve_amenities(self, info):
        query = Amenity.get_query(info=info).filter(AmenityModel.gym_id == self.id)
        return query

    def resolve_facilities(self, info):
        query = Facility.get_query(info=info).filter(FacilityModel.gym_id == self.id)
        return query

    def resolve_hours(self, info):
        query = OpenHours.get_query(info=info).filter(OpenHoursModel.gym_id == self.id)
        return query


# MARK: - Facility


class Facility(SQLAlchemyObjectType):
    class Meta:
        model = FacilityModel

    capacity = graphene.Field(lambda: Capacity)
    hours = graphene.List(lambda: OpenHours)
    equipment = graphene.List(lambda: Equipment)

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


# MARK: - User


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel


class UserInput(graphene.InputObjectType):
    net_id = graphene.String(required=True)
    giveaway_id = graphene.Int(required=True)


# MARK: - Giveaway


class Giveaway(SQLAlchemyObjectType):
    class Meta:
        model = GiveawayModel

    user_ids = graphene.List(lambda: User)

    def resolve_user_ids(self, info):
        query = User.get_query(info=info).filter(UserModel.giveaway_id == self.id)
        return query


# MARK: - Giveaway


class GiveawayInstance(SQLAlchemyObjectType):
    class Meta:
        model = GiveawayInstanceModel


# MARK: - Query


class Query(graphene.ObjectType):
    gyms = graphene.List(Gym)
    users_by_giveawayid = graphene.List(User, id=graphene.Int())

    def resolve_gyms(self, info):
        query = Gym.get_query(info)
        return query.all()


def resolve_users_by_giveaway_id(self, info, id):
    query = User.get_query(info).filter(UserModel.giveaway_ids.any(GiveawayInstance.giveaway_id == id))
    return query.all()


# MARK: - Mutation


class CreateUser(graphene.Mutation):
    class Arguments:
        net_id = graphene.String()

    user = graphene.Field(User)

    def mutate(root, info, net_id):
        # Check to see if NetID already exists
        existing_user = User.get_query(info).filter(UserModel.net_id == net_id).first()
        if existing_user:
            raise GraphQLError("NetID already exists.")

        # NetID does not exist
        new_user = UserModel(net_id=net_id)
        db_session.add(new_user)
        db_session.commit()
        return CreateUser(user=new_user)


class EnterGiveaway(graphene.Mutation):
    class Arguments:
        user_net_id = graphene.String(required=True)
        giveaway_id = graphene.Int(required=True)

    giveaway_instance = graphene.Field(GiveawayInstance)

    def mutate(self, info, user_net_id, giveaway_id):
        user = db_session.query(UserModel).filter_by(net_id=user_net_id).first()
        if not user:
            return EnterGiveaway(success=False, giveaway_instance=None)

        giveaway = db_session.query(GiveawayModel).get(giveaway_id)
        if not giveaway or any(instance.giveaway_id == giveaway_id for instance in user.giveaway_ids):
            return EnterGiveaway(success=False, giveaway_instance=None)

        giveaway_instance = GiveawayInstanceModel(user_id=user.id, giveaway_id=giveaway_id, numEntries=1)
        db_session.add(giveaway_instance)
        db_session.commit()
        return EnterGiveaway(success=True, giveaway_instance=giveaway_instance)


class Mutation(graphene.ObjectType):
    createUser = CreateUser.Field()
    enterGiveaway = EnterGiveaway.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
