import hashlib
import json
from datetime import datetime as dt
from src.models.openhours import OpenHours


def generate_id(data):
    return int.from_bytes(hashlib.sha256(data.encode("utf-8")).digest()[:3], 'little')


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


def parse_time(time):
    return dt.strptime(time, "%Y-%m-%d, %H:%M")


def parse_datetime(datetime):
    return dt.strptime(datetime, "%Y-%m-%dT%H:%M:%S%z")


def parse_c2c_datetime(datetime):
    return dt.strptime(datetime, "%m/%d/%Y %I:%M %p")


"""
Helper function for generating a list of OpenHours from
corresponding hours.
"""
def create_times(uid_str, facility_id, start, end, weekday):
  times = []
  day_range = range(0, 5) if weekday  else range(5, 7)
  for i in day_range:
    times.append(OpenHours(id=generate_id(f"{uid_str}-{i}"),
                           facility_id=facility_id,
                           day=i,
                           start_time=start,
                           end_time=end))
  return times