from datetime import datetime
from src.database import db_session
import time as t
import datetime as dt
import random
from bs4 import BeautifulSoup
import re
import requests
# from src.constants import (
#     ASSET_BASE_URL,
#     GYMS_BY_ID,
# )
from src.utils.utils import get_gym_id
from src.utils.constants import GYMS
from src.models.classes import Class, ClassInstance
from src.models.openhours import OpenHours, RestrictionEnum, Restrictions, openhours_restrictions
from src.models.facility import Facility


BASE_URL = "https://scl.cornell.edu/recreation/"
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
    db_session.query(ClassInstance).delete()
    db_session.commit()
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

            time_str = row_elems[3].string.replace("\n", "").strip()
            if time_str != "" and time_str != 'Canceled':
                class_instance.is_canceled = False
                time_strs = time_str.split(" - ")
                start_time_string = time_strs[0].strip()
                end_time_string = time_strs[1].strip()

                class_instance.start_time = datetime.strptime(f"{date_string} {start_time_string}", "%m/%d/%Y %I:%M%p")
                class_instance.end_time = datetime.strptime(f"{date_string} {end_time_string}", "%m/%d/%Y %I:%M%p")
            else:
                class_instance.isCanceled = True

            try:
                class_instance.instructor = row_elems[4].a.string
            except:
                class_instance.instructor = ""
            try:
                location = row_elems[5].a.string
                class_instance.location = location
                for gym in GYMS:
                    if gym in location:
                        if gym == "Virtual":
                            class_instance.isVirtual = True
                        else:
                            gym_id = get_gym_id(gym)
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


# def scrape_pool_hours():
#     db_session.query(openhours_restrictions).delete()
#     db_session.query(OpenHours).delete()
#     page = requests.get(BASE_URL + POOL_HOURS_PATH).text
#     soup = BeautifulSoup(page, "lxml")
#     schedules = soup.find_all("table")
#     pool_hours = {}
#     for table in schedules:
#         rows = table.find_all("tr")
#         if len(rows) <= 1:
#             continue
#         for schedule in rows[1:]:
#             pool_name = schedule.find_all("td")[0].text.strip()
#             times = []
#             for td in schedule.find_all(
#                 lambda tag: tag.name == "td" and (len(tag.findChildren()) > 0 or len(tag.text) > 0)
#             )[1:]:
#                 day = re.findall(
#                     "(?:Women Only\s*)?(?:\d{1,2}:\d{2}(?:am|pm)) - (?:\d{1,2}:\d{2}(?:am|pm))(?:\s*\(shallow\))?|Closed",
#                     td.text,
#                 )
#                 non_empty_hours = []
#                 for interval in day:
#                     if interval:
#                         non_empty_hours.append(interval)
#                 times.append(non_empty_hours)
#             if pool_name.count("Helen Newman Hall") > 0:
#                 pool_name = "Helen Newman Pool"
#             if pool_name.count("Teagle") > 0:
#                 pool_name = "Teagle Pool"
#             if pool_name not in pool_hours:
#                 pool_hours[pool_name] = [[], [], [], [], [], [], []]
#             pool = db_session.query(Facility).filter_by(name=pool_name).first()
#             for i in range(len(times)):
#                 day = times[i]
#                 for time in day:
#                     time_text = time.strip()
#                     try:
#                         if "Closed" in time_text:
#                             openhour = OpenHours(**{"facility_id": pool.id, "day": i, "end_time": dt.time(0), "start_time": dt.time(0), "restrictions": []})
#                             closed_obj = db_session.query(Restrictions).filter_by(restriction='closed').first()
#                             openhour.restrictions.append(closed_obj)
#                             db_session.add(openhour)
#                             db_session.commit()
#                             pool_hours[pool_name][i].append(openhour)
#                         else:
#                             women_only = False
#                             shallow = False
#                             if "Women Only" in time:
#                                 women_only = True
#                                 time = time.replace("Women Only", "").strip()
#                             if "(shallow)" in time:
#                                 shallow = True
#                                 time = time.replace("(shallow)", "").strip()
#                             start_time_string, end_time_string = time.split(" - ")
#                             start_time = datetime.strptime(start_time_string, "%I:%M%p").time()
#                             end_time = datetime.strptime(end_time_string, "%I:%M%p").time()
#                             openhour = OpenHours(
#                                 **{"facility_id": pool.id, "day": i, "end_time": end_time, "start_time": start_time, "restrictions": []}
#                             )
#                             if women_only:
#                                 women_only_obj = db_session.query(Restrictions).filter_by(restriction='women_only').first()
#                                 openhour.restrictions.append(women_only_obj)
#                             if shallow:
#                                 shallow_obj = db_session.query(Restrictions).filter_by(restriction='shallow_pool_only').first()
#                                 openhour.restrictions.append(shallow_obj)
#                             db_session.add(openhour)
#                             db_session.commit()
#                             pool_hours[pool_name][i].append(openhour)
#                     except:
#                         pass
#     return pool_hours