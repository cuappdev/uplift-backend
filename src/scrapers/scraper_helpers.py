import pytz
from datetime import datetime, timedelta, timezone
from src.utils.constants import (
    EASTERN_TIMEZONE,
    MARKER_ALT,
    MARKER_BADMINTON,
    MARKER_BASKETBALL,
    MARKER_SHALLOW,
    MARKER_VOLLEYBALL,
    MARKER_WOMEN,
)


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


def determine_pool_hours(time_str, date):
    """
    Determine hours for a facility with Pool type.

    The first element is the start time, second is end time, third is women only (bool),
    fourth is shallow only (bool).

    - Parameters:
        - `time_str`    The time string to parse.
        - `date`        The date to add the hours to.

    - Returns:      An array containing three elements.
    """
    # Remove MARKERS
    cleaned_str = time_str.replace(MARKER_WOMEN, "").replace(MARKER_SHALLOW, "")
    start, end = get_hours_datetimes(cleaned_str, date)

    # Handle women and shallow only
    if time_str.find(MARKER_WOMEN) != -1:
        return [start, end, True, False]
    elif time_str.find(MARKER_SHALLOW) != -1:
        return [start, end, False, True]
    else:
        return [start, end, False, False]


def determine_court_hours(time_str, date):
    """
    Determine hours for a facility with Court type.

    The first element is the start time, second is end time, third is court type.

    - Parameters:
        - `time_str`    The time string to parse.
        - `date`        The date to add the hours to.

    - Returns:      An array containing three elements.
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

    return [start, end, court_type]
