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
    TEAGLEUP = "TEAGLEUP"
    TEAGLEDOWN = "TEAGLEDOWN"
    HELENNEWMAN = "HELENNEWMAN"
    TONIMORRISON = "TONIMORRISON"
    NOYES = "NOYES"


class CapacityReminderGymGraphQLEnum(GrapheneEnum):
    TEAGLEUP = "TEAGLEUP"
    TEAGLEDOWN = "TEAGLEDOWN"
    HELENNEWMAN = "HELENNEWMAN"
    TONIMORRISON = "TONIMORRISON"
    NOYES = "NOYES"


class MuscleGroupEnum(enum.Enum):
    """Muscle groups a user can tag a saved workout with."""

    ARM = "ARM"
    LEG = "LEG"
    BACK = "BACK"
    CHEST = "CHEST"
    SHOULDER = "SHOULDER"
