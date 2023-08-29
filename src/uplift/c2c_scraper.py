"""
Controller to scrap fitness website, parse html data, and add to Gym datatable.
Only works if flask app is running at the same time.
Used by cron job.

it is very possible there is a more succinct, efficient way to write this!
"""
from models.gym import Gym
from models.capacity import Capacity
from database import db_session
from sqlalchemy import and_

from bs4 import BeautifulSoup
from utils import parse_c2c_datetime
import requests

CONNECT2CONCEPTS_PATH = "https://connect2concepts.com/connect2/?type=circle&key=355de24d-d0e4-4262-ae97-bc0c78b92839"
RECTRAC_PATH = "https://rectrac.pe.cornell.edu/private/webtrac.wsc/history.html?historyoption=inquiry&_csrf_token=9e7d41b4de08bca17c1e7b304c9bae559c02e92712476c3dcb8d0b342f6afeac"


def scrape_capacity():
    """
    scrape capacity and timestamp and add to capacity model for corresponding gym
    """
    # Get data from C2C module
    headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0"}
    page = requests.get(CONNECT2CONCEPTS_PATH, headers=headers).text
    soup = BeautifulSoup(page, "lxml")
    data = soup.findAll("div", attrs={"class": "col-md-3 col-sm-6"})

    # For each section,
    # fitness center / open status / last count / updated (date time)
    for gymData in data:
        # separate gym data into lines divided by \n
        text = gymData.find("div", attrs={"style": "text-align:center;"})
        lines = text.get_text("\n").split("\n")

        # Fitness Center
        index = lines[0].find("Fitness Center")
        name = lines[0][0:index].strip()

        # Count
        index = lines[2].find(":")
        count = lines[2][index + 1 :].strip()

        # Last Updated
        index = lines[3].find(":")
        last_updated = lines[3][index + 1 :].strip()

        gym = Gym.query.filter_by(name=name).first()

        if gym:
            gym_id = gym.serialize().get("id")
            last_updated = parse_c2c_datetime(last_updated)

            # If it doesn't exist yet, add to table.
            if not (Capacity.query.filter(and_(Capacity.gym_id == gym_id, Capacity.updated == last_updated)).first()):
                new_count = Capacity(gym_id=gym_id, count=int(count), updated=last_updated)
                db_session.add(new_count)
                db_session.commit()


scrape_capacity()
