import gspread, pytz
from datetime import datetime
from src.database import db_session
from src.models.capacity import Capacity
from src.utils.constants import FACILITY_ID_DICT, LOCAL_TIMEZONE, SERVICE_ACCOUNT_PATH, SHEET_CAPACITIES, SHEET_KEY
from src.utils.utils import unix_time

# Configure client and sheet
gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
sh = gc.open_by_key(SHEET_KEY)


def fetch_capacities():
    """
    Fetch capacities for all facilities.
    """
    worksheet = sh.worksheet(SHEET_CAPACITIES)
    vals = worksheet.get_all_values()

    # Fetch row info
    hnh_fitness = vals[2][1:]
    noyes_fitness = vals[3][1:]
    tgl_down = vals[4][1:]
    tgl_up = vals[5][1:]
    morr_fitness = vals[6][1:]
    hnh_court1 = vals[7][1:]
    hnh_court2 = vals[8][1:]
    noyes_court = vals[9][1:]

    # Note that the order matters!
    rows = [hnh_fitness, noyes_fitness, tgl_down, tgl_up, morr_fitness, hnh_court1, hnh_court2, noyes_court]
    facility_ids = [
        FACILITY_ID_DICT["hnh_fitness"],
        FACILITY_ID_DICT["noyes_fitness"],
        FACILITY_ID_DICT["tgl_down"],
        FACILITY_ID_DICT["tgl_up"],
        FACILITY_ID_DICT["morr_fitness"],
        FACILITY_ID_DICT["hnh_court1"],
        FACILITY_ID_DICT["hnh_court2"],
        FACILITY_ID_DICT["noyes_court"],
    ]

    # Add to database
    for i in range(len(rows)):
        # Count = 0, Percent = 1, Updated = 2
        count = rows[i][0]
        percent = rows[i][1]
        updated = get_capacity_datetime(rows[i][2])
        facility_id = facility_ids[i]

        add_single_capacity(count, facility_id, percent, updated)


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

    # Create capacity
    capacity = Capacity(count=count, facility_id=facility_id, percent=percent, updated=updated_unix)

    # Add to database
    db_session.merge(capacity)
    db_session.commit()


def get_capacity_datetime(time_str):
    """
    Get a datetime object for a Capacity given a time string.

    The time is converted into UTC time from Eastern time.

    Parameters:
        - `time_str`    The Eastern time string to parse in `%m/%d/%Y %I:%M %p`
                        format (ex: `12/18/2023 5:54 PM`).

    Returns:    a datetime object in UTC time.
    """
    format = "%m/%d/%Y %I:%M %p"
    time_obj = datetime.strptime(time_str, format)

    # Convert from Eastern to UTC time
    local_tz = pytz.timezone(LOCAL_TIMEZONE)
    time_obj = local_tz.localize(time_obj).astimezone(pytz.UTC)

    return time_obj
