import sys
sys.path.append('..')
from src.database import db_session
from bs4 import BeautifulSoup
import requests
from src.models.facility import Facility, FacilityType
from src.models.openhours import OpenHours
from src.models.gym import Gym

BASE_URL_CENTERS = 'https://scl.cornell.edu/recreation/cornell-fitness-centers'
  
def create_openhours(times_set, name, begin_day, end_day):
  for time in times_set:
    times = time.strip().split('-')
    times = [t.strip() for t in times]

    # case when don't have start and end time
    if len(times) != 2:
      continue
    
    am_st = times[0].lower().find('am') != -1
    am_e = times[1].lower().find('am') != -1
    stime_loc = times[0].lower().find('am') if am_st else times[0].lower().find('pm')
    etime_loc = times[1].lower().find('am') if am_e else times[1].lower().find('pm')
    
    start = times[0][:stime_loc].strip()
    start = start + 'am' if am_st else start + 'pm'
    end = times[1][:etime_loc].strip()
    end = end + 'am' if am_e else end + 'pm'
    
    facility = db_session.query(Facility).filter(Facility.name == name).first()
    

    #put an open hour for each day: 1 = Monday, 2 = Tuesday, etc.
    for i in range(begin_day, end_day):
      try:
        hour = db_session.query(OpenHours).filter(OpenHours.facility_id==facility.id, OpenHours.day == i, OpenHours.start_time == start, OpenHours.end_time == end).first()
        assert hour is not None
      except AssertionError:
        hour = OpenHours(facility_id=facility.id, day=i, start_time=start, end_time=end)
        db_session.add(hour)
        db_session.commit()

def get_days(data):
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
        converted.append(converted[0])
      converted[-1] += 1
      day_set[i] = converted
  return day_set
  
def create_times(day_set, data):
  for row in data[1:]:
    row_data = row.find_all('td')
    name = row_data[0].text.strip()
    row_data= row_data[1:]

    k = 0
    for i in range(len(row_data)):
      colspan = 1
      if 'colspan' in row_data[i].attrs:
        colspan = row_data[i].attrs['colspan']
      
      begin_day = day_set[k][0]
      for j in range(colspan):
          end_day = day_set[k][1]
          k += 1
      times = row_data[i].text.strip().split('/')

      create_openhours(times, name, begin_day, end_day)

def scrape_times():
  page = requests.get(BASE_URL_CENTERS).text
  soup = BeautifulSoup(page, 'lxml')
  table = soup.find('table', class_='colored striped')
  data = table.find_all('tr')

  d_set = get_days(data)
  create_times(d_set, data)

  




  
    

    
    

    


    

