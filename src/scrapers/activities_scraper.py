import gspread
from pandas import DataFrame
from src.database import db_session
from src.models.activity import Activity, Price
from src.models.activity import PriceType
from src.utils.constants import (
    MARKER_PRICE_DELIMITER,
    MARKER_RATE,
    MARKER_GEAR,
    SERVICE_ACCOUNT_PATH,
    SHEET_KEY,
    SHEET_ACTIVITY,
)
from src.utils.utils import get_facility_id, get_gym_id

# Configure client and sheet
gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
sh = gc.open_by_key(SHEET_KEY)


def fetch_activity():
    """
    Fetch a activity data.
    """
    worksheet = sh.worksheet(SHEET_ACTIVITY)
    vals = DataFrame(worksheet.get_all_records())

    for i, row in vals.iterrows():
        # Get spreadsheet info
        activity_name = row["Name"]
        gym = row["Gym"]
        facility = row["Facility"]
        has_membership = row["Membership"] == "Yes"
        needs_reserve = row["Reservation"] == "Yes"
        pricing = row["Pricing"]

        gym_id = get_gym_id(gym)
        facility_id = get_facility_id(facility)

        # Create a new Activity object
        activity = Activity(
            name=activity_name,
            gym_id=gym_id,
            facility_id=facility_id,
            has_membership=has_membership,
            needs_reserve=needs_reserve,
            pricing=None,
        )
        # Add activity to database
        db_session.add(activity)
        db_session.commit()

        # Handle case if there are multiple pricing options
        for price in pricing.split(MARKER_PRICE_DELIMITER):
            add_pricing(price, activity.id)


# MARK: Helpers


def add_pricing(pricing_str, activity_id):
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

    # Create price
    price = Price(
        activity_id=activity_id,
        cost=cost,
        name=name,
        rate=rate,
        type=price_type,
    )

    # Add to database
    db_session.merge(price)
    db_session.commit()


def add_proicing(activity_id, cost, name, rate, type):
    """
    Add pricing to the database.

    Parameters:
        - `activity_id`     The ID of the activity.
        - `cost`            The cost of the price.
        - `name`            The name of the price.
        - `rate`            The rate of the price.
        - `type`            The type of the price.
    """
    # print(activity_id + " " + cost + " " + name + " " + rate + " " + type)
    # Create price
    price = Price(
        activity_id=activity_id,
        cost=cost,
        name=name,
        rate=rate,
        type=type,
    )

    # Add to database
    db_session.merge(price)
    db_session.commit()
