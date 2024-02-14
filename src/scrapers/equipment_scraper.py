from bs4 import BeautifulSoup
import requests
from src.database import db_session
from src.models.equipment import Equipment, EquipmentType, AccessibilityType
from src.utils.utils import get_facility_id
from src.utils.constants import (
  HNH_DETAILS,
  NOYES_DETAILS,
  TEAGLE_DOWN_DETAILS,
  TEAGLE_UP_DETAILS,
  MORRISON_DETAILS
)

equip_pages = [HNH_DETAILS, NOYES_DETAILS, TEAGLE_DOWN_DETAILS, TEAGLE_UP_DETAILS, MORRISON_DETAILS]

def categorize_equip(category):
  if "cardio" in category.lower():
    return EquipmentType.cardio
  if "racks" in category.lower() or "benches" in category.lower():
    return EquipmentType.racks_and_benches
  if "selectorized" in category.lower():
    return EquipmentType.selectorized
  if "multi-cable" in category.lower():
    return EquipmentType.multi_cable
  if "free weights" in category.lower():
    return EquipmentType.free_weights
  if "miscellaneous" in category.lower():
    return EquipmentType.miscellaneous
  if "plate" in category.lower():
    return EquipmentType.plate_loaded
  return -1


def create_equip(category, equip, fit_center_id, fit_center):
  """
  Create equipment from a list of equipment.
  """
  equip_list = equip.find_all('li')
  equip_db_objs = []
  for equip in equip_list:
    if "precor ellipticals" in equip.text.lower() and fit_center == "Teagle Up Fitness Center":
      equip_obj = "Precor Ellipticals"
      num_objs = 10
    else:
      equip_obj = equip.text.split(' ')
      num_objs = 0
      if equip_obj[0].isnumeric():
        num_objs = int(equip_obj[0])
        equip_obj = equip_obj[1:]
      equip_obj = ' '.join(equip_obj)
    
    num_objs = None if num_objs == 0 else num_objs
    accessibility_option = None if "wheelchair" not in equip_obj else 1
    equip_type = categorize_equip(category)

    try:
      existing_equip = db_session.query(Equipment).filter(Equipment.name==equip_obj, Equipment.equipment_type==equip_type, Equipment.facility_id==fit_center_id).first()
      assert existing_equip is not None
    except:
      equip_db_obj = Equipment(
        name=equip_obj,
        equipment_type=equip_type,
        facility_id=fit_center_id,
        quantity=num_objs,
        accessibility = AccessibilityType.wheelchair if accessibility_option else None
      )
      equip_db_objs.append(equip_db_obj)
  db_session.add_all(equip_db_objs)
  db_session.commit()



def process_equip_page(page, fit_center):
  """
  Process equipment page.
  """

  soup = BeautifulSoup(requests.get(page).content, 'lxml')
  table = soup.find('table')
  body = table.find_all('tr')
  fit_center_id = get_facility_id(fit_center)
  for even_row in range(0, len(body), 2):
    categories = body[even_row].find_all('th')
    equip = body[even_row + 1].find_all('td')
    if categories[0].text:
      create_equip(categories[0].text, equip[0], fit_center_id, fit_center)
    if categories[1].text:
      create_equip(categories[1].text, equip[1], fit_center_id, fit_center)

def scrape_equipment():
  process_equip_page(HNH_DETAILS, "HNH Fitness Center")
  process_equip_page(NOYES_DETAILS, "Noyes Fitness Center")
  process_equip_page(TEAGLE_DOWN_DETAILS, "Teagle Down Fitness Center")
  process_equip_page(TEAGLE_UP_DETAILS, "Teagle Up Fitness Center")
  process_equip_page(MORRISON_DETAILS, "Morrison Fitness Center")


