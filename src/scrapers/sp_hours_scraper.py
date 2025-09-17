import gspread
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
    SHEET_SP_FACILITY,
    SHEET_KEY,
)
from src.utils.utils import unix_time, within_week, get_date_ranges, get_facility_id

# Configure client and sheet
gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
sh = gc.open_by_key(SHEET_KEY)


def fetch_sp_facility():
    """
    Fetch special facility hours.
    """
    worksheet = sh.worksheet(SHEET_SP_FACILITY)
    vals = DataFrame(worksheet.get_all_records())

    # Grab sheet data
    names = vals["Name"]

    for i in range(len(names)):
        # Check if date range exists
        date_range = vals["Date Range"][i]
        if date_range:
            type = vals["Type"][i]
            name = names[i]

            for date in get_date_ranges(date_range):
                day_of_week = DAYS_OF_WEEK[date.weekday()]
                hours = vals[day_of_week][i]

                # Check if hours exist and is within next 7 days
                if hours and within_week(date):
                    # Clean hours from database
                    clean_hours(date, get_facility_id(name))
                    if hours != MARKER_CLOSED:
                        parse_special_hours(hours, type, date, get_facility_id(name))
                    else:
                        add_special_facility_hours(date, date, get_facility_id(name))


# MARK: Helpers


def parse_special_hours(time_string, type, date, facility_id):
    """
    Parse a time string in the special hours sheet.

    - Parameters:
        - `time_string`     The string to parse.
        - `type`            The facility type.
        - `date`            The datetime object to get hours for.
        - `facility_id`              The ID of the facility.
    """
    # Handle case if there are multiple hours
    for time_str in time_string.split(MARKER_TIME_DELIMITER):
        # Check facility type
        if type == MARKER_BOWLING or type == MARKER_FITNESS:
            start, end = get_hours_datetimes(time_str, date)
            add_special_facility_hours(start, end, facility_id)
        elif type == MARKER_COURT:
            start, end, type = determine_court_hours(time_str, date)
            add_special_facility_hours(start, end, facility_id, court_type=type)
        elif type == MARKER_POOL:
            start, end, is_women, is_shallow = determine_pool_hours(time_str, date)
            if is_women:
                add_special_facility_hours(start, end, facility_id, is_women=True)
            elif is_shallow:
                add_special_facility_hours(start, end, facility_id, is_shallow=True)
            else:
                add_special_facility_hours(start, end, facility_id)


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

    if start_unix == end_unix:
        print(f"Skipping special hours because times are equal: start_unix={start_unix}, end_unix={end_unix}, facility_id={facility_id}")
        return
    
    print(f"Adding special hours: start_unix={start_unix}, end_unix={end_unix}, facility_id={facility_id}, is_special=True")

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
    print(f"Committed special hours for facility_id={facility_id}")
