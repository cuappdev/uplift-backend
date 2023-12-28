import gspread
from datetime import datetime, timedelta
from src.database import db_session
from src.models.openhours import OpenHours
from src.scrapers.scraper_helpers import determine_court_hours, determine_pool_hours, get_hours_datetimes
from src.utils.constants import (
    MARKER_CLOSED,
    MARKER_TIME_DELIMITER,
    FACILITY_ID_DICT,
    FACILITY_ROW_DICT,
    GYM_ID_DICT,
    SERVICE_ACCOUNT_PATH,
    SHEET_KEY,
    SHEET_REG_BUILDING,
    SHEET_REG_FACILITY,
)
from src.utils.utils import unix_time

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
    vals = worksheet.get_all_values()

    # Fetch row info
    hnh = vals[2][1:]
    noyes = vals[3][1:]
    teagle = vals[4][1:]
    morrison = vals[5][1:]

    for i in range(7):
        # Determine next day
        date = datetime.now() + timedelta(days=i)

        # Monday = 0, ..., Sunday = 6
        weekday = date.weekday()
        time_strings = [hnh[weekday], noyes[weekday], teagle[weekday], morrison[weekday]]

        # Keep order consistent
        gym_ids = [
            GYM_ID_DICT["hnh"],
            GYM_ID_DICT["noyes"],
            GYM_ID_DICT["teagle"],
            GYM_ID_DICT["morrison"],
        ]

        # Add to database
        for j in range(len(time_strings)):
            # Handle case if there is a are multiple hours
            for time_str in time_strings[j].split(MARKER_TIME_DELIMITER):
                # Handle closed
                if time_str != MARKER_CLOSED:
                    start, end = get_hours_datetimes(time_str, date)
                    add_regular_gym_hours(start, end, gym_ids[j])


def fetch_reg_facility():
    """
    Fetch regular facility hours.
    """
    worksheet = sh.worksheet(SHEET_REG_FACILITY)
    vals = worksheet.get_all_values()

    fetch_reg_bowling(hnh=vals[FACILITY_ROW_DICT["bowling_hnh"]][2:])
    fetch_reg_court(
        hnh_1=vals[FACILITY_ROW_DICT["court_hnh_1"]][2:],
        hnh_2=vals[FACILITY_ROW_DICT["court_hnh_2"]][2:],
        noyes=vals[FACILITY_ROW_DICT["court_noyes"]][2:],
    )
    fetch_reg_pool(hnh=vals[FACILITY_ROW_DICT["pool_hnh"]][2:], teagle=vals[FACILITY_ROW_DICT["pool_tgl"]][2:])
    fetch_reg_fc(
        hnh=vals[FACILITY_ROW_DICT["fc_hnh"]][2:],
        noyes=vals[FACILITY_ROW_DICT["fc_noyes"]][2:],
        tgl_down=vals[FACILITY_ROW_DICT["fc_tgl_down"]][2:],
        tgl_up=vals[FACILITY_ROW_DICT["fc_tgl_up"]][2:],
        morr=vals[FACILITY_ROW_DICT["fc_morr"]][2:],
    )


def fetch_reg_bowling(hnh):
    """
    Fetch regular bowling hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.

    - Parameters:
        - `hnh`         The row info for Helen Newman Bowling.
    """
    for i in range(7):
        # Determine next day and check if weekday or weekend
        date = datetime.now() + timedelta(days=i)

        # Monday = 0, ..., Sunday = 6
        weekday = date.weekday()
        time_string = hnh[weekday]

        facility_id = FACILITY_ID_DICT["hnh_bowling"]

        # Add to database
        # Handle case if there are multiple hours
        for time_str in time_string.split(MARKER_TIME_DELIMITER):
            # Handle closed
            if time_str != MARKER_CLOSED:
                start, end = get_hours_datetimes(time_str, date)
                add_regular_facility_hours(start, end, facility_id)


def fetch_reg_court(hnh_1, hnh_2, noyes):
    """
    Fetch regular court hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.

    - Parameters:
        - `hnh_1`       The row info for Helen Newman Court 1.
        - `hnh_2`       The row info for Heen Newman Court 2.
        - `noyes`       The row info for Noyes Indoor Court.
    """
    for i in range(7):
        # Determine next day
        date = datetime.now() + timedelta(days=i)

        # Monday = 0, ..., Sunday = 6
        weekday = date.weekday()
        time_strings = [hnh_1[weekday], hnh_2[weekday], noyes[weekday]]

        # Keep order consistent
        facility_ids = [FACILITY_ID_DICT["hnh_court1"], FACILITY_ID_DICT["hnh_court2"], FACILITY_ID_DICT["noyes_court"]]

        # Add to database
        for j in range(len(time_strings)):
            # Handle case if there are multiple hours
            for time_str in time_strings[j].split(MARKER_TIME_DELIMITER):
                # Handle closed
                if time_str != MARKER_CLOSED:
                    start, end, type = determine_court_hours(time_str, date)
                    add_regular_facility_hours(start, end, facility_ids[j], court_type=type)


def fetch_reg_pool(hnh, teagle):
    """
    Fetch regular pool hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.

    - Parameters:
        - `hnh`         The row info for Helen Newman Pool.
        - `teagle`      The row info for Teagle Pool.
    """
    for i in range(7):
        # Determine next day
        date = datetime.now() + timedelta(days=i)

        # Monday = 0, ..., Sunday = 6
        weekday = date.weekday()
        time_strings = [hnh[weekday], teagle[weekday]]

        # Keep order consistent
        facility_ids = [FACILITY_ID_DICT["hnh_pool"], FACILITY_ID_DICT["tgl_pool"]]

        # Add to database
        for j in range(len(time_strings)):
            # Handle case if there are multiple hours
            for time_str in time_strings[j].split(MARKER_TIME_DELIMITER):
                # Handle closed
                if time_str != MARKER_CLOSED:
                    start, end, women, shallow = determine_pool_hours(time_str, date)
                    if women:
                        add_regular_facility_hours(start, end, facility_ids[j], is_women=True)
                    elif shallow:
                        add_regular_facility_hours(start, end, facility_ids[j], is_shallow=True)
                    else:
                        add_regular_facility_hours(start, end, facility_ids[j])


def fetch_reg_fc(hnh, noyes, tgl_down, tgl_up, morr):
    """
    Fetch regular fitness center hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.

    - Parameters:
        - `hnh`         The row info for Helen Newman Fitness Center.
        - `noyes`       The row info for Noyes Fitness Center.
        - `tgl_down`    The row info for Teagle Down Fitness Center.
        - `tgl_up`      The row info for Teagle Up Fitness Center.
        - `morr`        The row info for Morrison Fitness Center.
    """
    for i in range(7):
        # Determine next day and check if weekday or weekend
        date = datetime.now() + timedelta(days=i)

        # Monday = 0, ..., Sunday = 6
        weekday = date.weekday()
        time_strings = [hnh[weekday], noyes[weekday], tgl_down[weekday], tgl_up[weekday], morr[weekday]]

        facility_ids = [
            FACILITY_ID_DICT["hnh_fitness"],
            FACILITY_ID_DICT["noyes_fitness"],
            FACILITY_ID_DICT["tgl_down"],
            FACILITY_ID_DICT["tgl_up"],
            FACILITY_ID_DICT["morr_fitness"],
        ]

        # Add to database
        for j in range(len(time_strings)):
            # Handle case if there are multiple hours
            for time_str in time_strings[j].split(MARKER_TIME_DELIMITER):
                # Handle closed
                if time_str != MARKER_CLOSED:
                    start, end = get_hours_datetimes(time_str, date)
                    add_regular_facility_hours(start, end, facility_ids[j])


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
