import os
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

# src.utils.constants reads these at import time.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_PATH", "service-account-key.json")
os.environ.setdefault("FLASK_ENV", "test")

import requests  # noqa: E402

from src.scrapers.web_hours_scraper import (  # noqa: E402
    check_hours,
    fetch_web_special_fitness_rows,
    merge_regular_rows,
    normalize_hours,
    parse_bowling_hours,
    parse_building_hours,
    parse_date_range,
    parse_days,
    parse_fitness_center_hours,
    parse_hours_tables,
)
from src.utils.constants import DAYS_OF_WEEK  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "hours"


def fixture(name):
    return (FIXTURES / name).read_text()


def by_name(rows):
    return {row["Name"]: row for row in rows}


class TestWebsiteSnapshots(unittest.TestCase):
    """
    Parse saved copies of the Cornell Recreation pages from 2026-11-11.

    These cover the formats the site uses today: day-range headers ("Monday -
    Thursday", "Weekend", "Weekdays"), colspans, " / " between time ranges,
    "Closed", captions with date ranges, and days listed down a column.
    """

    def test_fitness_center_regular_hours(self):
        regular, _ = parse_fitness_center_hours(fixture("cornell-fitness-centers.html"))
        rows = by_name(regular)

        self.assertEqual(
            set(rows),
            {
                "HNH Fitness Center",
                "Morrison Fitness Center",
                "Noyes Fitness Center",
                "Teagle Down Fitness Center",
                "Teagle Up Fitness Center",
            },
        )
        # "Monday - Thursday" and "Friday" share one cell; "Weekend" covers Saturday and Sunday
        self.assertEqual(rows["HNH Fitness Center"]["Friday"], "6:00am - 9:00pm")
        self.assertEqual(rows["HNH Fitness Center"]["Sunday"], "10:00am - 8:00pm")
        self.assertEqual(rows["Teagle Down Fitness Center"]["Thursday"], "7:00am - 8:30am\n10:00am - 10:00pm")
        self.assertEqual(rows["Teagle Down Fitness Center"]["Friday"], "7:00am - 10:00pm")
        self.assertEqual(set(rows["Morrison Fitness Center"]), {"Name", "Type", *DAYS_OF_WEEK})

    def test_fitness_center_special_hours(self):
        _, special = parse_fitness_center_hours(fixture("cornell-fitness-centers.html"))
        rows = by_name(special)

        self.assertEqual(len(special), 5)
        self.assertEqual({row["Date Range"] for row in special}, {"11/23/26 - 11/29/26"})
        self.assertEqual(
            [rows["HNH Fitness Center"][day] for day in DAYS_OF_WEEK],
            ["6:00am - 9:00pm", "6:00am - 7:00pm", "6:00am - 12:00pm", "Closed", "Closed", "Closed", "Closed"],
        )

    def test_special_hours_only_open_when_listed(self):
        html = """
        <table>
          <caption>Winter Break: December 21 - December 22, 2026</caption>
          <tr><th>Fitness Center</th><th>Monday</th><th>Tuesday</th></tr>
          <tr><td>Helen Newman</td><td>8:00am - 4:00pm</td><td></td></tr>
        </table>
        """
        rows = by_name(parse_fitness_center_hours(html)[1])

        self.assertEqual(len(rows), 5)
        # Listed with a blank day: closed that day
        self.assertEqual(
            (rows["HNH Fitness Center"]["Monday"], rows["HNH Fitness Center"]["Tuesday"]), ("8:00am - 4:00pm", "Closed")
        )
        # Not listed at all: closed for the whole range
        self.assertEqual({rows["Noyes Fitness Center"][day] for day in DAYS_OF_WEEK}, {"Closed"})

    def test_building_hours(self):
        hnh = parse_building_hours(fixture("helen-newman-hall.html"), "Helen Newman", "helen newman")[0]
        noyes = parse_building_hours(fixture("noyes-recreation-center.html"), "Noyes", "noyes")[0]
        teagle = parse_building_hours(fixture("teagle-hall.html"), "Teagle", "teagle")[0]

        self.assertEqual((hnh["Monday"], hnh["Sunday"]), ("6:00am - 11:00pm", "10:00am - 11:00pm"))
        self.assertEqual((noyes["Friday"], noyes["Saturday"]), ("7:00am - 11:00pm", "10:00am - 11:00pm"))
        self.assertEqual(teagle["Saturday"], "10:00am - 6:00pm")
        # The site lists Teagle's Sunday as "11:30pm - 5:30pm", so it's left for the sheet to fill in.
        self.assertNotIn("Sunday", teagle)

    def test_bowling_hours(self):
        bowling = parse_bowling_hours(fixture("bowling.html"))[0]

        self.assertEqual((bowling["Name"], bowling["Type"]), ("HNH Bowling", "B"))
        self.assertEqual(bowling["Monday"], "Closed")
        self.assertEqual(bowling["Saturday"], "3:00pm - 11:00pm")


class TestParsing(unittest.TestCase):
    """Formats and checks the website snapshots don't cover."""

    def test_parse_days(self):
        self.assertEqual(parse_days("Mondays"), [0])
        self.assertEqual(parse_days("Tues"), [1])
        self.assertEqual(parse_days("Friday - Monday"), [4, 5, 6, 0])
        self.assertEqual(parse_days("Saturday & Sunday"), [5, 6])
        for header in ["Fitness Centers", "Hours*", "Days and Times"]:
            self.assertIsNone(parse_days(header), header)

    def test_normalize_hours(self):
        self.assertEqual(normalize_hours("6:00am–8:15am\n\n12:00pm–2:00pm"), "6:00am - 8:15am\n12:00pm - 2:00pm")
        self.assertEqual(normalize_hours("6am-noon"), "6:00am - 12:00pm")
        for text in ["", "Closed when in use by PE", "Women Only 10:00am–11:00am"]:
            self.assertIsNone(normalize_hours(text), text)

    def test_check_hours(self):
        self.assertIsNone(check_hours("5:00pm - 1:00am"))
        self.assertIsNotNone(check_hours("9:00am - 9:00am"))
        self.assertIsNotNone(check_hours("1:00am - 11:00pm"))

    def test_parse_date_range(self):
        self.assertEqual(
            parse_date_range("December 28 - January 3, 2027"), (datetime(2026, 12, 28), datetime(2027, 1, 3))
        )
        self.assertEqual(parse_date_range("Nov 23 - 25, 2026"), (datetime(2026, 11, 23), datetime(2026, 11, 25)))
        self.assertEqual(parse_date_range("Labor Day: September 7, 2026"), (datetime(2026, 9, 7), datetime(2026, 9, 7)))
        self.assertIsNone(parse_date_range("Regular Semester Hours"))

    def test_rowspan(self):
        html = """
        <table>
          <tr><th>Gym</th><th>Monday</th><th>Tuesday</th></tr>
          <tr><td>A</td><td>6:00am - 9:00pm</td><td rowspan="2">Closed</td></tr>
          <tr><td>B</td><td>7:00am - 8:00pm</td></tr>
        </table>
        """
        rows = parse_hours_tables(html)[0]["rows"]
        self.assertEqual(normalize_hours(rows[1]["days"][1]), "Closed")


def page(html):
    response = mock.Mock(text=html)
    response.raise_for_status.return_value = None
    return response


@mock.patch("src.scrapers.web_hours_scraper.requests.get")
class TestFetchSpecialFitnessRows(unittest.TestCase):
    """None means "keep the sheet's special hours"; a list replaces them."""

    def test_returns_website_rows(self, get):
        get.return_value = page(fixture("cornell-fitness-centers.html"))
        self.assertEqual(len(fetch_web_special_fitness_rows()), 5)

    def test_page_without_hours_tables_keeps_sheet(self, get):
        get.return_value = page("<html><body><p>Under maintenance</p></body></html>")
        self.assertIsNone(fetch_web_special_fitness_rows())

    def test_request_and_parse_failures_are_logged_differently(self, get):
        get.side_effect = requests.ConnectionError()
        with self.assertLogs("src.scrapers.web_hours_scraper", "ERROR") as logs:
            self.assertIsNone(fetch_web_special_fitness_rows())
        self.assertIn("Could not load", logs.output[0])

        get.side_effect = None
        get.return_value = page(fixture("cornell-fitness-centers.html"))
        with mock.patch("src.scrapers.web_hours_scraper.parse_hours_tables", side_effect=ValueError):
            with self.assertLogs("src.scrapers.web_hours_scraper", "ERROR") as logs:
                self.assertIsNone(fetch_web_special_fitness_rows())
        self.assertIn("Could not parse", logs.output[0])


class TestMergeRegularRows(unittest.TestCase):
    def test_website_days_replace_only_matching_sheet_days(self):
        sheet = [
            {"Name": "Teagle", "Monday": "7am - 10pm", "Sunday": "12pm - 5pm"},
            {"Name": "HNH Pool", "Type": "P", "Monday": "6am - 8am"},
        ]
        merged = by_name(merge_regular_rows(sheet, [{"Name": "Teagle", "Monday": "7:00am - 11:00pm"}]))

        self.assertEqual(merged["Teagle"]["Monday"], "7:00am - 11:00pm")
        self.assertEqual(merged["Teagle"]["Sunday"], "12pm - 5pm")
        self.assertEqual(merged["HNH Pool"], sheet[1])
        self.assertEqual(sheet[0]["Monday"], "7am - 10pm", "sheet records should not be modified")

    def test_facility_missing_from_sheet_needs_every_day(self):
        partial = {"Name": "Morrison Fitness Center", "Monday": "5:00pm - 11:00pm"}
        complete = {"Name": "Morrison Fitness Center", **{day: "Closed" for day in DAYS_OF_WEEK}}

        self.assertEqual(merge_regular_rows([], [partial]), [])
        self.assertEqual(merge_regular_rows([], [complete]), [complete])


if __name__ == "__main__":
    unittest.main()
