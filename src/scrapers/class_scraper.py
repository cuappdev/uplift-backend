from datetime import datetime
from src.database import db_session
from bs4 import BeautifulSoup
import requests
from src.utils.utils import get_gym_id
from src.utils.constants import GYMS, BASE_URL, CLASSES_PATH
from src.models.classes import Class, ClassInstance


"""
Create a group class from a class page
Params:
  class_href: href of class page from group-fitness-classes page
Returns:
    Class Object created
"""


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
  num_pages: number of pages to scrape - this determines how far in advance we scrape classes
Returns:
  dict of ClassInstance objects
"""


def fetch_classes(num_pages):
    classes = {}
    db_session.query(ClassInstance).delete()
    db_session.commit()
    for i in range(num_pages):
        try:
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
                class_href = row_elems[0].a["href"].replace("/recreation/", "", 1)
                try:
                    gym_class = db_session.query(Class).filter(Class.name == class_name).first()
                    if gym_class is None:
                        raise Exception("Gym class is none, creating new gym class")
                except Exception:
                    gym_class = create_group_class(class_href)

                if gym_class is None or not gym_class.id:
                    raise Exception(f"Failed to create or retrieve gym class from {BASE_URL + class_href}")

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
                        if class_instance.end_time < datetime.now():
                            continue
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
                    db_session.add(class_instance)
                    db_session.commit()
                    classes[class_instance.id] = class_instance
        except:
            print("Page is none.")
    return classes
