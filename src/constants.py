import json
from src.utils import generate_id, create_times
from src.models.gym import Gym
from src.models.facility import Facility, FacilityType
from src.models.openhours import OpenHours
from src.database import db_session

CONNECT2CONCEPTS_PATH = "https://connect2concepts.com/connect2/?type=circle&key=355de24d-d0e4-4262-ae97-bc0c78b92839"
RECTRAC_PATH = "https://rectrac.pe.cornell.edu/private/webtrac.wsc/history.html?historyoption=inquiry&_csrf_token=9e7d41b4de08bca17c1e7b304c9bae559c02e92712476c3dcb8d0b342f6afeac"
ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"

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
      gym["id"] = generate_id(gym["name"])
      gym["image_url"] = ASSET_BASE_URL + gym["image_url"]
      gyms.append(Gym(**gym))

      for facility in gym["facilities"]:
        facility["gym_id"] = gym["id"]
        facility_id_str = facility["type"] + facility["name"]
        facility["id"] = generate_id(facility_id_str)
        facility["facility_type"] = FacilityType[facility["type"]]
        facilities.append(Facility(**facility))

        for i, open_hrs in enumerate(facility["hours"]):
          hours_id_str = facility_id_str + str(i)
          fitness_hours += create_times(uid_str=hours_id_str,
                                         facility_id=facility["id"],
                                         **open_hrs)
  
  for gym in gyms:
    db_session.merge(gym)
  for facility in facilities:
    db_session.merge(facility)
  for hours in fitness_hours:
    db_session.merge(hours)
  db_session.commit()