import unittest, pytz
from src.utils.constants import LOCAL_TIMEZONE
from datetime import datetime
from src.scrapers.hours_scraper import get_hours_datetimes
from src.scrapers.capacities_scraper import get_capacity_datetime


class TestScraperHelpers(unittest.TestCase):
    """
    Test suite for scraper helper functions.
    """

    def create_dt_helper(self, time_str):
        """
        Helper function to create a datetime object for testing.

        The format used is `%m/%d/%Y %H:%M` such as (`01/01/2023 23:30`).

        Parameters:
            - `time_str`    The string of the date to parse in Eastern time.

        Returns:    a datetime object in UTC time.
        """
        format = "%m/%d/%Y %H:%M"
        date_obj = datetime.strptime(time_str, format)

        # Convert from Eastern to UTC time
        local_tz = pytz.timezone(LOCAL_TIMEZONE)
        date_obj = local_tz.localize(date_obj).astimezone(pytz.UTC)

        return date_obj

    def assertDateEqual(self, d1, d2):
        """
        Assert equality between two datetime objects.

        Parameters:
            - `d1`      The first datetime object to compare.
            - `d2`      The second datetime object to compare.
        """
        self.assertEqual(d1.replace(tzinfo=None), d2.replace(tzinfo=None))

    def test_get_hours_datetimes(self):
        """
        Test procedure for `get_hours_datetimes()`.
        """
        print("Testing get_hours_datetimes...")
        curr_date = self.create_dt_helper("12/24/2023 12:30").replace(tzinfo=None)

        # Start and end both AM
        result = get_hours_datetimes("6am - 10am", curr_date)
        self.assertDateEqual(result[0], self.create_dt_helper("12/24/2023 6:00"))
        self.assertDateEqual(result[1], self.create_dt_helper("12/24/2023 10:00"))

        # Start and end both PM
        result = get_hours_datetimes("6pm - 10pm", curr_date)
        self.assertDateEqual(result[0], self.create_dt_helper("12/24/2023 18:00"))
        self.assertDateEqual(result[1], self.create_dt_helper("12/24/2023 22:00"))

        # Start and end AM to PM
        result = get_hours_datetimes("6am - 10pm", curr_date)
        self.assertDateEqual(result[0], self.create_dt_helper("12/24/2023 6:00"))
        self.assertDateEqual(result[1], self.create_dt_helper("12/24/2023 22:00"))

        # Start and end PM to AM
        result = get_hours_datetimes("10pm - 1am", curr_date)
        self.assertDateEqual(result[0], self.create_dt_helper("12/24/2023 22:00"))
        self.assertDateEqual(result[1], self.create_dt_helper("12/25/2023 1:00"))

        # Start and end with minutes
        result = get_hours_datetimes("10:30pm - 1:30am", curr_date)
        self.assertDateEqual(result[0], self.create_dt_helper("12/24/2023 22:30"))
        self.assertDateEqual(result[1], self.create_dt_helper("12/25/2023 1:30"))

        # Start and end no space
        result = get_hours_datetimes("10:30pm-1:30am", curr_date)
        self.assertDateEqual(result[0], self.create_dt_helper("12/24/2023 22:30"))
        self.assertDateEqual(result[1], self.create_dt_helper("12/25/2023 1:30"))

        # Month Change
        curr_date = self.create_dt_helper("11/30/2023 12:30").replace(tzinfo=None)
        result = get_hours_datetimes("10pm-1am", curr_date)
        self.assertDateEqual(result[0], self.create_dt_helper("11/30/2023 22:00"))
        self.assertDateEqual(result[1], self.create_dt_helper("12/01/2023 1:00"))

        # Year Change
        curr_date = self.create_dt_helper("12/31/2023 12:30").replace(tzinfo=None)
        result = get_hours_datetimes("10pm-1am", curr_date)
        self.assertDateEqual(result[0], self.create_dt_helper("12/31/2023 22:00"))
        self.assertDateEqual(result[1], self.create_dt_helper("01/01/2024 1:00"))

    def test_get_capacity_datetime(self):
        """
        Test procedure for `get_capacity_datetime()`.
        """
        print("Testing get_capacity_datetime...")

        # AM
        result = get_capacity_datetime("12/18/2023 5:54 AM")
        self.assertDateEqual(result, self.create_dt_helper("12/18/2023 5:54"))

        # PM
        result = get_capacity_datetime("12/18/2023 5:54 PM")
        self.assertDateEqual(result, self.create_dt_helper("12/18/2023 17:54"))


if __name__ == "__main__":
    unittest.main()
