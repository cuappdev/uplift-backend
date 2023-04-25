from models.gym import Gym 
from models.classes import Class, ClassTime 
from models.daytime import DayTime
from datetime import datetime

from database import db_session
from sqlalchemy import and_

from bs4 import BeautifulSoup
from utils import parse_c2c_datetime
import requests

BASE_URL = "https://recreation.athletics.cornell.edu"
CLASSES_PATH = "/fitness-centers/group-fitness-classes?&page="
ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"
CLASS_IMAGE_KEYWORDS = [
    "Abs",
    "Barre",
    "Chi",
    "Dance",
    "H.I.I.T",
    "OULA",
    "Pilates",
    "Pump",
    "ShockWave",
    "Spinning",
    "Strength",
    "TRX",
    "Yoga",
    "ZUMBA",
]
DAY_INDICES = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
PAGE_LIMIT = 10
CLASS_HISTORY_LIMIT = 4

def scrape_class_detail(class_href):
    """
    Scrape the name and class from a given class detail href page. 
    """

    page = requests.get(BASE_URL + class_href).text
    soup = BeautifulSoup(page, "lxml")
    try:
        contents = soup.find("div", {"class": "taxonomy-term-description"}).p.contents
    except AttributeError:
        contents = [""]

    name = soup.find("div", {"id": "main-body"}).h1.contents[0]
    description = ""
    for c in contents:
        if isinstance(c, str):
            description += c
        else:
            try:
                description += c.string
            except:
                break
    
    return {"name": name, "description" : description}


    
def scrape_classes(num_pages):
    """
    Scrape classes given number of pages.
    """
    for i in range(num_pages):
        page = requests.get(BASE_URL + CLASSES_PATH + str(i)).text
        soup = BeautifulSoup(page, "lxml")
        if len(soup.find_all("table")) == 1:
            continue
        schedule = soup.find_all("table")[1]  # first table is irrelevant
        data = schedule.find_all("tr")[1:]  # first row is header

        for row in data: 
            row_elems = row.find_all("td")
            date_string = row_elems[0].span.string

            class_date = datetime.strptime(date_string, "%m/%d/%Y").date()

            class_href = row_elems[2].a["href"]

            # get class name, description 
            class_details = scrape_class_detail(class_href)

            # get cancelled status and time 
            div = row_elems[3].span.span
            cancelled = True

            if div is not None:
                cancelled = False
                start_time_string = row_elems[3].span.span.find_all("span")[0].string
                end_time_string = row_elems[3].span.span.find_all("span")[1].string

                start_time = datetime.strptime(start_time_string, "%I:%M%p")
                end_time = datetime.strptime(end_time_string, "%I:%M%p")

                # Create new DayTime object 
                class_daytime = DayTime(
                    day = class_date, 
                    start_time = start_time, 
                    end_time = end_time,
                    special_hours = False 
                )
                db_session.add(class_daytime)
                db_session.commit()

            # get gym instructor 
            try:
                instructor = row_elems[4].a.string
            except:
                instructor = ""


            # get location by finding gym object with same location 
            location = row_elems[5].a.string
            gym_id = 0

            all_gyms = Gym.query.all()

            for gym in all_gyms:
                if gym.name in location:
                    gym_id = gym.id                 

            # get image url
            image_url = get_image_url(class_details.get("name"))

            # Create new Class object 
            new_class = Class(
                name = class_details.get("name"),
                description = class_details.get("description"),
                gym_id = gym_id,
                location = location, 
                image_url = image_url,
                instructor = instructor, 
                is_cancelled = cancelled
            )
            db_session.add(new_class)
            db_session.commit()

            # Create new ClassTime object 
            class_id = new_class.serialize().get("id")
            daytime_id = class_daytime.serialize().get("id")

            new_classtime = ClassTime(
                daytime_id = daytime_id,
                class_id = class_id
            )
            
            db_session.add(new_classtime)
            db_session.commit()

"""
Return an image URL that contains keywords in the name of the class
Params:
  name: name of the class
Returns:
  a string of image URL
"""

def get_image_url(name):
    image_keyword = "General"
    for keyword in CLASS_IMAGE_KEYWORDS:
        if keyword in name:
            image_keyword = keyword
            break
    
    return ASSET_BASE_URL + "classes/" + image_keyword + ".jpg"


"""
From class_metadata.csv
"""
def parse_class_metadata():
    tags = {}
    categories = {}
    with open("src/data/class_metadata.csv", "r") as metadata_file:
        reader = csv.reader(metadata_file)
        next(reader)
        for row in reader:
            class_name = row[0]
            tags[class_name] = [TAGS_BY_LABEL[label] for label in row[1].split(",")]
            categories[class_name] = row[2].split(",")
    return tags, categories