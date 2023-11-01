
from datetime import datetime
from ..database import db_session

from bs4 import BeautifulSoup
import requests

from ..models.openhours import OpenHours, Restrictions, openhours_restrictions
from ..models.facility import Facility
import re

BASE_URL = "https://scl.cornell.edu/recreation/"
CLASSES_PATH = "/fitness-centers/group-fitness-classes?&page="
SPECIAL_HOURS_PATH = "/hours-facilities/cornell-fitness-center-special-hours"
POOL_HOURS_PATH = "/hours-facilities/pool-hours"

def scrape_pool_hours():
    db_session.query(openhours_restrictions).delete()
    db_session.query(OpenHours).delete()

    page = requests.get(BASE_URL + POOL_HOURS_PATH).text
    soup = BeautifulSoup(page, "lxml")
    schedules = soup.find_all("table")
    pool_hours = {}

    for table in schedules:
        rows = table.find_all("tr")
        if len(rows) <= 1:
            continue

        for schedule in rows[1:]:
            pool_name = schedule.find_all("td")[0].text.strip()
            times = []
            for td in schedule.find_all(
                lambda tag: tag.name == "td" and (len(tag.findChildren()) > 0 or len(tag.text) > 0)
            )[1:]:
                day = re.findall(
                    "(?:Women Only\s*)?(?:\d{1,2}:\d{2}(?:am|pm)) - (?:\d{1,2}:\d{2}(?:am|pm))(?:\s*\(shallow\))?|Closed",
                    td.text,
                )
                non_empty_hours = []
                for interval in day:
                    if interval:
                        non_empty_hours.append(interval)
                times.append(non_empty_hours)

            if pool_name.count("Helen Newman Hall") > 0:
                pool_name = "Helen Newman Pool"

            if pool_name.count("Teagle") > 0:
                pool_name = "Teagle Pool"

            if pool_name not in pool_hours:
                pool_hours[pool_name] = [[], [], [], [], [], [], []]
            pool = db_session.query(Facility).filter_by(name=pool_name).first()
            for i in range(len(times)):
                day = times[i]
                for time in day:
                    time_text = time.strip()
                    try:
                        if "Closed" in time_text:
                            openhour = OpenHours(**{"facility_id": pool.id, "day": i, "end_time": dt.time(0), "start_time": dt.time(0), "restrictions": []})
                            closed_obj = db_session.query(Restrictions).filter_by(restriction='closed').first()
                            openhour.restrictions.append(closed_obj)
                            db_session.add(openhour)
                            db_session.commit()
                            pool_hours[pool_name][i].append(openhour)
                        else:
                            women_only = False
                            shallow = False
                            if "Women Only" in time:
                                women_only = True
                                time = time.replace("Women Only", "").strip()
                            if "(shallow)" in time:
                                shallow = True
                                time = time.replace("(shallow)", "").strip()
                            start_time_string, end_time_string = time.split(" - ")
                            start_time = datetime.strptime(start_time_string, "%I:%M%p").time()
                            end_time = datetime.strptime(end_time_string, "%I:%M%p").time()

                            openhour = OpenHours(
                                **{"facility_id": pool.id, "day": i, "end_time": end_time, "start_time": start_time, "restrictions": []}
                            )
                            if women_only:
                                women_only_obj = db_session.query(Restrictions).filter_by(restriction='women_only').first()
                                openhour.restrictions.append(women_only_obj)
                            if shallow:
                                shallow_obj = db_session.query(Restrictions).filter_by(restriction='shallow_pool_only').first()
                                openhour.restrictions.append(shallow_obj)
                            db_session.add(openhour)
                            db_session.commit()
                            pool_hours[pool_name][i].append(openhour)
                    except:
                        pass
    return pool_hours
