import requests
from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime
from src.database import db_session
from src.models.capacity import Capacity
from src.models.hourly_average_capacity import HourlyAverageCapacity
from src.models.enums import DayOfWeekEnum
from src.utils.messaging import send_capacity_reminder
from src.utils.constants import (
    C2C_URL,
    CAPACITY_MARKER_COUNTS,
    CAPACITY_MARKER_NAMES,
    CAPACITY_MARKER_UPDATED,
    CAPACITY_MARKER_PERCENT,
    CAPACITY_MARKER_PERCENT_NA,
)
from src.utils.utils import get_facility_id, unix_time


def fetch_capacities():
    """
    Fetch capacities for all facilities from Connect2Concepts.
    """
    global scrape_count, scrape_hour
    headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0"}
    html = requests.get(C2C_URL, headers=headers)
    soup = BeautifulSoup(html.text, "html.parser")
    data = soup.find_all("div", attrs={"class": "barChart"})

    # For each div element
    for facility_data in data:
        # Grab capacity data
        capacities = []
        for val in facility_data.get_text("\n").split("\n"):
            if val != "":
                capacities.append(val.strip())

        # Convert to named tuple
        CapacityData = namedtuple("CapacityData", ["name", "count", "updated", "percent"])
        capacity_data = CapacityData(*capacities)

        # Parse data
        facility_id = get_facility_id(CAPACITY_MARKER_NAMES[capacity_data.name])
        count = int(capacity_data.count.replace(CAPACITY_MARKER_COUNTS, ""))
        updated = get_capacity_datetime(capacity_data.updated.replace(CAPACITY_MARKER_UPDATED, ""))
        percent = (
            0.0
            if capacity_data.percent == CAPACITY_MARKER_PERCENT_NA
            else float(capacity_data.percent.replace(CAPACITY_MARKER_PERCENT, "")) / 100
        )

        target_gyms = [
            "HELENNEWMANFITNESSCENTER",
            "NOYESFITNESSCENTER",
            "TEAGLEDOWNFITNESSCENTER",
            "TEAGLEUPFITNESSCENTER",
            "TONIMORRISONFITNESSCENTER"
        ]

        last_percent = Capacity.query.filter_by(facility_id=facility_id).first()
        if last_percent:
            last_percent = last_percent.percent
        else:
            last_percent = 0

        topic_name = capacity_data.name.replace(" ", "").upper()

        if topic_name in target_gyms:
            check_and_send_capacity_reminders(topic_name, percent, last_percent)

        # Add to sheets
        add_single_capacity(count, facility_id, percent, updated)
        


def check_and_send_capacity_reminders(facility_name, current_percent, last_percent):
    """
    Check user reminders and send notifications to topic if the current capacity
    dips below the relevant thresholds.

    Parameters:
        - `facility_name`: The name of the facility.
        - `current_percent`: The current capacity percentage.
        - `last_percent`: The capacity percentage from the last scrape.
    """
    current_percent_int = int(current_percent * 100)  # Convert to integer percentage
    last_percent_int = int(last_percent * 100)

    current_day_name = datetime.now().strftime("%A").upper()
    
    # Check if the current percent crosses below any threshold from the last percent
    for percent in range(last_percent_int, current_percent_int - 1, -1):
        # print("last percent")
        # print(last_percent_int)
        # print("current percent")
        # print(current_percent_int)
        topic_name = f"{facility_name}_{current_day_name}_{percent}"
        # print(topic_name)
        send_capacity_reminder(topic_name, facility_name, current_percent)


# This function will run every hour to update hourly capacity
def update_hourly_capacity(curDay, curHour):
    """
    Update hourly average capacity every hour based on collected data.
    """
    currentCapacities = db_session.query(Capacity).all()

    for capacity in currentCapacities:
        try:
            hourly_average_capacity = db_session.query(HourlyAverageCapacity).filter(HourlyAverageCapacity.facility_id == capacity.facility_id, HourlyAverageCapacity.day_of_week == DayOfWeekEnum[curDay].value, HourlyAverageCapacity.hour_of_day == curHour).first()

            if hourly_average_capacity is not None:
                hourly_average_capacity.update_hourly_average(capacity.percent)
            else:
                print("No hourly capacity, creating new entry")
                hourly_average_capacity = HourlyAverageCapacity(
                    count=1,
                    facility_id=capacity.facility_id,
                    average_percent=capacity.percent,
                    hour_of_day=curHour,
                    day_of_week=DayOfWeekEnum[curDay].value,
                    history=[capacity.percent]
                )

            db_session.merge(hourly_average_capacity)
            db_session.commit()

        except Exception as e:
            print(f"Error updating hourly average: {e}")


def add_single_capacity(count, facility_id, percent, updated):
    """
    Add a single capacity to the database.

    Parameters:
        - `count`           The number of people in the facility.
        - `facility_id`     The ID of the facility this capacity belongs to.
        - `percent`         The percent filled between 0.0 and 1.0.
        - `updated`         The Unix time since this capacity was last updated.
    """
    # Convert datetime object to Unix
    updated_unix = unix_time(updated)

    # Clear old capacity and create a new one
    Capacity.query.filter_by(facility_id=facility_id).delete()
    capacity = Capacity(count=count, facility_id=facility_id, percent=percent, updated=updated_unix)

    # Save to database
    db_session.merge(capacity)
    db_session.commit()


def get_capacity_datetime(time_str):
    """
    Get a datetime object for a Capacity given a time string.

    Parameters:
        - `time_str`    The Eastern time string to parse in `%m/%d/%Y %I:%M %p`
                        format (ex: `12/18/2023 5:54 PM`).

    Returns:    a datetime object.
    """
    format = "%m/%d/%Y %I:%M %p"
    time_obj = datetime.strptime(time_str, format)
    return time_obj
