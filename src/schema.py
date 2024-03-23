import graphene
from graphene import Enum
from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.capacity import Capacity as CapacityModel
from src.models.facility import Facility as FacilityModel, FacilityType
from src.models.gym import Gym as GymModel
from src.models.openhours import OpenHours as OpenHoursModel
from src.models.amenity import Amenity as AmenityModel
from src.models.equipment import Equipment as EquipmentModel
from src.models.activity import Activity as ActivityModel, Gear as GearModel

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


# MARK: - Gear


class Gear(SQLAlchemyObjectType):
    class Meta:
        model = GearModel


# MARK: - Activity
        

class Activity(SQLAlchemyObjectType):
    class Meta:
        model = ActivityModel

    gear = graphene.List(lambda: Gear)

    def resolve_gear(self, info):
        query = Amenity.get_query(info=info).filter(GearModel.activity_id == self.id)
        return query


# MARK: - Query


class Query(graphene.ObjectType):
    gyms = graphene.List(Gym)
    activities = graphene.List(Activity)

    def resolve_gyms(self, info):
        query = Gym.get_query(info)
        return query.all()
    
    def resolve_activities(self, info):
        query = Activity.get_query(info)
        return query.all()


schema = graphene.Schema(query=Query)
