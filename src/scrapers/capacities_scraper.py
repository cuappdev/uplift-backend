import requests
import time
from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime
from src.database import db_session
from src.utils.messaging import send_capacity_reminder
from src.models.capacity import Capacity
from src.models.hourly_average_capacity import HourlyAverageCapacity
from src.models.facility import Facility
from src.models.enums import DayOfWeekEnum, CapacityReminderGym
from src.utils.constants import (
    C2C_URL,
    CRC_URL_NEW,
    CAPACITY_MARKER_COUNTS,
    CAPACITY_MARKER_NAMES,
    CAPACITY_MARKER_UPDATED,
    CAPACITY_MARKER_PERCENT,
    CAPACITY_MARKER_PERCENT_NA,
)
from src.utils.utils import get_facility_id, unix_time

# Legacy scraper from old webpage using CRC_URL
def fetch_capacities_old():
    """
    Fetch capacities for all facilities from Connect2Concepts.
    """
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

        # Add to sheets
        add_single_capacity(count, facility_id, percent, updated)


# New scraper from new API using CRC_URL_NEW
def fetch_capacities():
    """Fetch capacities from the new JSON API endpoint."""
    try:
        headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0"}

        response = requests.get(CRC_URL_NEW, headers=headers)
        facilities = response.json()

        for facility in facilities:
            try:
                facility_name = facility["LocationName"]

                # Map API name to database name
                if facility_name not in CAPACITY_MARKER_NAMES:
                    print(f"Warning: No name mapping for facility: {facility_name}")
                    continue

                db_name = CAPACITY_MARKER_NAMES[facility_name]
                facility_id = get_facility_id(db_name)

                count = int(facility["LastCount"])
                updated_str = facility["LastUpdatedDateAndTime"]
                total_capacity = int(facility["TotalCapacity"])

                percent = count / total_capacity if total_capacity > 0 else 0.0
                updated = datetime.strptime(updated_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")

                gym_mapping = {
                    "HNH Fitness Center": CapacityReminderGym.HELENNEWMAN,
                    "Noyes Fitness Center": CapacityReminderGym.NOYES,
                    "Teagle Down Fitness Center": CapacityReminderGym.TEAGLEDOWN,
                    "Teagle Up Fitness Center": CapacityReminderGym.TEAGLEUP,
                    "Morrison Fitness Center": CapacityReminderGym.TONIMORRISON,
                }

                last_capacity = Capacity.query.filter_by(facility_id=facility_id).first()
                last_percent = last_capacity.percent if last_capacity else 0

                if db_name in gym_mapping:
                    # Check if facility is closed
                    facility = Facility.query.filter_by(id=facility_id).first()

                    if not facility or not facility.hours:
                        print(f"Warning: No hours found for facility ID {facility_id}")
                        continue

                    current_time = int(time.time())

                    is_open = any(hour.start_time <= current_time <= hour.end_time for hour in facility.hours)

                    if is_open:
                        topic_enum = gym_mapping[db_name]
                        check_and_send_capacity_reminders(topic_enum.name, db_name, percent, last_percent)

                add_single_capacity(count, facility_id, percent, updated)

            except Exception as e:
                print(f"Error processing facility {facility.get('LocationName', 'unknown')}: {str(e)}")

    except Exception as e:
        print(f"Error fetching capacities: {str(e)}")
        raise


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


def update_hourly_capacity(curDay, curHour):
    """
    Update hourly average capacity every hour based on collected data.
    """
    currentCapacities = db_session.query(Capacity).all()

    for capacity in currentCapacities:
        try:
            hourly_average_capacity = (
                db_session.query(HourlyAverageCapacity)
                .filter(
                    HourlyAverageCapacity.facility_id == capacity.facility_id,
                    HourlyAverageCapacity.day_of_week == DayOfWeekEnum[curDay].value,
                    HourlyAverageCapacity.hour_of_day == curHour,
                )
                .first()
            )

            if hourly_average_capacity is not None:
                print("updating average")
                hourly_average_capacity.update_hourly_average(capacity.percent)
            else:
                print("No hourly capacity, creating new entry")
                hourly_average_capacity = HourlyAverageCapacity(
                    facility_id=capacity.facility_id,
                    average_percent=capacity.percent,
                    hour_of_day=curHour,
                    day_of_week=DayOfWeekEnum[curDay].value,
                    history=[capacity.percent],
                )

            db_session.merge(hourly_average_capacity)
            db_session.commit()

        except Exception as e:
            print(f"Error updating hourly average: {e}")


def check_and_send_capacity_reminders(facility_name, readable_name, current_percent, last_percent):
    """
    Send notifications to topic if the current capacity dips below relevant thresholds.
    """

    current_percent_int = int(current_percent * 100)  # Convert to integer percentage
    last_percent_int = int(last_percent * 100)

    current_day_name = datetime.now().strftime("%A").upper()

    # Define threshold levels
    thresholds = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]

    # Find the thresholds that were crossed
    crossed_thresholds = [p for p in thresholds if last_percent_int > p >= current_percent_int]

    for threshold in crossed_thresholds:
        topic_name = f"{facility_name}_{current_day_name}_{threshold}"
        print(f"Sending message to devices subscribed to {topic_name}")
        send_capacity_reminder(topic_name, readable_name, threshold)
