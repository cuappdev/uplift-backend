import os

# URL for Uplift image assets
ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"

# The path for capacities
C2C_URL = "https://connect2concepts.com/connect2/?type=bar&key=355de24d-d0e4-4262-ae97-bc0c78b92839&loc_status=false"

# The marker for counts in the HTML
CAPACITY_MARKER_COUNTS = "Last Count: "

# The marker for each facility name in the HTML
CAPACITY_MARKER_NAMES = {
    "Helen Newman Fitness Center": "HNH Fitness Center",
    "Noyes Fitness Center": "Noyes Fitness Center",
    "Teagle Down Fitness Center": "Teagle Down Fitness Center",
    "Teagle Up Fitness Center": "Teagle Up Fitness Center",
    "Toni Morrison Fitness Center": "Morrison Fitness Center",
    "HNH Court 1 Basketball": "HNH Court 1",
    "HNH Court 2 Volleyball/Badminton": "HNH Court 2",
    "Noyes Court Basketball": "Noyes Court",
}

# The marker for percent in the HTML
CAPACITY_MARKER_PERCENT = "%"

# The marker for missing percent in the HTML
CAPACITY_MARKER_PERCENT_NA = "NA"

# The marker for last updated in the HTML
CAPACITY_MARKER_UPDATED = "Updated: "

# Days of the week used in the spreadsheet
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Eastern Timezone
EASTERN_TIMEZONE = "America/New_York"

# The path for general gym hours
GYM_HOUR_BASE_URL = "https://scl.cornell.edu/recreation/cornell-fitness-centers"

# The path for Helen Newman Fitness Center details
HNH_DETAILS = "https://scl.cornell.edu/recreation/facility/helen-newman-fitness-center"

# Marker in sheets for alternating between badminton and volleyball (HNH Fridays)
MARKER_ALT = "(ALT)"

# Marker in sheets for badminton court
MARKER_BADMINTON = "(BAD)"

# Marker in sheets for basketball court
MARKER_BASKETBALL = "(BAS)"

# Marker in sheets for Bowling type
MARKER_BOWLING = "B"

# Marker in sheets for closed hours (closed for the day)
MARKER_CLOSED = "Closed"

# Marker in sheets for Court type
MARKER_COURT = "C"

# Marker in sheets for Fitness Center type
MARKER_FITNESS = "FC"

# Marker in sheets for Pool type
MARKER_POOL = "P"

# Marker in sheets for shallow pool
MARKER_SHALLOW = "(S)"

# Marker in sheets to delimit multiple hours (time blocks)
MARKER_TIME_DELIMITER = "\n"

# Marker in sheets for volleyball court
MARKER_VOLLEYBALL = "(VOL)"

# Marker in sheets for women pool
MARKER_WOMEN = "(W)"

# The path for Morrison Fitness Center details
MORRISON_DETAILS = "https://scl.cornell.edu/recreation/facility/toni-morrison-fitness-center"

# The path for Noyes Fitness Center details
NOYES_DETAILS = "https://scl.cornell.edu/recreation/facility/noyes-fitness-center"

# The number of seconds in a day
SECONDS_IN_DAY = 86400

# Path to service account key for scraping sheets
SERVICE_ACCOUNT_PATH = os.environ["GOOGLE_SERVICE_ACCOUNT_PATH"]

# Worksheet name for capacities
SHEET_CAPACITIES = "Capacities"

# Identifier for the Google Sheet
if os.environ["FLASK_ENV"] == "production":
    SHEET_KEY = "1jhNvSxUuHZuNr3mjvlRTbosFkSE4RiaBRDbi4bcdssY"
else:
    SHEET_KEY = "1PKBoOl4UvnjcV1MVihIQl4PklHNO9K8haiQQ_s--NGI"

# Worksheet name for regular building hours
SHEET_REG_BUILDING = "[REG] Building Hours"

# Worksheet name for regular facility hours
SHEET_REG_FACILITY = "[REG] Facility Hours"

# Worksheet name for special facility hours
SHEET_SP_FACILITY = "[SP] Facility Hours"

# The path for Teagle Down Fitness Center details
TEAGLE_DOWN_DETAILS = "https://scl.cornell.edu/recreation/facility/teagle-downstairs"

# The path for Teagle Up Fitness Center details
TEAGLE_UP_DETAILS = "https://scl.cornell.edu/recreation/facility/teagle-upstairs"


