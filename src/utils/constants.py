# URL for Uplift image assets
ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"

# Eastern Timezone
EASTERN_TIMEZONE = "America/New_York"

# Dictionary of Facility IDs
FACILITY_ID_DICT = {
    "hnh_fitness": 1,
    "hnh_pool": 2,
    "hnh_bowling": 3,
    "hnh_court1": 4,
    "hnh_court2": 5,
    "morr_fitness": 6,
    "noyes_fitness": 7,
    "noyes_court": 8,
    "tgl_up": 9,
    "tgl_down": 10,
    "tgl_pool": 11,
}

# Note that we need to subtract by an offset of 1
FACILITY_ROW_OFFSET = 1

# Dictionary of Facility row number in sheets
FACILITY_ROW_DICT = {
    "fc_hnh": 3 - FACILITY_ROW_OFFSET,
    "fc_noyes": 4 - FACILITY_ROW_OFFSET,
    "fc_tgl_down": 5 - FACILITY_ROW_OFFSET,
    "fc_tgl_up": 6 - FACILITY_ROW_OFFSET,
    "fc_morr": 7 - FACILITY_ROW_OFFSET,
    "pool_hnh": 8 - FACILITY_ROW_OFFSET,
    "pool_tgl": 9 - FACILITY_ROW_OFFSET,
    "court_hnh_1": 10 - FACILITY_ROW_OFFSET,
    "court_hnh_2": 11 - FACILITY_ROW_OFFSET,
    "court_noyes": 12 - FACILITY_ROW_OFFSET,
    "bowling_hnh": 13 - FACILITY_ROW_OFFSET,
}

# Dictionary of Gym IDs
GYM_ID_DICT = {"hnh": 1, "morrison": 2, "noyes": 3, "teagle": 4}

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

# Path to service account key for scraping sheets
SERVICE_ACCOUNT_PATH = "service-account-key.json"

# Worksheet name for capacities
SHEET_CAPACITIES = "Capacities"

# Identifier for the Google Sheet
SHEET_KEY = "1luODvvGKe7-qerJ4-7mM1o1oiIuP26m5Z_2P-SRxxlY"

# Worksheet name for regular building hours
SHEET_REG_BUILDING = "[REG] Building Hours"

# Worksheet name for regular facility hours
SHEET_REG_FACILITY = "[REG] Facility Hours"

# Worksheet name for special facility hours
SHEET_SP_FACILITY = "[SP] Facility Hours"
