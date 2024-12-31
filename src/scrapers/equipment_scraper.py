from bs4 import BeautifulSoup
import requests
import json
from src.database import db_session
from src.models.equipment import Equipment, MuscleGroup, AccessibilityType
from src.utils.utils import get_facility_id
from src.utils.constants import HNH_DETAILS, NOYES_DETAILS, TEAGLE_DOWN_DETAILS, TEAGLE_UP_DETAILS, MORRISON_DETAILS

equip_pages = [HNH_DETAILS, NOYES_DETAILS, TEAGLE_DOWN_DETAILS, TEAGLE_UP_DETAILS, MORRISON_DETAILS]

try:
    # Load equipment labels from JSON file
    with open('src/utils/equipment_labels.json') as file:
        data = json.load(file)
except Exception as e:
    raise RuntimeError(f"Failed to load equipment labels: {str(e)}")

def categorize_equip(name):
    try:
        cats = data[name]["label"]
        return [MuscleGroup[cat.replace(" ", "_")] for cat in cats]
    except KeyError:
        return []  # Return empty list if no muscle groups found

def get_clean_name(name):
    try:
        return data[name]["clean_name"]
    except KeyError:
        return name


def create_equip(equip, fit_center_id, fit_center):
    """
    Create equipment from a list of equipment.
    """
    equip_list = equip.find_all("li")
    equip_db_objs = []
    for equip in equip_list:
        if "precor ellipticals" in equip.text.lower() and fit_center == "Teagle Up Fitness Center":
            equip_obj = "Precor Ellipticals"
            num_objs = 10
        else:
            equip_obj = equip.text.split(" ")
            num_objs = 0
            if equip_obj[0].isnumeric():
                num_objs = int(equip_obj[0])
                equip_obj = equip_obj[1:]
            # Strip leading and trailing spaces and replace non-breaking space with regular space after joining
            equip_obj = ((" ".join(equip_obj)).strip()).replace(chr(160), chr(32))
        clean_name = get_clean_name(equip_obj)
        num_objs = None if num_objs == 0 else num_objs
        accessibility_option = None if "wheelchair" not in equip_obj else 1
        muscle_groups = categorize_equip(equip_obj)

        try:
            existing_equip = (
                db_session.query(Equipment)
                .filter(
                    Equipment.name == equip_obj,
                    Equipment.facility_id == fit_center_id,
                )
                .first()
            )
            if existing_equip is not None:
                continue

            equip_db_obj = Equipment(
                name=equip_obj.strip(),
                facility_id=fit_center_id,
                clean_name=clean_name,
                quantity=num_objs,
                accessibility=AccessibilityType.wheelchair if accessibility_option else None,
                muscle_groups=muscle_groups,
            )

            equip_db_objs.append(equip_db_obj)

        except Exception as e:
            print(f"Error creating equipment {equip_obj}: {str(e)}")
            continue

    if equip_db_objs:
        db_session.add_all(equip_db_objs)
        db_session.commit()


def process_equip_page(page, fit_center):
    """
    Process equipment page.
    """

    soup = BeautifulSoup(requests.get(page).content, "lxml")
    fit_center_id = get_facility_id(fit_center)
    table = soup.find("table")
    if fit_center == "Morrison Fitness Center":
        head = table.find("thead").find_all("tr")
        body = table.find("tbody").find_all("tr")
        for row in range(len(head)):
            muscle_groups = head[row].find_all("th")
            equip = body[row].find_all("td")
            if muscle_groups[0].text:
                create_equip(equip[0], fit_center_id, fit_center)
            if muscle_groups[1].text:
                create_equip(equip[1], fit_center_id, fit_center)
    else:
        body = table.find_all("tr")
        for even_row in range(0, len(body), 2):
            muscle_groups = body[even_row].find_all("th")
            equip = body[even_row + 1].find_all("td")
            if muscle_groups[0].text:
                create_equip(equip[0], fit_center_id, fit_center)
            if muscle_groups[1].text:
                create_equip(equip[1], fit_center_id, fit_center)


def scrape_equipment():
    process_equip_page(HNH_DETAILS, "HNH Fitness Center")
    process_equip_page(NOYES_DETAILS, "Noyes Fitness Center")
    process_equip_page(TEAGLE_DOWN_DETAILS, "Teagle Down Fitness Center")
    process_equip_page(TEAGLE_UP_DETAILS, "Teagle Up Fitness Center")
    process_equip_page(MORRISON_DETAILS, "Morrison Fitness Center")
