import gspread
from src.database import db_session
from src.models.capacity import Capacity  # do not remove
from src.models.openhours import OpenHours
from src.models.gym import Gym
from src.scrapers.scraper_helpers import determine_court_hours, determine_pool_hours, get_hours_datetimes
from src.utils.constants import (
    MARKER_BOWLING,
    MARKER_CLOSED,
    MARKER_COURT,
    MARKER_FITNESS,
    MARKER_POOL,
    MARKER_TIME_DELIMITER,
    FACILITY_ID_DICT,
    SERVICE_ACCOUNT_PATH,
    SHEET_SP_FACILITY,
    SHEET_KEY,
)
from src.utils.utils import unix_time, within_week, get_date_ranges

# Configure client and sheet
gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
sh = gc.open_by_key(SHEET_KEY)


def fetch_sp_facility():
    """
    Fetch special facility hours.
    """
    worksheet = sh.worksheet(SHEET_SP_FACILITY)
    vals = worksheet.get_all_values()

    # For loop goes here
    row = vals[2]
    # for row in vals[2:]:
    # Grab sheet data
    dates = get_date_ranges(row[0])
    type = row[1]
    name = row[2]
    time_strings = row[3:]

    for i in range(len(dates)):
        date = dates[i]
        hours = time_strings[date.weekday()]

        # Check if hours exist and is within next 7 days
        if hours and within_week(date):
            if hours == MARKER_CLOSED:
                remove_facility_hours(date, FACILITY_ID_DICT[name])
            else:
                # Handle case if there are multiple hours
                for time_str in hours.split(MARKER_TIME_DELIMITER):
                    # Check facility type
                    if type == MARKER_BOWLING or type == MARKER_FITNESS:
                        start, end = get_hours_datetimes(time_str, date)
                        add_special_facility_hours(start, end, FACILITY_ID_DICT[name])
                    elif type == MARKER_COURT:
                        start, end, type = determine_court_hours(time_str, date)
                        add_special_facility_hours(start, end, FACILITY_ID_DICT[name], court_type=type)
                    elif type == MARKER_POOL:
                        start, end, women, shallow = determine_pool_hours(time_str, date)
                        if women:
                            add_special_facility_hours(start, end, FACILITY_ID_DICT[name], is_women=True)
                        elif shallow:
                            add_special_facility_hours(start, end, FACILITY_ID_DICT[name], is_shallow=True)
                        else:
                            add_special_facility_hours(start, end, FACILITY_ID_DICT[name])


# MARK: Helpers


def remove_facility_hours(start_time, facility_id):
    """
    Remove facility hours from the database.

    Parameters:
        - `start_time`      The datetime object representing the opening time.
        - `facility_id`     The ID of the facility.
    """
    # Get unix time for the day
    day_start_unix = unix_time(start_time.replace(hour=0, minute=0, second=0, microsecond=0))
    day_end_unix = day_start_unix + 86400  # 86400 seconds in a day

    # Delete overlapping hours
    OpenHours.query.filter_by(facility_id=facility_id).filter(day_start_unix <= OpenHours.start_time).filter(
        day_end_unix >= OpenHours.start_time
    ).delete()

    # Save changes
    db_session.commit()


def add_special_facility_hours(start_time, end_time, facility_id, court_type=None, is_shallow=None, is_women=None):
    """
    Add special facility hours to the database.

    This removes regular hours if there is an overlap.

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

    # Get unix time for the day
    day_start_unix = unix_time(start_time.replace(hour=0, minute=0, second=0, microsecond=0))
    day_end_unix = day_start_unix + 86400  # 86400 seconds in a day

    # Delete overlapping hours
    OpenHours.query.filter_by(facility_id=facility_id).filter(day_start_unix <= OpenHours.start_time).filter(
        day_end_unix >= OpenHours.start_time
    ).delete()

    # Create hours
    hrs = OpenHours(
        end_time=end_unix,
        facility_id=facility_id,
        start_time=start_unix,
        court_type=court_type,
        is_shallow=is_shallow,
        is_special=True,
        is_women=is_women,
    )

    # Add to database
    db_session.merge(hrs)
    db_session.commit()
