import csv
import datetime as dt
import calendar

from src.schema import DayTimeRangeType, GymType, TagType, EquipmentType, FacilityType
from src.utils import generate_id

ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"

"""
Weekday indexing: 0 is Sunday, 1 is Monday, ... etc.
"""


def parse_class_metadata():
    tags = {}
    categories = {}
    with open("src/data/class_metadata.csv", "r") as metadata_file:
        reader = csv.reader(metadata_file)
        next(reader)
        for row in reader:
            class_name = row[0]
            tags[class_name] = [TAGS_BY_LABEL[label] for label in row[1].split(",")]
            categories[class_name] = row[2].split(",")
    return tags, categories


def parse_gym_metadata():
    with open("src/data/gym_metadata.csv", "r") as metadata_file:
        reader = csv.reader(metadata_file)
        appel = GymType(
            id=generate_id("Appel"),
            name="Appel",
            description="description",
            facilities=[],
            popular=[
                [0, 0, 0, 0, 0, 0, 15, 25, 27, 22, 21, 31, 47, 53, 45, 34, 36, 52, 70, 75, 60, 35, 14, 0],
                [0, 0, 0, 0, 0, 0, 16, 26, 36, 45, 50, 50, 46, 40, 38, 42, 52, 59, 59, 56, 51, 36, 15, 0],
                [0, 0, 0, 0, 0, 0, 17, 23, 23, 17, 14, 23, 40, 50, 45, 35, 33, 42, 52, 55, 47, 33, 17, 5],
                [0, 0, 0, 0, 0, 0, 12, 20, 28, 34, 37, 37, 37, 39, 47, 57, 67, 70, 62, 47, 34, 32, 26, 5],
                [0, 0, 0, 0, 0, 0, 19, 25, 21, 17, 19, 26, 34, 38, 38, 40, 46, 56, 64, 64, 54, 37, 20, 6],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 26, 44, 42, 30, 29, 35, 42, 43, 38, 28, 17, 80, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 19, 31, 32, 23, 26, 43, 59, 57, 51, 51, 47, 34, 17, 3, 0],
            ],
            image_url=ASSET_BASE_URL + "gyms/Appel.jpg",
        )
        helen_newman = GymType(
            id=generate_id("Helen Newman"),
            name="Helen Newman",
            description="description",
            facilities=[],
            popular=[
                [0, 0, 0, 0, 0, 0, 15, 25, 27, 22, 21, 31, 47, 53, 45, 34, 36, 52, 70, 75, 60, 35, 14, 0],
                [0, 0, 0, 0, 0, 0, 16, 26, 36, 45, 50, 50, 46, 40, 38, 42, 52, 59, 59, 56, 51, 36, 15, 0],
                [0, 0, 0, 0, 0, 0, 17, 23, 23, 17, 14, 23, 40, 50, 45, 35, 33, 42, 52, 55, 47, 33, 17, 5],
                [0, 0, 0, 0, 0, 0, 12, 20, 28, 34, 37, 37, 37, 39, 47, 57, 67, 70, 62, 47, 34, 32, 26, 5],
                [0, 0, 0, 0, 0, 0, 19, 25, 21, 17, 19, 26, 34, 38, 38, 40, 46, 56, 64, 64, 54, 37, 20, 6],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 26, 44, 42, 30, 29, 35, 42, 43, 38, 28, 17, 80, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 19, 31, 32, 23, 26, 43, 59, 57, 51, 51, 47, 34, 17, 3],
            ],
            image_url=ASSET_BASE_URL + "gyms/Helen_Newman.jpg",
        )
        noyes = GymType(
            id=generate_id("Noyes"),
            name="Noyes",
            description="description",
            facilities=[],
            popular=[
                [0, 0, 0, 0, 0, 0, 0, 4, 11, 20, 26, 26, 24, 24, 29, 39, 48, 51, 48, 47, 52, 52, 38, 17],
                [0, 0, 0, 0, 0, 0, 0, 8, 13, 17, 17, 17, 20, 27, 36, 45, 50, 51, 51, 56, 64, 67, 55, 33],
                [0, 0, 0, 0, 0, 0, 0, 5, 11, 18, 23, 23, 20, 20, 26, 38, 48, 56, 63, 71, 70, 56, 34, 14],
                [0, 0, 0, 0, 0, 0, 0, 9, 16, 21, 21, 17, 13, 16, 26, 41, 53, 54, 51, 55, 67, 69, 51, 24],
                [0, 0, 0, 0, 0, 0, 0, 2, 7, 14, 17, 17, 15, 19, 32, 50, 58, 56, 51, 52, 52, 45, 30, 15],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 36, 46, 56, 58, 50, 47, 53, 58, 50, 35, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 36, 44, 39, 33, 38, 45, 52, 63, 75, 70, 45, 18],
            ],
            image_url=ASSET_BASE_URL + "gyms/Noyes.jpg",
        )
        teagle_up = GymType(
            id=generate_id("Teagle Up"),
            name="Teagle Up",
            description="description",
            facilities=[],
            popular=[
                [0, 0, 0, 0, 0, 0, 0, 14, 27, 41, 53, 60, 58, 50, 44, 45, 56, 69, 74, 64, 43, 22, 80, 0],
                [0, 0, 0, 0, 0, 0, 0, 16, 26, 35, 43, 53, 63, 67, 61, 53, 50, 52, 51, 44, 30, 16, 6, 0],
                [0, 0, 0, 0, 0, 0, 0, 21, 46, 38, 40, 58, 62, 48, 34, 35, 51, 68, 75, 65, 47, 26, 11, 0],
                [0, 0, 0, 0, 0, 0, 0, 16, 26, 37, 46, 52, 53, 52, 51, 53, 53, 47, 45, 58, 59, 32, 7, 0],
                [0, 0, 0, 0, 0, 0, 0, 12, 26, 32, 38, 48, 56, 54, 50, 52, 53, 44, 26, 11, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 17, 27, 36, 41, 36, 24, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 13, 21, 24, 34, 36, 14, 0, 0, 0, 0, 0],
            ],
            image_url=ASSET_BASE_URL + "gyms/Teagle.jpg",
        )
        teagle_down = GymType(
            id=generate_id("Teagle Down"),
            name="Teagle Down",
            description="description",
            facilities=[],
            popular=[
                [0, 0, 0, 0, 0, 0, 0, 14, 27, 41, 53, 60, 58, 50, 44, 45, 56, 69, 74, 64, 43, 22, 80, 0],
                [0, 0, 0, 0, 0, 0, 0, 16, 26, 35, 43, 53, 63, 67, 61, 53, 50, 52, 51, 44, 30, 16, 6, 0],
                [0, 0, 0, 0, 0, 0, 0, 21, 46, 38, 40, 58, 62, 48, 34, 35, 51, 68, 75, 65, 47, 26, 11, 0],
                [0, 0, 0, 0, 0, 0, 0, 16, 26, 37, 46, 52, 53, 52, 51, 53, 53, 47, 45, 58, 59, 32, 7, 0],
                [0, 0, 0, 0, 0, 0, 0, 12, 26, 32, 38, 48, 56, 54, 50, 52, 53, 44, 26, 11, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 17, 27, 36, 41, 36, 24, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 13, 21, 24, 34, 36, 14, 0, 0, 0, 0, 0],
            ],
            image_url=ASSET_BASE_URL + "gyms/Teagle.jpg",
        )
        gyms = [appel, helen_newman, noyes, teagle_up, teagle_down]
        days = dict(zip(calendar.day_name, range(7)))
        for row in reader:
            for gym in gyms:
                if gym.name == row[0]:
                    facility_name = row[1]
                    category = row[2]
                    found = False
                    for facility in gym.facilities:
                        if facility.name == facility_name:
                            new_facility = facility
                            found = True
                    if not found:
                        new_facility = FacilityType(
                            equipment=[], misc_information=[], name=row[1], phone_number="", times=[]
                        )
                    if category == "Hours":
                        try:
                            end_time = dt.datetime.strptime(row[6], "%I:%M %p").time()
                            start_time = dt.datetime.strptime(row[5], "%I:%M %p").time()
                        except:
                            end_time = dt.time(0)
                            start_time = dt.time(0)
                        time = DayTimeRangeType(
                            day=(days[row[4]] + 1) % 7, end_time=end_time, restrictions=row[7], start_time=start_time
                        )
                        new_facility.times.append(time)
                    elif category == "Equipment":
                        equipment = EquipmentType(
                            equipment_type=row[8], name=row[9], quantity=row[10], workout_type=row[11]
                        )
                        new_facility.equipment.append(equipment)
                    elif category == "Phone Number":
                        new_facility.phone_number = row[3]
                    elif category == "Misc Information":
                        new_facility.misc_information.append(row[12])
                    if not found:
                        gym.facilities.append(new_facility)
    return gyms


GYMS = parse_gym_metadata()

GYMS_BY_ID = {gym.id: gym for gym in GYMS}

TAGS_BY_LABEL = {
    label: TagType(label=label, image_url=ASSET_BASE_URL + "class_tags/" + label.lower() + ".png")
    for label in ["Cardio", "Intensity", "Strength", "Zen", "Toning", "Energy"]
}


TAGS_BY_CLASS_NAME, CATEGORIES_BY_CLASS_NAME = parse_class_metadata()

PAGE_LIMIT = 10
UPDATE_DELAY = 3600
CLASS_HISTORY_LIMIT = 4

CLASS_IMAGE_KEYWORDS = [
    "Abs",
    "Barre",
    "Chi",
    "Dance",
    "H.I.I.T",
    "OULA",
    "Pilates",
    "Pump",
    "ShockWave",
    "Spinning",
    "Strength",
    "TRX",
    "Yoga",
    "ZUMBA",
]

IMAGE_CHOICES = {"General": 2, "Yoga": 3}
