from datetime import datetime
import threading
import constants
import scraper
from schema import Data

def start_update():
  print('[{0}] Updating data'.format(datetime.now()))
  gyms = constants.GYMS_BY_ID
  class_details, classes = scraper.scrape_classes(constants.PAGE_LIMIT)
  Data.update_data(gyms=gyms, classes=classes, class_details=class_details)
  threading.Timer(constants.UPDATE_DELAY, start_update).start()

start_update()
