import datetime as dt
from socketserver import StreamRequestHandler
from xml.sax.handler import property_declaration_handler
from graphene import Field, ObjectType, String, List, Int, Boolean
from graphene.types.datetime import Date, Time
from models.gym import Gym as GymModel, GymTime as GymTimeModel
from models.daytime import DayTime as DayTimeModel
from models.activity import Activity as ActivityModel, ActivityPrice as ActivityPriceModel
from models.capacity import Capacity as CapacityModel
from models.activity import Amenity as AmenityModel
from models.price import Price as PriceModel
from models.facility import (
    Facility as FacilityModel,
    FacilityPrice as FacilityPriceModel,
    Equipment as EquipmentModel,
    FacilityTime as FacilityTimeModel,
)
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from sqlalchemy import desc


class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel

    times = graphene.List(
        lambda: DayTime,
        day=graphene.Int(),
        start_time=graphene.DateTime(),
        end_time=graphene.DateTime(),
        restrictions=graphene.String(),
        special_hours=graphene.Boolean(),
    )
    activities = graphene.List(lambda: Activity, name=graphene.String())
    facilities = graphene.List(lambda: Facility, gym_id=graphene.Int())
    capacities = graphene.List(lambda: Capacity, gym_id=graphene.Int())

    @staticmethod
    def resolve_times(self, info, day=None, start_time=None, end_time=None):
        query = GymTime.get_query(info=info)
        query = query.filter(GymTimeModel.gym_id == self.id)
        query_daytime = DayTime.get_query(info=info)  # could be wrong
        if day:
            query_daytime = query_daytime.filter(DayTimeModel.day == day)
        if start_time:
            query_daytime = query_daytime.filter(DayTimeModel.start_time == start_time)
        if end_time:
            query_daytime = query_daytime.filter(DayTimeModel.end_time == end_time)

        daytime_queries = []
        for row in query:
            daytime = query_daytime.filter(DayTimeModel.id == row.daytime_id)
            if daytime.first():
                daytime_queries.append(daytime[0])

        return daytime_queries

    def resolve_activities(self, info, name=None):
        query = Activity.get_query(info=info)
        activity_queries = []
        for act in self.activities:
            activity = query.filter(ActivityModel.id == act.id)
            if activity.first() and (name == act.name or name is None):
                activity_queries.append(activity[0])
        return activity_queries

    @staticmethod
    def resolve_capacities(self, info, gym_id=None):
        query = (
            Capacity.get_query(info=info).filter(CapacityModel.gym_id == self.id).order_by(desc(CapacityModel.updated))
        )

        return [query.first()]


class DayTime(SQLAlchemyObjectType):
    class Meta:
        model = DayTimeModel


class GymTime(SQLAlchemyObjectType):
    class Meta:
        model = GymTimeModel


class Activity(SQLAlchemyObjectType):
    class Meta:
        model = ActivityModel

    gyms = graphene.List(lambda: Gym, name=graphene.String())
    prices = graphene.List(lambda: Price, cost=graphene.Int(), one_time=graphene.Boolean())

    def resolve_gyms(self, info, name=None):
        query = Gym.get_query(info=info)
        gym_queries = []
        for g in self.gyms:
            gym = query.filter(GymModel.id == g.id)
            if gym.first() and (name == g.name or name == None):
                gym_queries.append(gym[0])

        return gym_queries

    @staticmethod
    def resolve_prices(self, info, name=None, cost=None):
        query = ActivityPrice.get_query(info=info)
        query = query.filter(ActivityPriceModel.activity_id == self.id)
        query_price = Price.get_query(info=info)

        if name:
            query_price = query_price.filter(PriceModel.name == name)
        if cost:
            query_price = query_price.filter(PriceModel.cost == cost)

        price_queries = []
        for row in query:
            price = query_price.filter(PriceModel.id == row.price_id)

            if price.first():
                price_queries.append(price[0])

        return price_queries


class Capacity(SQLAlchemyObjectType):
    class Meta:
        model = CapacityModel


class Price(SQLAlchemyObjectType):
    class Meta:
        model = PriceModel


class ActivityPrice(SQLAlchemyObjectType):
    class Meta:
        model = ActivityPriceModel


class Facility(SQLAlchemyObjectType):
    class Meta:
        model = FacilityModel

    @staticmethod
    def resolve_times(self, info, day=None, start_time=None, end_time=None):
        query = FacilityTime.get_query(info=info)
        query = query.filter(FacilityTimeModel.facilty_id == self.id)
        query_daytime = DayTime.get_query(info=info)

        if day:
            query_datytime = query_daytime.filter(DayTimeModel.day == day)
        if start_time:
            query_daytime = query_daytime.filter(DayTimeModel.start_time == start_time)
        if end_time:
            query_daytime = query_daytime.filter(DayTimeModel.end_time == end_time)

        daytime_queries = []
        for row in query:
            daytime = query_daytime.filter(DayTimeModel.id == row.daytime_id)
            if daytime.first():
                daytime_queries.append(daytime[0])

        return daytime_queries

    @staticmethod
    def resolve_price(self, info, name=None, cost=None):
        query = FacilityPrice.get_query(info=info)
        query = query.filter(FacilityPriceModel.facility_id == self.id)
        query_price = Price.get_query(info=info)

        if name:
            query_price = query_price.filter(PriceModel.name == name)
        if cost:
            query_price = query_price.filter(PriceModel.cost == cost)

        price_queries = []
        for row in query:
            price = query_price.filter(PriceModel.id == row.price_id)

            if price.first():
                price_queries.append(price[0])

        return price_queries


class TagType(ObjectType):
    label = String(required=True)
    image_url = String(required=True)


class FacilityTime(SQLAlchemyObjectType):
    class Meta:
        model = FacilityTimeModel


class FacilityPrice(SQLAlchemyObjectType):
    class Meta:
        model = FacilityPriceModel


class Equipment(SQLAlchemyObjectType):
    class Meta:
        model = EquipmentModel


class Amenity(SQLAlchemyObjectType):
    class Meta:
        model = AmenityModel


class Query(graphene.ObjectType):
    gyms = graphene.List(
        lambda: Gym,
        id=graphene.Int(),
        name=graphene.String(),
        description=graphene.String(),
        location=graphene.String(),
        latitude=graphene.Float(),
        longitude=graphene.Float(),
        image_url=graphene.String(),
    )

    def resolve_gyms(self, info, name=None):
        query = Gym.get_query(info)
        if name:
            query = query.filter(GymModel.name == name)
        return query.all()

    activities = graphene.List(
        lambda: Activity, name=graphene.String(), details=graphene.String(), image_url=graphene.String()
    )

    def resolve_activities(self, info, name=None):
        query = Activity.get_query(info)
        if name:
            query = query.filter(ActivityModel.name == name)
        return query.all()


schema = graphene.Schema(query=Query)
