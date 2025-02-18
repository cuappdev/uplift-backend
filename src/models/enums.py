import enum
from graphene import Enum as GrapheneEnum

# SQLAlchemy Enum
class DayOfWeekEnum(enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

# GraphQL Enum
class DayOfWeekGraphQLEnum(GrapheneEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

class CapacityReminderGym(enum.Enum):
    TEAGLEUP = "Teagle Up"
    TEAGLEDOWN = "Teagle Down"
    HELENNEWMAN = "Helen Newman"
    TONIMORRISON = "Toni Morrison"
    NOYES = "Noyes"

class CapacityReminderGymGraphQLEnum(GrapheneEnum):
    TEAGLEUP = "TEAGLEUP"
    TEAGLEDOWN = "TEAGLEDOWN"
    HELENNEWMAN = "HELENNEWMAN"
    TONIMORRISON = "TONIMORRISON"
    NOYES = "NOYES"
