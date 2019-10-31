import datetime as dt

from graphene import Field, ObjectType, String, List, Int, Boolean
from graphene.types.datetime import Date, Time


class Data(object):
    gyms = {}
    classes_by_date = {}
    class_details = {}

    @staticmethod
    def update_data(**kwargs):
        Data.gyms = kwargs.get("gyms")

        date_limit = dt.date.today() - dt.timedelta(days=kwargs.get("limit"))
        classes_by_date = Data.classes_by_date
        classes_data = kwargs.get("classes")
        for class_id, class_data in classes_data.items():
            if class_data.date in classes_by_date:
                classes_by_date[class_data.date][class_id] = class_data
            else:
                classes_by_date[class_data.date] = {class_id: class_data}
        classes_by_date = {date: classes_data for date, classes_data in classes_by_date.items() if date > date_limit}
        Data.classes_by_date = classes_by_date

        Data.class_details = kwargs.get("class_details")


class DayTimeRangeType(ObjectType):
    day = Int(required=True)
    end_time = Time(required=True)
    restrictions = String(default_value="", required=True)
    special_hours = Boolean(default_value=False, required=True)
    start_time = Time(required=True)


class TimeRangeType(ObjectType):
    end_time = Time(required=True)
    restrictions = String(default_value="", required=True)
    special_hours = Boolean(default_value=False, required=True)
    start_time = Time(required=True)


class DayTimeRangesType(ObjectType):
    day = Int(required=True)
    time_ranges = List(TimeRangeType, required=True)


class EquipmentType(ObjectType):
    equipment_type = String(required=True)
    name = String(required=True)
    quantity = String(default_value="1", required=True)
    workout_type = String(required=True)


# details types: Equipment, Hours, Images, Phone Numbers, Prices, Sub-Facilities
class FacilityDetailsType(ObjectType):
    details_type = String(required=True)
    equipment = List(EquipmentType, required=True)
    image_urls = List(String, required=True)
    items = List(String, required=True)
    prices = List(String, required=True)
    sub_facility_names = List(String, required=True)
    times = List(DayTimeRangesType, required=True)


class FacilityType(ObjectType):
    details = List(FacilityDetailsType, required=True)
    name = String(required=True)


class GymType(ObjectType):
    id = String(required=True)
    name = String(required=True)
    description = String(required=True)
    facilities = List(FacilityType, required=True)
    popular = List(List(Int))
    times = List(DayTimeRangeType, required=True)
    image_url = String()

    def is_open(self, day=None):
        return day is None or any([day == dt_range.day for dt_range in self.times])


class TagType(ObjectType):
    label = String(required=True)
    image_url = String(required=True)


class ClassDetailType(ObjectType):
    id = String(required=True)
    name = String(required=True)
    description = String(required=True)
    tags = List(TagType, required=True)
    categories = List(String, required=True)


class ClassType(ObjectType):
    id = String(required=True)
    gym_id = String()
    gym = Field(GymType)
    location = String(required=True)
    details_id = String(required=True)
    details = Field(ClassDetailType, required=True)
    date = Date(required=True)
    start_time = Time()
    end_time = Time()
    instructor = String(required=True)
    is_cancelled = Boolean(required=True)
    image_url = String(required=True)

    def resolve_gym(self, info):
        return Data.gyms.get(self.gym_id)

    def resolve_details(self, info):
        return Data.class_details.get(self.details_id)

    def filter(self, detail_ids=None, day=None, name=None, tags=None, gym_id=None, instructor=None):
        details = Data.class_details.get(self.details_id)
        return (
            (detail_ids is None or self.details_id in detail_ids)
            and (day is None or day == self.date)
            and (name is None or name in details.name)
            and (tags is None or any([tag in details.tags for tag in tags]))
            and (gym_id is None or gym_id == self.gym_id)
            and (instructor is None or instructor in self.instructor)
        )


class Query(ObjectType):
    gyms = List(GymType, day=Date(), gym_id=String(name="id"))
    classes = List(
        ClassType,
        detail_ids=List(String),
        day=Date(),
        name=String(),
        tags=List(String),
        gym_id=String(),
        instructor=String(),
    )

    def resolve_gyms(self, info, day=None, gym_id=None):
        if gym_id is not None:
            gym = Data.gyms.get(gym_id)
            return [gym] if gym is not None else []
        return [gym for gym in Data.gyms.values() if gym.is_open(day)]

    def resolve_classes(self, info, **kwargs):
        result = []
        for classes in Data.classes_by_date.values():
            for c in classes.values():
                if c.filter(**kwargs):
                    result.append(c)
        return result
