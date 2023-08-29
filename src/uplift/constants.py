import csv
from schema import TagType

ASSET_BASE_URL = "https://raw.githubusercontent.com/cuappdev/assets/master/uplift/"

TAGS_BY_LABEL = {
    label: TagType(label=label, image_url=ASSET_BASE_URL + "class_tags/" + label.lower() + ".png")
    for label in ["Cardio", "Intensity", "Strength", "Zen", "Toning", "Energy"]
}


def parse_class_metadata():
    tags = {}
    categories = {}
    with open("data/class_metadata.csv", "r") as metadata_file:
        reader = csv.reader(metadata_file)
        next(reader)
        for row in reader:
            class_name = row[0]
            tags[class_name] = [TAGS_BY_LABEL[label] for label in row[1].split(",")]
            categories[class_name] = row[2].split(",")
    return tags, categories


GYMS = parse_gym_metadata()

GYMS_BY_ID = {gym.id: gym for gym in GYMS}

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
