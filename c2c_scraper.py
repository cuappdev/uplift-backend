"""
Controller to scrap fitness website, parse html data, and add to Capacity table.
Used by cron job.
"""

from bs4 import BeautifulSoup
import requests
from sqlalchemy import and_
from src.constants import CONNECT2CONCEPTS_PATH, CAPACITY_SCRAPE_INTERVAL
from src.database import init_db, db_session
from src.models.facility import Facility
from src.models.capacity import Capacity 
from src.utils import parse_c2c_datetime
import time

def _scrape_capacity():
  """
  scrape capacity and timestamp and add to capacity model for corresponding gym
  """
  # Get data from C2C module    
  headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0'}
  page = requests.get(CONNECT2CONCEPTS_PATH, headers=headers).text
  soup = BeautifulSoup(page, "lxml")
  data = soup.findAll('div', attrs = {"class":"barChart"})

  # For each section,
  # fitness center / open status / last count / updated (date time) / percent
  for gymData in data:
    lines = list(map(str.strip, filter(lambda v: v != '', gymData.get_text("\n").split("\n"))))

    # Fitness Center
    index = lines[0].find("Fitness Center")
    name = lines[0][0:index].strip()

    # Count
    index = lines[2].find(":")
    count = int(lines[2][index+1:].strip())

    # Last Updated
    index = lines[3].find(":")
    last_updated = parse_c2c_datetime(lines[3][index+1:].strip())

    # Percent
    percent = -1 if lines[4] == "NA" else (int(lines[4][:-1]) / 100)

    facility = Facility.query.filter_by(name=name).first()

    if facility: 
      facility_id = facility.serialize().get("id")

      # If it doesn't exist yet, add to table.
      if not (Capacity.query.filter(and_(Capacity.facility_id==facility_id, Capacity.updated==last_updated)).first()):
        new_capacity = Capacity(
          facility_id = facility_id,
          count=count,
          percent=percent,
          updated=last_updated
        )
        db_session.add(new_capacity)
        db_session.commit()

def run_capacity_scraper():
  print("Starting capacity scraper")
  while True:
    _scrape_capacity()
    time.sleep(60 * CAPACITY_SCRAPE_INTERVAL)

if __name__ == "__main__":
  run_capacity_scraper()