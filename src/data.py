from copy import deepcopy
from datetime import datetime
import threading
import src.constants as constants
import src.scraper as scraper
from src.schema import Data

def start_update():
  try:
    print('[{0}] Updating data'.format(datetime.now()))
    gyms = {gym.id: gym for gym in check_for_special_hours()}
    class_details, classes = scraper.scrape_classes(constants.PAGE_LIMIT)
    Data.update_data(gyms=gyms, classes=classes, class_details=class_details, limit=constants.CLASS_HISTORY_LIMIT)
  finally:
    threading.Timer(constants.UPDATE_DELAY, start_update).start()

"""
Check for special hours and update hours if applicable
Returns:
  list of GymType objects with special hours if applicable else uses regular hours
"""
def check_for_special_hours():
  now = datetime.now()
  current_date = '{0}/{1}'.format(now.month, now.day)
  try:
    special_hours = scraper.scrape_special_hours()
  except:
    special_hours = None

  # Deep copy so the regular gym times aren't modified
  gyms = deepcopy(constants.GYMS)

  if special_hours and any(special_hours):
    for gym in gyms:
      # Since we have both Teagle Up and Teagle Down
      if 'Teagle' in gym.name:
        times = special_hours['Teagle Hall']
      else:
        times = special_hours[gym.name]

      start_index = None
      for i in range(len(times)):
        if times[i]['date'] == current_date:
          start_index = i
          break

      if not start_index:
        # No special hours for gym
        continue

      end_index = min(start_index + 7, len(times))
      hours = [elt['hours'] for elt in times[start_index:end_index]]
      # Indices of days given by special hours
      days_covered = [elt.day for elt in hours]

      # Gym has mix of special and regular hours
      if len(days_covered) < 7:
        for reg_hours in gym.times:
          if reg_hours.day not in days_covered:
            hours.append(reg_hours)

      gym.times = sorted(hours, key=lambda hour: hour.day)

  return gyms

start_update()
