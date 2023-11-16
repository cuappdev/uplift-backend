import sys
sys.path.append('..')
from database import db_session
from bs4 import BeautifulSoup
import requests
from models.facility import Facility, FacilityType
from models.openhours import OpenHours
from models.gym import Gym

# BASE_URL = 'https://scl.cornell.edu/recreation'
BASE_URL_CENTERS = 'https://scl.cornell.edu/recreation/cornell-fitness-centers'
NEWMAN = 'https://scl.cornell.edu/recreation/facility/helen-newman-fitness-center'
result = requests.get(BASE_URL_CENTERS).text

 
def create_openhours(times_set, name, start_day, end_day):
  for time in times_set:
    times = time.strip().split('-')
    times = [t.strip() for t in times]

    # case when don't have start and end time
    if len(times) != 2:
      continue
    
    am = times[0].lower().find('am') != -1
    stime_loc = times[0].lower().find('am') if am else times[0].lower().find('pm')
    etime_loc = times[1].lower().find('am') if am else times[1].lower().find('pm')
    
    start = times[0][:stime_loc].strip()
    start = start + 'am' if am else start + 'pm'
    end = times[1][:etime_loc].strip()
    end = end + 'am' if am else end + 'pm'
    
    #get facility id for specific fitness center
    gym = db_session.query(Gym).filter(Gym.name == name).first()
    facility = db_session.query(Facility).filter(Facility.gym_id == gym.id).first()
    

    #put an open hour for each day: 1 = Monday, 2 = Tuesday, etc.
    for i in range(start_day, end_day):
      try:
        hour = db_session.query(OpenHours).filter(OpenHours.facility_id==facility.id, OpenHours.day == i, OpenHours.start_time == start, OpenHours.end_time == end).first()
        assert hour is not None
      except AssertionError:
        hour = OpenHours(facility_id=facility.id, day=i, start_time=start, end_time=end)
        db_session.add(hour)
        db_session.commit()

days_to_nums = {
  'monday': 1,
  'tuesday': 2,
  'wednesday': 3,
  'thursday': 4,
  'friday': 5,
  'saturday': 6,
  'sunday': 7, 
}  

#finding the days - (for break hours this is necessary)
def convert_days(data):
  day_set = data[0].find_all('th')[1:]
  day_set = [days.text.strip().split('-') for days in day_set]

  for i, days in enumerate(day_set):
    if days[0].lower() == 'weekdays':
      day_set[i] = [1, 6]
    elif days[0].lower() == 'weekend':
      day_set[i] = [6, 8]
    else:
      converted = []
      for day in days:
        converted.append(days_to_nums[day.strip().lower()])
      if len(converted == 1):
        converted.append(converted[0]+1)
      day_set[i] = converted

  return day_set

page = requests.get(BASE_URL_CENTERS).text
soup = BeautifulSoup(page, 'lxml')
table = soup.find('table', class_='colored striped')
data = table.find_all('tr')

day_set = convert_days(data)

for row in data[1:]:
  row_eles = row.find_all('td')
  name = row_eles[0].text.strip()

  for element in row_eles:
    if int(element.attr.colspan) > 1:
      

  for i in range(1, len(day_set)+1):
    times = row_eles[i].text.strip().split('/')
    create_openhours(times, name, day_set[i-1][0], day_set[i-1][1])




    
    

    


    

