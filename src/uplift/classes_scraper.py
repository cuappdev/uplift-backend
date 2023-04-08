from models.gym import Gym 
from models.classes import Class, ClassTime 
from models.daytime import DayTime

from database import db_session
from sqlalchemy import and_

from bs4 import BeautifulSoup
from utils import parse_c2c_datetime
import requests

BASE_URL = "https://recreation.athletics.cornell.edu"
CLASSES_PATH = "/fitness-centers/group-fitness-classes?&page="
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
    Scrape classes given number of pages (??????????????)
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
            if class_href not in class_details:
                class_details = scrape_class_detail(class_href)

            # get cancelled status and time 
            div = row_elems[3].span.span
            cancelled = True
            if div is not None:
                cancelled = False
                start_time_string = row_elems[3].span.span.find_all("span")[0].string
                end_time_string = row_elems[3].span.span.find_all("span")[1].string

                start_time = datetime.strptime(start_time_string, "%I:%M%p").time()
                end_time = datetime.strptime(end_time_string, "%I:%M%p").time() 

                # Create new DayTime object 
                class_daytime = DayTime(
                    date = class_date, 
                    start_time = start_time, 
                    end_time = end_time,
                    special_hours = False 
                )
                db.session.add(class_daytime)

                daytime_id = class_daytime.serialize().get("id")


            # get gym instructor 
            try:
                instructor = row_elems[4].a.string
            except:
                instructor = ""


            # get location by finding gym object with same location 
            try:
                location = row_elems[5].a.string
                gym_query = Gym.query.filter( Gym.name.like(location) )

                if gym_query:
                    gym_id = gym.query.first().serialize().get("id")

            except:
                location = ""


            # get image url
            image_url = get_image_url(name)

            # Create new Class object 
            new_class = Class(
                name = class_details.get("name"),
                description = class_details.get("description"),
                gym_id = gym_id,
                location = location, 
                image_url = image_url
                instructor = instructor, 
                is_cancelled = cancelled
            )

            # Create new ClassTime object 
            class_id = new_class.serialize().get("id")

            new_classtime = ClassTime(
                daytime_id = daytime_id,
                class_id = class_id
            )
            
            db.session.add(new_class)
            db.session.add(new_classtime)
            db.session.commit()



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