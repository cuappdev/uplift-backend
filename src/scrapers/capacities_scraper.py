import gspread, pytz
from datetime import datetime, timezone
from pandas import DataFrame
from src.database import db_session
from src.models.capacity import Capacity
from src.utils.constants import EASTERN_TIMEZONE, SERVICE_ACCOUNT_PATH, SHEET_CAPACITIES, SHEET_KEY
from src.utils.utils import get_facility_id, unix_time

# Configure client and sheet
gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
sh = gc.open_by_key(SHEET_KEY)


def fetch_capacities():
    """
    Fetch capacities for all facilities.
    """
    worksheet = sh.worksheet(SHEET_CAPACITIES)
    vals = DataFrame(worksheet.get_all_records())
    names = vals["Name"]

    # Add to database
    for i in range(len(names)):
        count = int(vals["Count"][i])
        percent = float(vals["Percent"][i])
        updated = get_capacity_datetime(vals["Updated"][i])
        facility_id = int(get_facility_id(names[i]))

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

    # Clear old capacity and create a new one
    Capacity.query.filter_by(facility_id=facility_id).delete()
    capacity = Capacity(count=count, facility_id=facility_id, percent=percent, updated=updated_unix)

    # Save to database
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

    # Convert from Eastern to Local time
    eastern_tz = pytz.timezone(EASTERN_TIMEZONE)
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    time_obj = eastern_tz.localize(time_obj).astimezone(local_tz)

    return time_obj
