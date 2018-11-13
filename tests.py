import unittest

from graphene import Schema
from graphene.test import Client
from snapshottest import TestCase

from constants import CLASS_HISTORY_LIMIT, GYMS_BY_ID, PAGE_LIMIT
from schema import Data, Query
import scraper

schema = Schema(query=Query)
client = Client(schema)

class TestQuery(TestCase):
  def setUp(self):
    gyms = GYMS_BY_ID
    class_details, classes = scraper.scrape_classes(PAGE_LIMIT)
    Data.update_data(gyms=gyms, classes=classes, class_details=class_details, limit=CLASS_HISTORY_LIMIT)

  def test_gyms(self):
    query = '''
        query GymsQuery {
          gyms {
            name
            times{
              day
              startTime
              endTime
            }
          }
        }
    '''
    self.assert_match_snapshot(client.execute(query))

  def test_classes(self):
    query = '''
        query ClassesInfoQuery {
          classes {
            date
            startTime
            endTime
            isCancelled
          }
        }
    '''
    self.assertIsNotNone(client.execute(query))

if __name__ == '__main__':
  unittest.main()
