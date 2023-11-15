import graphene
from graphene import ObjectType
from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.capacity import Capacity as CapacityModel
from src.models.facility import Facility as FacilityModel
from src.models.gym import Gym as GymModel
from src.models.openhours import OpenHours as OpenHoursModel
from src.models.classes import Class as ClassModel
from src.models.classes import ClassInstance as ClassInstanceModel


# MARK: - Gym


class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel

    facilities = graphene.List(lambda: Facility)

    def resolve_facilities(self, info):
        query = Facility.get_query(info=info).filter(FacilityModel.gym_id == self.id)
        return query


# MARK: - Facility


class Facility(SQLAlchemyObjectType):
    class Meta:
        model = FacilityModel

    open_hours = graphene.List(lambda: OpenHours, name=graphene.String())
    capacity = graphene.Field(lambda: Capacity)

    def resolve_open_hours(self, info):
        query = OpenHours.get_query(info=info).filter(OpenHoursModel.facility_id == self.id)
        return query

    def resolve_capacity(self, info):
        query = (
            Capacity.get_query(info=info)
            .filter(CapacityModel.facility_id == self.id)
            .order_by(CapacityModel.updated.desc())
            .first()
        )
        return query


# MARK: - Classes


class Class(SQLAlchemyObjectType):
    class Meta:
        model = ClassModel


class ClassInstance(SQLAlchemyObjectType):
    class Meta:
        model = ClassInstanceModel


# MARK: - Open Hours


class OpenHours(SQLAlchemyObjectType):
    class Meta:
        model = OpenHoursModel


# MARK: - Capacity


class Capacity(SQLAlchemyObjectType):
    class Meta:
        model = CapacityModel


# MARK: - Query


class Query(graphene.ObjectType):
    gyms = graphene.List(Gym)

    def resolve_gyms(self, info):
        query = Gym.get_query(info)
        return query.all()


schema = graphene.Schema(query=Query)