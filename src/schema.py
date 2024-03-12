import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.capacity import Capacity as CapacityModel
from src.models.facility import Facility as FacilityModel
from src.models.gym import Gym as GymModel
from src.models.openhours import OpenHours as OpenHoursModel
from src.models.amenity import Amenity as AmenityModel
from src.models.equipment import Equipment as EquipmentModel
from src.models.user import User as UserModel
from src.models.giveaway import Giveaway as GiveawayModel


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

#MARK: - Giveaway
        
class Giveaway(SQLAlchemyObjectType):
    class Meta:
        model = GiveawayModel

    user_ids = graphene.List(lambda: User)

    def resolve_userids(self, info):
        query = User.get_query(info=info).filter(UserModel.giveaway_id == self.id)
        return query

# MARK: - Activity
# class Activity(SQLAlchemyObjectType):
#     class Meta:
#         model = ActivityModel

#     facilities = graphene.List(lambda: Facility)
        

# MARK: - Query


    #     user_data = UserInput(required=True)

    # user = graphene.Field(User)

    # def mutate(root, info, user_data=None):
    #     user = User(
    #         net_id=user_data.net_id,
    #         age=user_data.giveaway_id
    #     )
    #     return CreateUser(user=user)    


class Query(graphene.ObjectType):
    gyms = graphene.List(Gym)
    users_by_giveawayid = graphene.List(User, giveaway_id=graphene.Int(required=True))

    def resolve_gyms(self, info):
        query = Gym.get_query(info)
        return query.all()
    
    def resolve_users_by_giveawayid(self, giveaway_id, info):
        try:
            return User.objects.filter(giveaway_id=giveaway_id)
        except User.DoesNotExist:
            return None
        
        
#MARK: - Mutation

class createUser(graphene.Mutation):
    class Arguments:
        net_id = graphene.String()
        giveaway_id = graphene.Int()

    user = graphene.Field(lambda: User)

    def mutate(root, info, net_id, giveaway_id):
        user = User(net_id=net_id, giveaway_id=giveaway_id)
        user.save()
        return createUser(user=user)

class Mutation(graphene.ObjectType):
    createUser = createUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

