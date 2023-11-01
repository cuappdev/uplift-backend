import json
from src.utils import generate_id, create_times
from src.models.gym import Gym
from src.models.facility import Facility, FacilityType
from src.models.capacity import Capacity
from src.models.openhours import OpenHours
from src.database import db_session

ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"
CAPACITY_SCRAPE_PATH = "https://connect2concepts.com/connect2/?type=bar&key=355de24d-d0e4-4262-ae97-bc0c78b92839"
CAPACITY_SCRAPE_INTERVAL_MINUTES = 15

GYMS_BY_ID = {"Helen": 1, "Toni": 2, "Noyes": 3, "Teagle": 4, "Virtual": -1}

"""
Initialize basic information for all five fitness centers
(Helen Newman...Teagle Down) with location, hours, images. 
"""


def create_gym_table():
    gyms = []
    facilities = []
    fitness_hours = []

    with open("src/constants.json", "r") as constants_json:
        constants = json.load(constants_json)

        for gym in constants["default_gyms"]:
            gym["image_url"] = ASSET_BASE_URL + gym["image_url"]
            gyms.append(Gym(**gym))

            for facility in gym["facilities"]:
                facility["gym_id"] = gym["id"]
                facility_id_str = facility["type"] + facility["name"]
                facility["id"] = generate_id(facility_id_str)
                facility["facility_type"] = FacilityType[facility["type"]]
                facilities.append(Facility(**facility))


    for gym in gyms:
        db_session.merge(gym)
    for facility in facilities:
        db_session.merge(facility)
    db_session.commit()
