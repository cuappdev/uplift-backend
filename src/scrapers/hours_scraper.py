import gspread, pytz
from datetime import datetime, timedelta, timezone
from src.database import db_session
from src.models.openhours import OpenHours
from src.utils.constants import (
    EASTERN_TIMEZONE,
    MARKER_ALT,
    MARKER_BADMINTON,
    MARKER_BASKETBALL,
    MARKER_CLOSED,
    MARKER_SHALLOW,
    MARKER_TIME_DELIMITER,
    MARKER_VOLLEYBALL,
    MARKER_WOMEN,
    FACILITY_ID_DICT,
    GYM_ID_DICT,
    SERVICE_ACCOUNT_PATH,
    SHEET_KEY,
    SHEET_REG_BUILDING,
    SHEET_REG_COURT,
    SHEET_REG_FC,
    SHEET_REG_POOL,
)
from src.utils.utils import unix_time

# Configure client and sheet
gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
sh = gc.open_by_key(SHEET_KEY)


def fetch_reg_court():
    """
    Fetch regular court hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.
    """
    worksheet = sh.worksheet(SHEET_REG_COURT)
    vals = worksheet.get_all_values()

    # Fetch row info
    hnh_1 = vals[2][1:]
    hnh_2 = vals[3][1:]
    noyes = vals[4][1:]

    for i in range(6):
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
                    # Remove MARKERS
                    cleaned_str = (
                        time_str.replace(MARKER_BADMINTON, "")
                        .replace(MARKER_BASKETBALL, "")
                        .replace(MARKER_VOLLEYBALL, "")
                        .replace(MARKER_ALT, "")
                    )
                    start, end = get_hours_datetimes(cleaned_str, date)

                    # Handle different courts (MUST HAVE A MARKER)
                    if time_str.find(MARKER_BADMINTON) != -1:
                        court_type = "badminton"
                    elif time_str.find(MARKER_BASKETBALL) != -1:
                        court_type = "basketball"
                    elif time_str.find(MARKER_VOLLEYBALL) != -1:
                        court_type = "volleyball"
                    elif time_str.find(MARKER_ALT) != -1:
                        # TODO: Odd Day - Badminton; Even Day - Volleyball
                        court_type = "badminton" if date.day % 2 == 1 else "volleyball"

                    add_single_facility_hours(start, end, facility_ids[j], court_type=court_type)


def fetch_reg_pool():
    """
    Fetch regular pool hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.
    """
    worksheet = sh.worksheet(SHEET_REG_POOL)
    vals = worksheet.get_all_values()

    # Fetch row info
    hnh = vals[2][1:]
    teagle = vals[3][1:]

    for i in range(6):
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
                    # Remove MARKERS
                    cleaned_str = time_str.replace(MARKER_WOMEN, "").replace(MARKER_SHALLOW, "")
                    start, end = get_hours_datetimes(cleaned_str, date)

                    # Handle women and shallow only
                    if time_str.find(MARKER_WOMEN) != -1:
                        add_single_facility_hours(start, end, facility_ids[j], is_women=True)
                    elif time_str.find(MARKER_SHALLOW) != -1:
                        add_single_facility_hours(start, end, facility_ids[j], is_shallow=True)
                    else:
                        add_single_facility_hours(start, end, facility_ids[j])


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

    for i in range(6):
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
                    add_single_gym_hours(start, end, gym_ids[j])


def fetch_reg_fc():
    """
    Fetch regular fitness center hours for the next 7 days (inclusive of today).

    For example, if today is Tuesday, fetch hours for today up to and including
    next Monday.
    """
    worksheet = sh.worksheet(SHEET_REG_FC)

    # Fetch weekday/weekend strings
    _, hnh_wday, hnh_wend = worksheet.row_values("3")
    _, noyes_wday, noyes_wend = worksheet.row_values("4")
    _, tgl_dn_wday, tgl_dn_wend = worksheet.row_values("5")
    _, tgl_up_wday, tgl_up_wend = worksheet.row_values("6")
    _, morr_wday, morr_wend = worksheet.row_values("7")

    for i in range(6):
        # Determine next day and check if weekday or weekend
        date = datetime.now() + timedelta(days=i)

        # Keep order consistent
        time_strings = [hnh_wend, noyes_wend, tgl_dn_wend, tgl_up_wend, morr_wend]
        if date.weekday() < 5:
            # Weekday
            time_strings = [hnh_wday, noyes_wday, tgl_dn_wday, tgl_up_wday, morr_wday]

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
                    add_single_facility_hours(start, end, facility_ids[j])


def add_single_gym_hours(start_time, end_time, gym_id):
    """
    Add a single gym hours to the database.

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


def add_single_facility_hours(start_time, end_time, facility_id, court_type=None, is_shallow=None, is_women=None):
    """
    Add a single facility hours to the database.

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


def get_hours_datetimes(time_str, day):
    """
    Get datetime objects for OpenHours given a time string and day in UTC time.

    The first element is the start time. The second element is the end time.
    If the end time is 12am or later, use the next day. For example, `2pm - 1am`
    will return an end time for the day after the day for 2pm.

    Parameters:
        - `time_str`    The Eastern time string to parse in `%I%p - %I%p` format
                        (ex: `6am - 9pm`) or `%I:%M%p - %I:%M%p` format
                        (ex: `6:30am - 9:30pm`).
        - `day`         A datetime object representing the day for these times in UTC.

    Returns:    a list of datetime objects with the first element as start time
                and second element as end time.
    """
    # Remove all spaces
    time_str = time_str.replace(" ", "")

    # Separate start and end time
    dash_pos = time_str.index("-")
    start_time_str = time_str[:dash_pos]
    end_time_str = time_str[dash_pos + 1 :]

    result = []
    for time in [start_time_str, end_time_str]:
        # Change format if minutes is missing (ex: `6pm`)
        format = "%I%p" if time.find(":") == -1 else "%I:%M%p"

        # Convert to datetime objects and add to given day
        time_obj = datetime.strptime(time, format)
        time_obj = day.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)

        # Check if end time is past midnight (since CFC displays it like this)
        if time == end_time_str and result[0] > time_obj:
            time_obj += timedelta(days=1)

        result.append(time_obj)

    # Convert from Eastern to Local Time
    eastern_tz = pytz.timezone(EASTERN_TIMEZONE)
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    for i in range(len(result)):
        result[i] = eastern_tz.localize(result[i]).astimezone(local_tz)

    return result
