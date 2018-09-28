from datetime import datetime
import hashlib
import os

from bs4 import BeautifulSoup
from lxml import html
import requests

import constants
from schema import ClassDetailType, ClassType, DayTimeRangeType, GymType
from utils import generate_id

BASE_URL = 'https://recreation.athletics.cornell.edu'
CLASSES_PATH = '/fitness-centers/group-fitness-classes?&page='

'''
Scrape class detail from [class_href]
'''
def scrape_class(class_href):
  class_detail = ClassDetailType()
  page = requests.get(BASE_URL + class_href).text
  soup = BeautifulSoup(page, 'lxml')
  contents = soup.find(
      'div',
      {'class': 'taxonomy-term-description'}
  ).p.contents

  title = soup.find(
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
  class_detail.name = title
  class_detail.tags = constants.TAGS_BY_CLASS_NAME[title]
  class_detail.id = generate_id()
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
      gym_class = ClassType(id=generate_id())
      row_elems = row.find_all('td')
      date = row_elems[0].span.string

      class_href = row_elems[2].a['href']
      if class_href not in class_details:
        class_details[class_href] = scrape_class(class_href)

      gym_class.details_id = class_details[class_href].id
      # special handling for time (cancelled)
      div = row_elems[3].span.span

      if div is not None:
        gym_class.is_cancelled = False
        start_time = row_elems[3].span.span.find_all('span')[0].string
        end_time = row_elems[3].span.span.find_all('span')[1].string

        gym_class.start_time = datetime.strptime(date + ' ' + start_time, '%m/%d/%Y %I:%M%p')
        gym_class.end_time = datetime.strptime(date + ' ' + end_time, '%m/%d/%Y %I:%M%p')
      else:
        gym_class.is_cancelled = True

      try:
        gym_class.instructor = row_elems[4].a.string
      except:
        pass

      try:
        gym_class.location = row_elems[5].a.string
      except:
        pass

      classes[gym_class.id] = gym_class
  return {detail.id: detail for detail in class_details.values()}, classes
