from collections import namedtuple
from datetime import datetime, timedelta
from src.database import db_session
from src.models.openhours import OpenHours
from src.models.activity import PriceType
from src.utils.constants import (
    MARKER_ALT,
    MARKER_BADMINTON,
    MARKER_BASKETBALL,
    MARKER_GEAR,
    MARKER_RATE,
    MARKER_SHALLOW,
    MARKER_VOLLEYBALL,
    MARKER_WOMEN,
    SECONDS_IN_DAY,
)
from src.utils.utils import unix_time


def clean_past_hours():
    """
    Remove hours that are in the past by one day.
    """
    day_unix = unix_time(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)) - SECONDS_IN_DAY
    OpenHours.query.filter(OpenHours.end_time <= day_unix).delete()
    db_session.commit()


def clean_hours(date, facility_id=None, gym_id=None):
    """
    Remove hours that are on the same day as the given date.

    Parameters:
        - `date`            The date to compare with.
        - `facility_id`     The ID of the facility to remove from. Default is None.
        - `gym_id`          The ID of the gym to remove from. Defaut is None.
    """
    if facility_id:
        day_start_unix = unix_time(date.replace(hour=0, minute=0, second=0, microsecond=0))
        day_end_unix = day_start_unix + SECONDS_IN_DAY
        OpenHours.query.filter_by(facility_id=facility_id).filter(day_start_unix <= OpenHours.start_time).filter(
            day_end_unix >= OpenHours.start_time
        ).delete()

    if gym_id:
        day_start_unix = unix_time(date.replace(hour=0, minute=0, second=0, microsecond=0))
        day_end_unix = day_start_unix + SECONDS_IN_DAY
        OpenHours.query.filter_by(gym_id=gym_id).filter(day_start_unix <= OpenHours.start_time).filter(
            day_end_unix >= OpenHours.start_time
        ).delete()


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

    return result


def determine_pool_hours(time_str, date):
    """
    Determine hours for a facility with Pool type.

    The hours are represented by a `CourtHours` named tuple with attributes
    `start`, `end`, `is_women`, and `is_shallow`.

    - Parameters:
        - `time_str`    The time string to parse.
        - `date`        The date to add the hours to.

    - Returns:      A named tuple with the attributes described above.
    """
    # Remove MARKERS
    cleaned_str = time_str.replace(MARKER_WOMEN, "").replace(MARKER_SHALLOW, "")
    start, end = get_hours_datetimes(cleaned_str, date)

    # Create named tuple
    PoolHours = namedtuple("PoolHours", "start end is_women is_shallow")

    # Handle women and shallow only
    if time_str.find(MARKER_WOMEN) != -1:
        return PoolHours(start, end, True, False)
    elif time_str.find(MARKER_SHALLOW) != -1:
        return PoolHours(start, end, False, True)
    else:
        return PoolHours(start, end, False, False)


def determine_court_hours(time_str, date):
    """
    Determine hours for a facility with Court type.

    The hours are represented by a `CourtHours` named tuple with attributes
    `start`, `end`, and `type`.

    - Parameters:
        - `time_str`    The time string to parse.
        - `date`        The date to add the hours to.

    - Returns:      A named tuple with the attributes described above.
    """
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

    # Create named tuple
    CourtHours = namedtuple("Hours", "start end type")
    return CourtHours(start, end, court_type)


def get_pricing(pricing_str):
    """
    Determine pricing of a gear or rate for an activity.

    The pricings are represented by a `Pricing` named tuple with attributes
    `name`, `cost`, `rate`, and `type`.

    - Parameters:
        - `pricing_str` The price string to parse.

    - Returns:      A named tuple with the attributes described above.
    """
    # Separate into elements
    parts = pricing_str.split(", ")
    name = parts[0][4:]

    # Handle different price types (MUST HAVE A MARKER)
    if pricing_str.find(MARKER_RATE) != -1:
        price_type = PriceType.rate
    elif pricing_str.find(MARKER_GEAR) != -1:
        price_type = PriceType.gear
    cost_part = parts[1]
    if "/" in cost_part:
        cost, rate = cost_part.split("/")
    else:
        cost = cost_part
        rate = None
    cost = float(cost)

    # Create named tuple
    Price = namedtuple("Pricing", "name cost rate type")
    print(Price)
    return Price(cost, name, rate, price_type)
