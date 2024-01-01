import hashlib, json, pytz, time
from datetime import datetime, timedelta
from src.database import db_session
from src.models.gym import Gym
from src.models.facility import Facility, FacilityType
from src.models.amenity import Amenity, AmenityType
from src.utils.constants import ASSET_BASE_URL, EASTERN_TIMEZONE


def generate_id(data):
    return int.from_bytes(hashlib.sha256(data.encode("utf-8")).digest()[:3], "little")


def unix_time(date):
    """
    Convert a datetime object to Unix time.

    Parameters:
        - `date`    The datetime object to convert from.
    """
    return time.mktime(date.timetuple())


def get_date_ranges(time_str):
    """
    Get datetime objects between the given time string.

    The first element is the start time. The last element is the end time.

    Parameters:
        - `time_str`    The time string to parse in `%m/%d/%y - %m/%d/%y` format
                        (ex: `12/27/23 - 12/31/23`).

    Returns:    a list of datetime objects with the first element as start time
                and last element as end time.
    """
    format = "%m/%d/%y"

    # Remove all spaces
    time_str = time_str.replace(" ", "")

    # Separate start and end time
    dash_pos = time_str.index("-")
    start_time_str = time_str[:dash_pos]
    end_time_str = time_str[dash_pos + 1 :]

    start_time = datetime.strptime(start_time_str, format)
    end_time = datetime.strptime(end_time_str, format)
    delta = end_time - start_time

    # Add dates in between
    result = []
    for i in range(delta.days + 1):
        day = start_time + timedelta(days=i)
        result.append(day)
    return result


def within_week(date):
    """
    Determine if a date is within 1 week.

    - Parameters:
        - `date`    The datetime object to check.

    - Returns:      True if the given date is within 1 week. False otherwise.
    """
    now = (
        datetime.now()
        .astimezone(pytz.timezone(EASTERN_TIMEZONE))  # In Eastern time
        .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    )
    return 0 <= (date - now).days < 7


def create_gym_table():
    """
    Initialize basic information for all gyms.
    """
    gyms = []
    facilities = []
    amenities = []

    with open("src/constants.json", "r") as json_file:
        json_gyms = json.load(json_file)

        # Add Gyms
        for gym in json_gyms:
            gym["id"] = generate_id(gym["name"])
            gym["image_url"] = f"{ASSET_BASE_URL}{gym['image_url']}"
            gyms.append(Gym(**gym))

            # Add Facilities
            for facility in gym["facilities"]:
                facility["id"] = generate_id(facility["name"])
                facility["gym_id"] = gym["id"]
                facility["facility_type"] = FacilityType[facility["type"]]
                facilities.append(Facility(**facility))

            # Add Amenities
            for amenity in gym["amenities"]:
                amenity["gym_id"] = gym["id"]
                amenity["type"] = AmenityType[amenity["type"]]
                amenities.append(Amenity(**amenity))

    # Add to database
    [db_session.merge(gym) for gym in gyms]
    [db_session.merge(facility) for facility in facilities]
    [db_session.merge(amenity) for amenity in amenities]
    db_session.commit()


def get_gym_id(name):
    """
    Retreive the ID of a gym.

    Parameters:
        - `name`    The name of the gym.

    Returns:    The ID of the gym.
    """
    gym = Gym.query.filter_by(name=name).first()
    return gym.id


def get_facility_id(name):
    """
    Retreive the ID of a facility.

    Parameters:
        - `name`    The name of the facility.

    Returns:    The ID of the facility.
    """
    facility = Facility.query.filter_by(name=name).first()
    return facility.id
