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

type = FacilityType(name='Fitness Center')

def create_fitcenter_object(h_ref):
  page = requests.get(NEWMAN).text
  soup = BeautifulSoup(page, 'lxml')

  box = soup.find('article', id='main-article', class_='primary')
  facility_name = box.find('h1').get_text()

  facility = Facility(name=facility_name, facility_type=type.id)
  
  db_session.add(facility)
  db_session.commit()
  print(facility_name)
  return facility

def scrape_fitcenters():
  centers = {}
  page = requests.get(BASE_URL_CENTERS).text
  soup = BeautifulSoup(page, 'lxml')
  table = soup.find('table', class_='colored striped')
  data = table.find_all('tr')[1:]
  for row in data:
    row_eles = row.find_all('td')

    week_times = row_eles[1].text.strip()
    week_times = week_times.split('/')

    for time in week_times:
      time = time.strip()
      time = time.split('-')
      time = [t.strip() for t in time]

      

    
    wkend_time = row_eles[2].text


page = requests.get(BASE_URL_CENTERS).text
soup = BeautifulSoup(page, 'lxml')
table = soup.find('table', class_='colored striped')
data = table.find_all('tr')[1:]
time = []
for row in data:
  row_eles = row.find_all('td')
  name = row_eles[0].text.strip()
  print(row_eles[1].text)
  print(row_eles[2].text)

  #standard week times
  week_times = row_eles[1].text.strip()
  week_times = week_times.split('/')

  for time in week_times:
    time = time.strip()
    time = time.split('-')
    time = [t.strip() for t in time]

    # case when don't have start and end time
    if len(time) != 2:
      continue
    
    am = time[0].find('am') != -1
    stime_loc = time[0].lower().find('am') if am else time[0].lower().find('pm')
    etime_loc = time[1].lower().find('am') if am else time[1].lower().find('pm')
    
    start = time[0][:stime_loc].strip()
    start = start + 'am' if am else start + 'pm'
    end = time[1][:etime_loc].strip()
    end = end + 'am' if am else end + 'pm'
    
    #get facility id for specific fitness center
    gym = db_session.query(Gym).filter(Gym.name == name).first()
    # facilities = db_session.query(Facility).filter(Facility.gym_id == gym.id)
    #get facility id and check if 
    for i in range(1, 6):
      hour = OpenHours(day=i, start_time=start, end_time=end)
      # db_session.add(hour)
      # db_session.commit()

    
    

    


    

