from datetime import datetime
from ..database import db_session
import time as t
import datetime as dt
import random

from bs4 import BeautifulSoup
import re
import requests

from ..constants import (
    ASSET_BASE_URL,
    GYMS_BY_ID,
)
from ..models.classes import Class, ClassInstance
from ..models.openhours import OpenHours
from ..models.facility import Facility

BASE_URL = "https://recreation.athletics.cornell.edu"
CLASSES_PATH = "/fitness-centers/group-fitness-classes?&page="
SPECIAL_HOURS_PATH = "/hours-facilities/cornell-fitness-center-special-hours"
POOL_HOURS_PATH = "/hours-facilities/pool-hours"


def create_group_class(class_href):
    page = requests.get(BASE_URL + class_href).text
    soup = BeautifulSoup(page, "lxml")
    container = soup.select_one("#main-article")
    name = container.select_one("h1").text
    try:
        contents = container.select("p")
    except AttributeError as e:
        print(e)
        contents = [""]

    description = ""
    for c in contents:
        if isinstance(c, str):
            description += c
        else:
            description += c.text
    model = Class(name=name, description=description)
    db_session.add(model)
    db_session.commit()
    return model


"""
Scrape classes from the group-fitness-classes page
Params:
  num_pages: number of pages to scrape
Returns:
  dict of ClassInstance objects
"""


def scrape_classes(num_pages):
    classes = {}

    for i in range(num_pages):
        page = requests.get(BASE_URL + CLASSES_PATH + str(i)).text
        soup = BeautifulSoup(page, "lxml")
        if len(soup.find_all("table")) == 1:
            continue
        schedule = soup.find_all("table")[1]  # first table is irrelevant
        data = schedule.find_all("tr")[1:]  # first row is header
        for row in data:
            row_elems = row.find_all("td")
            class_instance = ClassInstance()

            class_name = row_elems[0].a.text
            class_href = row_elems[0].a["href"]
            try:
                gym_class = db_session.query(Class).filter(Class.name == class_name).first()
                assert gym_class is not None
            except AssertionError:
                gym_class = create_group_class(class_href)
            class_instance.class_id = gym_class.id

            date_string = row_elems[1].text.strip()
            if "Today" in date_string:
                date_string = datetime.strftime(datetime.now(), "%m/%d/%Y")

            # special handling for time (cancelled)
            time_str = row_elems[3].string

            if time_str != "" or time_str.strip() != "Canceled":
                class_instance.is_canceled = False
                time_strs = time_str.split("-")
                start_time_string = time_strs[0].strip()
                end_time_string = time_strs[1].strip()

                class_instance.start_time = datetime.strptime(f"{date_string} {start_time_string}", "%m/%d/%Y %I:%M%p")
                class_instance.end_time = datetime.strptime(f"{date_string} {end_time_string}", "%m/%d/%Y %I:%M%p")
            else:
                class_instance.is_canceled = True

            try:
                class_instance.instructor = row_elems[4].a.string
            except:
                class_instance.instructor = ""

            try:
                location = row_elems[5].a.string
                class_instance.location = location
                for gym, gym_id in GYMS_BY_ID.items():
                    if gym in location:
                        if gym == "Virtual":
                            class_instance.isVirtual = True
                        else:
                            class_instance.gym_id = gym_id
                        break
            except:
                gym_class.location = ""

            # gym_class.id = generate_id(gym_class.details_id + date_string + gym_class.instructor)
            # gym_class.image_url = get_image_url(class_details[class_href].name)
            db_session.add(class_instance)
            db_session.commit()
            classes[class_instance.id] = class_instance

    return classes

def scrape_pool_hours(gyms):
    page = requests.get(BASE_URL + POOL_HOURS_PATH).text
    soup = BeautifulSoup(page, "lxml")
    schedules = soup.find_all("table")
    pool_hours = {}

    for table in schedules:
        rows = table.find_all("tr")
        if len(rows) <= 1:
            continue

        for schedule in rows[1:]:
            gym_name = schedule.find_all("td")[0].text.strip()
            times = []
            for td in schedule.find_all(
                lambda tag: tag.name == "td" and (len(tag.findChildren()) > 0 or len(tag.text) > 0)
            )[1:]:
                day = list(map(lambda match: match.group(), 
                               re.findall('((\d{1,2}:\d{2}(am|pm)) - (\d{1,2}:\d{2}(am|pm)))|Closed', td.text)))
                non_empty_hours = []
                for interval in day:
                    if interval:
                        non_empty_hours.append(interval)
                times.append(non_empty_hours)

            if gym_name.count("Helen Newman") > 0:
                gym_name = "Helen Newman"

            if gym_name.count("Teagle") > 0:
                gym_name = "Teagle Down"

            if gym_name not in pool_hours:
                pool_hours[gym_name] = [[], [], [], [], [], [], []]

            for i in range(len(times)):
                day = times[i]
                for time in day:
                    time_text = time.strip()
                    try:
                        if time_text == "Closed":
                            pool_hours[gym_name][i].append(OpenHours(end_time=dt.time(0), start_time=dt.time(0)))
                        else:
                            if "-" in time_text and "M" in time_text[time_text.index("-") + 1 :]:
                                dash_index = time_text.index("-")
                                start_time_string = time_text[0:dash_index].strip()
                                end_period_index = time_text[dash_index + 1 :].index("M")
                                end_time_string = time_text[dash_index + 1 :][: end_period_index + 1].strip()
                                restrictions = time_text[dash_index + 1 :][end_period_index + 1 :].strip()

                                if ":" not in start_time_string:
                                    if " AM" in start_time_string:
                                        start_time_string = start_time_string.replace(" AM", "") + ":00 AM"
                                    else:
                                        start_time_string += ":00"

                                if "AM" not in start_time_string and "PM" not in start_time_string:
                                    if "AM" in end_time_string:
                                        start_time_string += " AM"
                                    elif "PM" in end_time_string:
                                        start_time_string += " PM"

                                if ":" not in end_time_string:
                                    if " AM" in end_time_string:
                                        end_time_string = end_time_string.replace(" AM", "") + ":00 AM"
                                    elif " PM" in end_time_string:
                                        end_time_string = end_time_string.replace(" PM", "") + ":00 PM"

                                start_time = datetime.strptime(start_time_string, "%I:%M %p").time()
                                end_time = datetime.strptime(end_time_string, "%I:%M %p").time()

                                pool_hours[gym_name][i].append(
                                    TimeRangeType(end_time=end_time, restrictions=restrictions, start_time=start_time)
                                )
                    except:
                        pass
    return pool_hours