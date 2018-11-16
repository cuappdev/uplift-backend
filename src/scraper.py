from datetime import datetime
import hashlib
import os
import random

from bs4 import BeautifulSoup
from lxml import html
import requests

import src.constants as constants
from src.schema import ClassDetailType, ClassType, DayTimeRangeType, GymType
from src.utils import generate_id

BASE_URL = 'https://recreation.athletics.cornell.edu'
CLASSES_PATH = '/fitness-centers/group-fitness-classes?&page='

'''
Scrape class detail from [class_href]
'''
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

'''
Scrape classes from the group-fitness-classes page
Params:
  num_pages: number of pages to scrape
Returns:
  dict of ClassDetailType objects, list of ClassType objects
'''
def scrape_classes(num_pages):
  classes = {}
  class_details = {}

  for i in range(num_pages):
    page = requests.get(BASE_URL + CLASSES_PATH + str(i)).text
    soup = BeautifulSoup(page, 'lxml')
    schedule = soup.find_all('table')[1] # first table is irrelevant
    data = schedule.find_all('tr')[1:] # first row is header

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
    image_number = random.choice(range(1, constants.IMAGE_CHOICES[image_keyword]+1))
    image_keyword = image_keyword + str(image_number)
  return constants.ASSET_BASE_URL + 'classes/' + image_keyword + '.jpg'
