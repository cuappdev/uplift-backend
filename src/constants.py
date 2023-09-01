import json
from src.utils import generate_id
from src.models.gym import Gym
from src.models.facility import Facility, FacilityType
from src.models.openhours import OpenHours
from src.database import db_session

"""
Helper function for generating a list of OpenHours from 
corresponding json object. 
"""
def _create_times(uid, facility_id, start, end, weekday):
  times = []
  day_range = range(0, 5) if weekday  else range(5, 7)
  for i in day_range:
    times.append(OpenHours(id=f"{uid}-{i}",
                           facility_id=facility_id,
                           day=i,
                           start_time=start,
                           end_time=end))
  return times

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
        facility["id"] = generate_id(facility["type"] + facility["name"])
        facility["facility_type"] = FacilityType[facility["type"]]
        facilities.append(Facility(**facility))
        for i, open_hrs in enumerate(facility["hours"]):
          hours_id = facility["id"] + str(i)
          fitness_hours += _create_times(uid=hours_id, 
                                         facility_id=facility["id"], 
                                         **open_hrs)
  
  for gym in gyms:
    db_session.merge(gym)
  for facility in facilities:
    db_session.merge(facility)
  for hours in fitness_hours:
    db_session.merge(hours)
  db_session.commit()