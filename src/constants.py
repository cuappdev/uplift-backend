from src.utils import generate_id
from src.models.gym import Gym
from src.models.facility import Facility, FacilityType
from src.models.openhours import OpenHours
from src.database import db_session

ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"

def _create_times(facility_id, start, end, weekday, id_base = None):
  uid = id_base if id_base is not None else facility_id
  times = []
  for i in (range(0, 5) if weekday  else range(5, 7)):
    times.append(OpenHours(id=f"{uid}-{i}",
                           facility_id=facility_id,
                           day=i,
                           start_time=start,
                           end_time=end,
                           special_hours=False))
  return times

"""
Initialize basic information for all five fitness centers
(Helen Newman...Teagle Down) with location, hours, images. 
"""
def create_gym_table():

  gyms = []
  facilities = []
  fitness_hours = []

  # MARK: - Helen Newman
  hn_id = generate_id("Helen Newman")
  hn_fitness_id = generate_id("Helen Newman Fitness")

  gyms.append(Gym(id=hn_id,
                  name='Helen Newman',
                  description='description', # TODO: - Add a description? or get rid
                  location='163 Cradit Farm Road',
                  latitude=42.453188923853595,
                  longitude=-76.47730907608567,
                  image_url=ASSET_BASE_URL + 'gyms/helen-newman.jpg'))

  facilities.append(Facility(id=hn_fitness_id,
                             name="Helen Newman",
                             gym_id=hn_id, 
                             facility_type=FacilityType.fitness))

  fitness_hours += _create_times(facility_id = hn_fitness_id,
                                 start=6,
                                 end=21,
                                 weekday=True)

  fitness_hours += _create_times(facility_id = hn_fitness_id,
                                 start=10,
                                 end=20,
                                 weekday=False)

  # MARK: - Toni Morrison
  tm_id = generate_id("Toni Morrison")
  tm_fitness_id = generate_id("Toni Morrison Fitness")

  gyms.append(Gym(id=tm_id,
                  name='Toni Morrison',
                  description='description', # TODO: - Add a description? or get rid
                  location='18 Sisson Pl',
                  latitude=42.45582093240726,
                  longitude=-76.47883902202813,
                  image_url=ASSET_BASE_URL + 'gyms/toni-morrison-outside-min.jpeg'))

  facilities.append(Facility(id=tm_fitness_id,
                             name="Toni Morrison",
                             gym_id=tm_id,
                             facility_type=FacilityType.fitness))

  fitness_hours += _create_times(facility_id = tm_fitness_id,
                                 start=14,
                                 end=23,
                                 weekday=True)

  fitness_hours += _create_times(facility_id = tm_fitness_id,
                                 start=12,
                                 end=22,
                                 weekday=False)

  # MARK: - Noyes
  ns_id = generate_id("Noyes")
  ns_fitness_id = generate_id("Noyes Fitness")

  gyms.append(Gym(id=ns_id,
                  name='Noyes',
                  description='description', # TODO: - Add a description? or get rid
                  location='306 West Ave',
                  latitude=42.44660528140398,
                  longitude=-76.48803891048553,
                  image_url=ASSET_BASE_URL + 'gyms/noyes.jpg'))
  
  facilities.append(Facility(id=ns_fitness_id,
                             name="Noyes",
                             gym_id=ns_id,
                             facility_type=FacilityType.fitness))

  fitness_hours += _create_times(facility_id = ns_fitness_id,
                                 start=7,
                                 end=23,
                                 weekday=True)

  fitness_hours += _create_times(facility_id = ns_fitness_id,
                                 start=14,
                                 end=22,
                                 weekday=False)

  # MARK: - Teagle (up and down)
  tgl_id = generate_id("Teagle")
  tu_fitness_id = generate_id("Teagle Up Fitness")
  td_fitness_id = generate_id("Teagle Down Fitness")

  gyms.append(Gym(id=tgl_id,
                  name='Teagle',
                  description='description', # TODO: - Add a description? or get rid
                  location='512 Campus Rd',
                  latitude=42.4459926380709,
                  longitude=-76.47915389837931,
                  image_url=ASSET_BASE_URL + 'gyms/teagle.jpg'))

  # Teagle Up
  facilities.append(Facility(id=tu_fitness_id,
                             name="Teagle Up",
                             gym_id=tgl_id,
                             facility_type=FacilityType.fitness))

  fitness_hours += _create_times(facility_id = tu_fitness_id,
                                 start=7,
                                 end=22.75,
                                 weekday=True)

  fitness_hours += _create_times(facility_id = tu_fitness_id,
                                 start=12,
                                 end=17.5,
                                 weekday=False)

  # Teagle Down
  facilities.append(Facility(id=td_fitness_id,
                             name="Teagle Down",
                             gym_id=tgl_id,
                             facility_type=FacilityType.fitness))

  fitness_hours += _create_times(facility_id = td_fitness_id,
                                 start=7,
                                 end=8.5,
                                 weekday=True,
                                 id_base=f"{td_fitness_id}-w0")

  fitness_hours += _create_times(facility_id = td_fitness_id,
                                 start=10,
                                 end=22.75,
                                 weekday=True,
                                 id_base=f"{td_fitness_id}-w1")

  fitness_hours += _create_times(facility_id = td_fitness_id,
                                 start=12,
                                 end=17.5,
                                 weekday=False)


  for gym in gyms:
    db_session.merge(gym)
  for facility in facilities:
    db_session.merge(facility)
  for hours in fitness_hours:
    db_session.merge(hours)
  db_session.commit()