import json
from src.utils import generate_id, create_times
from src.models.gym import Gym
from src.models.facility import Facility, FacilityType
from src.models.openhours import OpenHours
from src.database import db_session

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

    asset_base_url = constants["asset_base_url"]

    for gym in constants["default_gyms"]:      
      gym["id"] = generate_id(gym["name"])
      gym["image_url"] = asset_base_url + gym["image_url"]
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