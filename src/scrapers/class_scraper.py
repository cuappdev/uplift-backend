from datetime import datetime
from ..database import db_session

from bs4 import BeautifulSoup
import requests

from ..constants import (
    ASSET_BASE_URL,
    GYMS_BY_ID,
)
from ..models.classes import Class, ClassInstance

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
            if time_str != "" and "Canceled" not in time_str:
                class_instance.is_canceled = False
                time_strs = time_str.split(" - ")
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
