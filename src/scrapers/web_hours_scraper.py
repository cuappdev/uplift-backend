"""Scrape fitness center, building, and bowling hours from the Cornell Recreation website.

The functions here return rows shaped like the hours worksheets (name, type,
date range, and one column per weekday, with time ranges joined by
MARKER_TIME_DELIMITER), so the existing hours scrapers store them exactly as
they store sheet rows.

Only values that parse cleanly and look plausible are returned. Anything else is
logged and left out, so the caller can keep the sheet's value instead.
"""

import logging
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.scrapers.scraper_helpers import get_hours_datetimes
from src.utils.constants import (
    BOWLING_HOURS_URL,
    DAYS_OF_WEEK,
    GYM_HOUR_BASE_URL,
    HOURS_LATEST_CLOSING_HOUR,
    HOURS_MAX_OPEN_HOURS,
    HOURS_REQUEST_TIMEOUT_SECONDS,
    MARKER_BOWLING,
    MARKER_CLOSED,
    MARKER_FITNESS,
    MARKER_TIME_DELIMITER,
    SHEET_COLUMN_DATE_RANGE,
    SHEET_COLUMN_NAME,
    SHEET_COLUMN_TYPE,
    SHEET_DATE_FORMAT,
    WEB_BOWLING_FACILITY,
    WEB_BUILDING_PAGES,
    WEB_FITNESS_CENTER_LABELS,
    WEB_FITNESS_CENTER_URLS,
    WEB_REGULAR_CAPTION_WORDS,
)

logger = logging.getLogger(__name__)

_TIME = r"\d{1,2}(?::\d{2})?(?:am|pm)"
_TIME_RANGE_RE = re.compile(r"^(%s)-(%s)$" % (_TIME, _TIME))

_MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
# "November 23, 2026 - November 29, 2026" or "December 28 - January 3, 2027"
_DATE_RANGE_RE = re.compile(
    r"(%s)\s+(\d{1,2})(?:,?\s+(\d{4}))?\s*-\s*(%s)\s+(\d{1,2}),?\s+(\d{4})" % (_MONTH, _MONTH), re.IGNORECASE
)
# "November 23 - 29, 2026"
_SAME_MONTH_RANGE_RE = re.compile(r"(%s)\s+(\d{1,2})\s*-\s*(\d{1,2}),?\s+(\d{4})" % _MONTH, re.IGNORECASE)
# "November 27, 2026"
_SINGLE_DATE_RE = re.compile(r"(%s)\s+(\d{1,2}),?\s+(\d{4})" % _MONTH, re.IGNORECASE)


# MARK: Text parsing


def _normalize_text(text):
    """Collapse whitespace and turn en dashes, em dashes, and minus signs into hyphens."""
    text = text.replace("\xa0", " ").replace("–", "-").replace("—", "-").replace("−", "-")
    return re.sub(r"[ \t]+", " ", text).strip()


def _day_index(word):
    """Return the weekday index (Monday is 0) for a day name like "Tues" or "Mondays"."""
    word = word.strip().rstrip("s")
    if len(word) < 3 or not word.isalpha():
        return None
    return next((i for i, day in enumerate(DAYS_OF_WEEK) if day.lower().startswith(word)), None)


def _day_span(start, end):
    """Weekday indices from start to end inclusive, wrapping past Sunday."""
    return [(start + offset) % 7 for offset in range((end - start) % 7 + 1)]


def parse_days(header):
    """
    Return the weekday indices a table header covers, or None if it isn't a day header.

    Handles "Monday", "Mondays", "Monday - Thursday", "Thursday - Sunday",
    "Weekdays", "Weekend", and lists like "Saturday & Sunday".
    """
    text = _normalize_text(header).lower().rstrip("*").strip()
    if re.fullmatch(r"week ?days?", text):
        return _day_span(0, 4)
    if re.fullmatch(r"week ?ends?", text):
        return _day_span(5, 6)

    days = []
    for part in filter(None, re.split(r"\s*(?:,|&|/|\band\b)\s*", text)):
        bounds = [_day_index(bound) for bound in part.split("-")]
        if len(bounds) > 2 or None in bounds:
            return None
        days.extend(_day_span(bounds[0], bounds[-1]))
    return days or None


def _canonical_time(time_str):
    """Write a time like "6am" or "6:30pm" as "6:00am" or "6:30pm"."""
    hour, _, minute = time_str[:-2].partition(":")
    return "%d:%s%s" % (int(hour), minute or "00", time_str[-2:])


def normalize_hours(text):
    """
    Convert a cell like "7:00am - 9:30am / 12:00pm - 10:30pm" to the sheet format.

    Returns MARKER_CLOSED for closed days, time ranges joined by
    MARKER_TIME_DELIMITER, or None if the text isn't a plain list of hours.
    """
    if text is None:
        return None
    text = _normalize_text(str(text)).lower()
    text = text.replace("a.m.", "am").replace("p.m.", "pm").replace("noon", "12:00pm").replace("midnight", "12:00am")

    parts = [re.sub(r"\s+", "", part).rstrip("*") for part in re.split(r"\n|/|,|;", text)]
    parts = [part for part in parts if part]
    if parts == [MARKER_CLOSED.lower()]:
        return MARKER_CLOSED

    matches = [_TIME_RANGE_RE.match(part) for part in parts]
    if not matches or not all(matches):
        return None
    return MARKER_TIME_DELIMITER.join(
        "%s - %s" % (_canonical_time(match.group(1)), _canonical_time(match.group(2))) for match in matches
    )


def check_hours(value):
    """Return None if normalized hours look plausible, otherwise the reason they don't."""
    if value == MARKER_CLOSED:
        return None

    reference_day = datetime(2000, 1, 3)
    for time_range in value.split(MARKER_TIME_DELIMITER):
        try:
            start, end = get_hours_datetimes(time_range, reference_day)
        except (ValueError, IndexError) as error:
            # get_hours_datetimes raises IndexError when the start and end text are identical
            return "could not parse %r: %s" % (time_range, error)
        if end <= start:
            return "%r does not end after it starts" % time_range
        if end - start > timedelta(hours=HOURS_MAX_OPEN_HOURS):
            return "%r is open longer than %d hours" % (time_range, HOURS_MAX_OPEN_HOURS)
        if end.date() > start.date() and (end.hour, end.minute) > (HOURS_LATEST_CLOSING_HOUR, 0):
            return "%r closes later than %d:00am the next day" % (time_range, HOURS_LATEST_CLOSING_HOUR)
    return None


def _parse_date(month, day, year):
    return datetime.strptime("%s %s %s" % (month[:3].title(), day, year), "%b %d %Y")


def parse_date_range(text):
    """
    Return (start, end) datetimes for text like "November 23, 2026 - November 29, 2026 - Thanksgiving Break Hours".

    Returns None if the text has no date.
    """
    text = _normalize_text(text)

    match = _DATE_RANGE_RE.search(text)
    if match:
        start_month, start_day, start_year, end_month, end_day, end_year = match.groups()
        start = _parse_date(start_month, start_day, start_year or end_year)
        end = _parse_date(end_month, end_day, end_year)
        if start > end and not start_year:
            start = start.replace(year=start.year - 1)
    elif _SAME_MONTH_RANGE_RE.search(text):
        month, start_day, end_day, year = _SAME_MONTH_RANGE_RE.search(text).groups()
        start, end = _parse_date(month, start_day, year), _parse_date(month, end_day, year)
    elif _SINGLE_DATE_RE.search(text):
        start = end = _parse_date(*_SINGLE_DATE_RE.search(text).groups())
    else:
        return None

    return (start, end) if start <= end else None


def _format_date_range(date_range):
    start, end = date_range
    return "%s - %s" % (start.strftime(SHEET_DATE_FORMAT), end.strftime(SHEET_DATE_FORMAT))


# MARK: HTML parsing


def _span(cell, attribute):
    try:
        return max(1, int(cell.get(attribute, 1)))
    except (TypeError, ValueError):
        return 1


def _table_grid(table):
    """Expand a table into a grid of cells, repeating cells that span several rows or columns."""
    grid = {}
    rows = table.find_all("tr")
    for r, row in enumerate(rows):
        c = 0
        for cell in row.find_all(["th", "td"], recursive=False):
            while (r, c) in grid:
                c += 1
            for dr in range(_span(cell, "rowspan")):
                for dc in range(_span(cell, "colspan")):
                    grid[(r + dr, c + dc)] = cell
            c += _span(cell, "colspan")

    if not grid:
        return []
    n_cols = max(c for _, c in grid) + 1
    return [[grid.get((r, c)) for c in range(n_cols)] for r in range(len(rows))]


def _cell_text(cell):
    return _normalize_text(cell.get_text()) if cell is not None else ""


def _raw_cell_text(cell):
    """Cell text with line breaks kept, for splitting several time ranges in one cell."""
    return cell.get_text() if cell is not None else ""


def _cell_href(cell):
    link = cell.find("a", href=True) if cell is not None else None
    return link["href"].strip() if link else None


def _parse_soup(html):
    """Parse HTML, turning <br> and block ends into line breaks so cells keep one time range per line."""
    soup = BeautifulSoup(html, "lxml")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for block in soup.find_all(["p", "div", "li"]):
        block.append("\n")
    return soup


def _rows_with_days_across(grid, column_days):
    """One row per facility, with day headers across the top (fitness centers, buildings)."""
    rows = []
    for grid_row in grid[1:]:
        days = {}
        for cell, cell_days in zip(grid_row, column_days):
            for day in cell_days or []:
                days[day] = _raw_cell_text(cell)
        rows.append({"label": _cell_text(grid_row[0]), "href": _cell_href(grid_row[0]), "days": days})
    return rows


def _row_with_days_down(grid):
    """The whole table as one facility, with days down the first column (bowling)."""
    days = {}
    for grid_row in grid[1:]:
        for day in parse_days(_cell_text(grid_row[0])):
            days[day] = _raw_cell_text(grid_row[1])
    return [{"label": _cell_text(grid[0][0]), "href": None, "days": days}]


def parse_hours_tables(html):
    """
    Return every hours table on a page.

    Each table is a dict with:
        - `caption`     The table caption text.
        - `date_range`  (start, end) datetimes for special hours, or None.
        - `rows`        A list of {"label", "href", "days": {weekday index: cell text}}.

    Tables with neither days across the top nor days down the first column are skipped.
    """
    tables = []
    for table in _parse_soup(html).find_all("table"):
        grid = _table_grid(table)
        if len(grid) < 2:
            continue

        # The first column holds row labels, not days
        column_days = [None] + [parse_days(_cell_text(cell)) for cell in grid[0][1:]]
        if any(column_days):
            rows = _rows_with_days_across(grid, column_days)
        elif all(len(grid_row) > 1 and parse_days(_cell_text(grid_row[0])) for grid_row in grid[1:]):
            rows = _row_with_days_down(grid)
        else:
            continue

        caption = _cell_text(table.find("caption"))
        tables.append({"caption": caption, "date_range": parse_date_range(caption), "rows": rows})
    return tables


def _is_regular(table):
    caption = table["caption"].lower()
    return not table["date_range"] and (not caption or any(word in caption for word in WEB_REGULAR_CAPTION_WORDS))


def _hours_by_day(source, days):
    """Normalize and check each day's hours, leaving out (and logging) any that don't pass."""
    result = {}
    for day, text in sorted(days.items()):
        value = normalize_hours(text)
        problem = "unrecognized hours %r" % _normalize_text(text) if value is None else check_hours(value)
        if problem:
            logger.warning("Skipping %s hours on %s from the website: %s", source, DAYS_OF_WEEK[day], problem)
        else:
            result[DAYS_OF_WEEK[day]] = value
    return result


def _sheet_row(name, hours, facility_type=None, date_range=None):
    """
    Build a sheet-format row.

    Special-hours rows (with a date range) get every weekday column, blank for
    days without hours, because the special hours scraper skips blank days.
    """
    row = {SHEET_COLUMN_NAME: name}
    if facility_type:
        row[SHEET_COLUMN_TYPE] = facility_type
    if date_range:
        row[SHEET_COLUMN_DATE_RANGE] = _format_date_range(date_range)
        row.update({day: hours.get(day, "") for day in DAYS_OF_WEEK})
    else:
        row.update(hours)
    return row


def _url_path(url):
    return urlparse(url).path.rstrip("/")


def _fitness_center_name(row):
    if row["href"]:
        for url, name in WEB_FITNESS_CENTER_URLS.items():
            if _url_path(row["href"]) == _url_path(url):
                return name
    return WEB_FITNESS_CENTER_LABELS.get(row["label"].lower())


def _fitness_center_rows(table):
    rows = []
    for row in table["rows"]:
        name = _fitness_center_name(row)
        if not name:
            logger.warning("Unknown fitness center %r in hours table %r", row["label"], table["caption"])
            continue
        hours = _hours_by_day("%s (%s)" % (name, table["caption"] or "regular"), row["days"])
        rows.append(_sheet_row(name, hours, MARKER_FITNESS, table["date_range"]))
    return rows


def parse_fitness_center_hours(html):
    """
    Parse GYM_HOUR_BASE_URL into (regular_rows, special_rows) in sheet format.

    Regular rows come from the first regular hours table. Special rows come from
    every table with a date range in its caption.
    """
    regular_rows, special_rows = [], []
    for table in parse_hours_tables(html):
        if table["date_range"]:
            special_rows.extend(_fitness_center_rows(table))
        elif not _is_regular(table):
            logger.warning("Ignoring fitness center hours table with no date range: %r", table["caption"])
        elif regular_rows:
            logger.warning("Ignoring extra regular hours table %r on the fitness centers page", table["caption"])
        else:
            regular_rows = _fitness_center_rows(table)
    return regular_rows, special_rows


def parse_building_hours(html, gym_name, label_keyword):
    """Parse a building page into a list with one sheet-format row, or an empty list if none was found."""
    for table in filter(_is_regular, parse_hours_tables(html)):
        for row in table["rows"]:
            if label_keyword in row["label"].lower():
                return [_sheet_row(gym_name, _hours_by_day("%s building" % gym_name, row["days"]))]
    logger.warning("No building hours found on the website for %s", gym_name)
    return []


def parse_bowling_hours(html):
    """Parse BOWLING_HOURS_URL into a list with one sheet-format row, or an empty list if none was found."""
    for table in filter(_is_regular, parse_hours_tables(html)):
        if len(table["rows"]) == 1:
            hours = _hours_by_day(WEB_BOWLING_FACILITY, table["rows"][0]["days"])
            return [_sheet_row(WEB_BOWLING_FACILITY, hours, MARKER_BOWLING)]
    logger.warning("No bowling hours found on the website")
    return []


# MARK: Fetching


def _scrape(url, parse, *args):
    """Fetch a page and parse it, or log the error and return None."""
    try:
        response = requests.get(url, timeout=HOURS_REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Could not load hours page %s", url)
        return None
    try:
        return parse(response.text, *args)
    except Exception:
        logger.exception("Could not parse hours page %s; its layout may have changed", url)
        return None


def fetch_web_regular_facility_rows():
    """Regular fitness center and bowling hours from the website. Pages that fail to load are skipped."""
    fitness_centers = _scrape(GYM_HOUR_BASE_URL, parse_fitness_center_hours)
    regular_rows = fitness_centers[0] if fitness_centers else []
    return regular_rows + (_scrape(BOWLING_HOURS_URL, parse_bowling_hours) or [])


def fetch_web_building_rows():
    """Regular building hours from the website. Pages that fail to load are skipped."""
    rows = []
    for url, gym_name, label_keyword in WEB_BUILDING_PAGES:
        rows.extend(_scrape(url, parse_building_hours, gym_name, label_keyword) or [])
    return rows


def fetch_web_special_fitness_rows():
    """
    Special fitness center hours from the website.

    Returns None if the page couldn't be loaded or parsed, or has no hours
    tables at all, so the sheet's special hours are kept. Returns an empty list
    only when the page has regular hours but no special hours.
    """
    fitness_centers = _scrape(GYM_HOUR_BASE_URL, parse_fitness_center_hours)
    if fitness_centers is None:
        return None
    regular_rows, special_rows = fitness_centers
    if not regular_rows and not special_rows:
        logger.warning("No hours tables found on %s; keeping the sheet's special hours", GYM_HOUR_BASE_URL)
        return None
    return special_rows


# MARK: Merging with the sheet


def merge_regular_rows(sheet_records, web_rows):
    """
    Overlay website hours onto sheet rows with the same name.

    Each day the website provides replaces the sheet's value for that day; days
    the website doesn't provide keep the sheet's value. A facility that isn't in
    the sheet is added only if the website has all seven days. Differences from
    the sheet are logged.
    """
    records = [dict(record) for record in sheet_records]
    by_name = {record.get(SHEET_COLUMN_NAME): record for record in records}

    for web_row in web_rows:
        name = web_row[SHEET_COLUMN_NAME]
        existing = by_name.get(name)
        if existing is None:
            if all(day in web_row for day in DAYS_OF_WEEK):
                by_name[name] = dict(web_row)
                records.append(by_name[name])
            else:
                logger.warning("Skipping website hours for %s: not in the sheet and missing some days", name)
            continue

        for day in DAYS_OF_WEEK:
            if day in web_row and normalize_hours(existing.get(day)) != web_row[day]:
                logger.info(
                    "Website hours for %s on %s differ from the sheet: %r (sheet) -> %r (website)",
                    name,
                    day,
                    existing.get(day),
                    web_row[day],
                )
        existing.update(web_row)
    return records
