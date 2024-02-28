import gspread
from datetime import datetime, timedelta
from pandas import DataFrame
from src.database import db_session
from src.models.openhours import OpenHours
from src.scrapers.scraper_helpers import clean_hours, determine_court_hours, determine_pool_hours, get_hours_datetimes
from src.utils.constants import (
    DAYS_OF_WEEK,
    MARKER_BOWLING,
    MARKER_CLOSED,
    MARKER_COURT,
    MARKER_FITNESS,
    MARKER_POOL,
    MARKER_TIME_DELIMITER,
    SERVICE_ACCOUNT_PATH,
    SHEET_KEY,
    SHEET_REG_BUILDING,
    SHEET_REG_FACILITY,
)
from src.utils.utils import get_facility_id, get_gym_id, unix_time

# Configure client and sheet
gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
sh = gc.open_by_key(SHEET_KEY)


def fetch_reg_building():
    """
    Fetch regular building hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.
    """
    worksheet = sh.worksheet(SHEET_REG_BUILDING)
    vals = DataFrame(worksheet.get_all_records())

    for i in range(len(DAYS_OF_WEEK)):
        # Determine next day
        date = datetime.now() + timedelta(days=i)

        # Get spreadsheet info
        weekday = DAYS_OF_WEEK[date.weekday()]
        names = vals["Name"]

        # Add to database
        for j in range(len(names)):
            time_string = vals[weekday][j]
            gym_id = get_gym_id(names[j])

            # Clean hours for that day
            clean_hours(date, gym_id=gym_id)

            # Handle case if there are multiple hours
            for time_str in time_string.split(MARKER_TIME_DELIMITER):
                # Handle closed
                if time_str != MARKER_CLOSED:
                    start, end = get_hours_datetimes(time_str, date)
                    add_regular_gym_hours(start, end, gym_id)


def fetch_reg_facility():
    """
    Fetch regular facility hours.
    """
    worksheet = sh.worksheet(SHEET_REG_FACILITY)
    vals = DataFrame(worksheet.get_all_records())

    fetch_reg_bowling(vals)
    fetch_reg_court(vals)
    fetch_reg_pool(vals)
    fetch_reg_fc(vals)


def fetch_reg_bowling(vals):
    """
    Fetch regular bowling hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.

    - Parameters:
        - `vals`         The spreadsheet data.
    """
    for i in range(len(DAYS_OF_WEEK)):
        # Determine next day
        date = datetime.now() + timedelta(days=i)

        # Get spreadsheet info
        weekday = DAYS_OF_WEEK[date.weekday()]
        names = vals["Name"]

        # Add to database
        for j in range(len(names)):
            if vals["Type"][j] == MARKER_BOWLING:
                time_string = vals[weekday][j]
                facility_id = get_facility_id(names[j])

                # Clean hours for that day
                clean_hours(date, facility_id)

                # Handle case if there are multiple hours
                for time_str in time_string.split(MARKER_TIME_DELIMITER):
                    # Handle closed
                    if time_str != MARKER_CLOSED:
                        start, end = get_hours_datetimes(time_str, date)
                        add_regular_facility_hours(start, end, facility_id)


def fetch_reg_court(vals):
    """
    Fetch regular court hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.

    - Parameters:
        - `vals`         The spreadsheet data.
    """
    for i in range(len(DAYS_OF_WEEK)):
        # Determine next day
        date = datetime.now() + timedelta(days=i)

        # Get spreadsheet info
        weekday = DAYS_OF_WEEK[date.weekday()]
        names = vals["Name"]

        # Add to database
        for j in range(len(names)):
            if vals["Type"][j] == MARKER_COURT:
                time_string = vals[weekday][j]
                facility_id = get_facility_id(names[j])

                # Clean hours for that day
                clean_hours(date, facility_id)

                # Handle case if there are multiple hours
                for time_str in time_string.split(MARKER_TIME_DELIMITER):
                    # Handle closed
                    if time_str != MARKER_CLOSED:
                        start, end, type = determine_court_hours(time_str, date)
                        add_regular_facility_hours(start, end, facility_id, court_type=type)


def fetch_reg_pool(vals):
    """
    Fetch regular pool hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.

    - Parameters:
        - `vals`         The spreadsheet data.
    """
    for i in range(len(DAYS_OF_WEEK)):
        # Determine next day
        date = datetime.now() + timedelta(days=i)

        # Get spreadsheet info
        weekday = DAYS_OF_WEEK[date.weekday()]
        names = vals["Name"]

        # Add to database
        for j in range(len(names)):
            if vals["Type"][j] == MARKER_POOL:
                time_string = vals[weekday][j]
                facility_id = get_facility_id(names[j])

                # Clean hours for that day
                clean_hours(date, facility_id)

                # Handle case if there are multiple hours
                for time_str in time_string.split(MARKER_TIME_DELIMITER):
                    # Handle closed
                    if time_str != MARKER_CLOSED:
                        start, end, is_women, is_shallow = determine_pool_hours(time_str, date)
                        if is_women:
                            add_regular_facility_hours(start, end, facility_id, is_women=True)
                        elif is_shallow:
                            add_regular_facility_hours(start, end, facility_id, is_shallow=True)
                        else:
                            add_regular_facility_hours(start, end, facility_id)


def fetch_reg_fc(vals):
    """
    Fetch regular fitness center hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.

    - Parameters:
        - `vals`         The spreadsheet data.
    """
    for i in range(len(DAYS_OF_WEEK)):
        # Determine next day
        date = datetime.now() + timedelta(days=i)

        # Get spreadsheet info
        weekday = DAYS_OF_WEEK[date.weekday()]
        names = vals["Name"]

        # Add to database
        for j in range(len(names)):
            if vals["Type"][j] == MARKER_FITNESS:
                time_string = vals[weekday][j]
                facility_id = get_facility_id(names[j])

                # Clean hours for that day
                clean_hours(date, facility_id)

                # Handle case if there are multiple hours
                for time_str in time_string.split(MARKER_TIME_DELIMITER):
                    # Handle closed
                    if time_str != MARKER_CLOSED:
                        start, end = get_hours_datetimes(time_str, date)
                        add_regular_facility_hours(start, end, facility_id)


# MARK: Helpers


def add_regular_gym_hours(start_time, end_time, gym_id):
    """
    Add regular gym hours to the database.

    Parameters:
        - `start_time`      The datetime object representing the opening time.
        - `end_time`        The datetime object representing the closing time.
        - `gym_id`          The ID of the gym.
    """
    # Convert datetime objects to Unix
    start_unix = unix_time(start_time)
    end_unix = unix_time(end_time)

    # Create hours
    hrs = OpenHours(end_time=end_unix, gym_id=gym_id, start_time=start_unix)

    # Add to database
    db_session.merge(hrs)
    db_session.commit()


def add_regular_facility_hours(start_time, end_time, facility_id, court_type=None, is_shallow=None, is_women=None):
    """
    Add regular facility hours to the database.

    Parameters:
        - `start_time`      The datetime object representing the opening time.
        - `end_time`        The datetime object representing the closing time.
        - `facility_id`     The ID of the facility.
        - `court_type`      The facility court type. None by default.
        - `is_shallow`      Whether the pool is shallow or not. None by default.
        - `is_women`        Whether the pool is for women only. None by default.
    """
    # Convert datetime objects to Unix
    start_unix = unix_time(start_time)
    end_unix = unix_time(end_time)

    # Create hours
    hrs = OpenHours(
        end_time=end_unix,
        facility_id=facility_id,
        start_time=start_unix,
        court_type=court_type,
        is_shallow=is_shallow,
        is_women=is_women,
    )

    # Add to database
    db_session.merge(hrs)
    db_session.commit()
