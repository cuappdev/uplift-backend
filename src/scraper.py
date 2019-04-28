from datetime import datetime
import datetime as dt
import random

from bs4 import BeautifulSoup
import requests

import src.constants as constants
from src.schema import ClassDetailType, ClassType, DayTimeRangeType
from src.utils import generate_id

BASE_URL = 'https://recreation.athletics.cornell.edu'
CLASSES_PATH = '/fitness-centers/group-fitness-classes?&page='
SPECIAL_HOURS_PATH = '/hours-facilities/cornell-fitness-center-special-hours'

DAY_INDICES = {
  'Sunday': 0,
  'Monday': 1,
  'Tuesday': 2,
  'Wednesday': 3,
  'Thursday': 4,
  'Friday': 5,
  'Saturday': 6
}

"""
Scrape class detail from [class_href]
"""
def scrape_class_detail(class_href):
  class_detail = ClassDetailType()
  page = requests.get(BASE_URL + class_href).text
  soup = BeautifulSoup(page, 'lxml')
  contents = soup.find(
      'div',
      {'class': 'taxonomy-term-description'}
  ).p.contents

  name = soup.find(
      'div',
      {'id': 'main-body'}
  ).h1.contents[0]
  description = ''
  for c in contents:
    if isinstance(c, str):
      description += c
    else:
      try:
        description += c.string
      except:
        break

  class_detail.description = description
  class_detail.name = name
  class_detail.tags = constants.TAGS_BY_CLASS_NAME.get(name, [])
  class_detail.categories = constants.CATEGORIES_BY_CLASS_NAME.get(name, [])
  class_detail.id = generate_id(name)
  return class_detail

"""
Scrape classes from the group-fitness-classes page
Params:
  num_pages: number of pages to scrape
Returns:
  dict of ClassDetailType objects, list of ClassType objects
"""
def scrape_classes(num_pages):
  classes = {}
  class_details = {}

  for i in range(num_pages):
    page = requests.get(BASE_URL + CLASSES_PATH + str(i)).text
    soup = BeautifulSoup(page, 'lxml')
    if len(soup.find_all('table')) == 1:
      continue
    schedule = soup.find_all('table')[1]  # first table is irrelevant
    data = schedule.find_all('tr')[1:]  # first row is header

    for row in data:
      gym_class = ClassType()
      row_elems = row.find_all('td')
      date_string = row_elems[0].span.string
      gym_class.date = datetime.strptime(date_string, '%m/%d/%Y').date()

      class_href = row_elems[2].a['href']
      if class_href not in class_details:
        class_details[class_href] = scrape_class_detail(class_href)

      gym_class.details_id = class_details[class_href].id
      # special handling for time (cancelled)
      div = row_elems[3].span.span

      if div is not None:
        gym_class.is_cancelled = False
        start_time_string = row_elems[3].span.span.find_all('span')[0].string
        end_time_string = row_elems[3].span.span.find_all('span')[1].string

        gym_class.start_time = datetime.strptime(start_time_string, '%I:%M%p').time()
        gym_class.end_time = datetime.strptime(end_time_string, '%I:%M%p').time()
      else:
        gym_class.is_cancelled = True

      try:
        gym_class.instructor = row_elems[4].a.string
      except:
        gym_class.instructor = ''

      try:
        location = row_elems[5].a.string
        gym_class.location = location
        for gym_id, gym in constants.GYMS_BY_ID.items():
          if gym.name in location:
            gym_class.gym_id = gym_id
            break
      except:
        gym_class.location = ''

      gym_class.id = generate_id(gym_class.details_id + date_string + gym_class.instructor)
      gym_class.image_url = get_image_url(class_details[class_href].name)

      classes[gym_class.id] = gym_class

  return {detail.id: detail for detail in class_details.values()}, classes

"""
Return an image URL that contains keywords in the name of the class
Params:
  name: name of the class
Returns:
  a string of image URL
"""
def get_image_url(name):
  image_keyword = 'General'
  for keyword in constants.CLASS_IMAGE_KEYWORDS:
    if keyword in name:
      image_keyword = keyword
      break
  if image_keyword in constants.IMAGE_CHOICES:
    image_number = random.choice(range(1, constants.IMAGE_CHOICES[image_keyword] + 1))
    image_keyword = image_keyword + str(image_number)
  return constants.ASSET_BASE_URL + 'classes/' + image_keyword + '.jpg'

"""
Scrape special gym hours
Returns:
  dict mapping gym names to list of dicts each with a date and a DayTimeRangeType object

Example:
  { 'Helen Newman': [ {'date': '2/18', 'day': 1, 'hours': <DayTimeRangeType object>}, ...] }
"""
def scrape_special_hours():
  page = requests.get(BASE_URL + SPECIAL_HOURS_PATH).text
  soup = BeautifulSoup(page, 'lxml')
  schedules = soup.find_all('table')
  gym_hours = {}

  for table in schedules:
    rows = table.find_all('tr')
    if len(rows) <= 1:
      continue

    # First cell is blank
    header = rows[0].find_all('td')[1:]
    days_of_week = [day.find_all('p')[0].text.strip() for day in header]
    dates = [day.find_all('p')[1].text.strip() for day in header]

    for schedule in rows[1:]:
      gym_name = schedule.find_all('td')[0].text.strip()
      times = schedule.find_all('td')[1:]

      if gym_name not in gym_hours:
        gym_hours[gym_name] = []

      current_date_index = 0

      for time in times:
        time_text = time.text.strip().replace('Noon', '12:00p')

        # Number of consecutive days these hours are effective
        days = int(time.get('colspan', 1))

        if time_text == 'Closed':
          for i in range(days):
            day_of_week = days_of_week[current_date_index]
            gym_hours[gym_name].append({
              'date': dates[current_date_index],
              'hours': DayTimeRangeType(
                day=DAY_INDICES[day_of_week],
                start_time=dt.time(0),
                end_time=dt.time(0),
                special_hours=True
              )
            })
            current_date_index += 1
        else:
          mid_index = time_text.index('-')

          # The start and end times use 'a' or 'p' to indicate 'am' vs 'pm'
          start_time_string = time_text[0:mid_index] + 'm'
          end_time_string = time_text[mid_index + 1:] + 'm'

          start_time = datetime.strptime(start_time_string, '%I:%M%p').time()
          end_time = datetime.strptime(end_time_string, '%I:%M%p').time()

          for i in range(days):
            curr_date = dates[current_date_index]
            day_of_week = days_of_week[current_date_index]
            current_date_index += 1

            gym_hours[gym_name].append(
              {
                'date': curr_date,
                'hours': DayTimeRangeType(
                  day=DAY_INDICES[day_of_week],
                  start_time=start_time,
                  end_time=end_time,
                  special_hours=True
                )
              }
            )
  return gym_hours
