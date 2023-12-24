import hashlib, json
from datetime import datetime as dt
from src.database import db_session
from src.models.gym import Gym
from src.models.facility import Facility, FacilityType
from src.models.amenity import Amenity, AmenityType
from src.utils.constants import ASSET_BASE_URL, FACILITY_ID_DICT, GYM_ID_DICT


def generate_id(data):
    return int.from_bytes(hashlib.sha256(data.encode("utf-8")).digest()[:3], "little")


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


def parse_time(time):
    return dt.strptime(time, "%Y-%m-%d, %H:%M")


def parse_datetime(datetime):
    return dt.strptime(datetime, "%Y-%m-%dT%H:%M:%S%z")


def parse_c2c_datetime(datetime):
    return dt.strptime(datetime, "%m/%d/%Y %I:%M %p")


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
            gym["id"] = GYM_ID_DICT[gym["id"]]
            gym["image_url"] = f"{ASSET_BASE_URL}{gym['image_url']}"
            gyms.append(Gym(**gym))

            # Add Facilities
            for facility in gym["facilities"]:
                facility["id"] = FACILITY_ID_DICT[facility["id"]]
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
