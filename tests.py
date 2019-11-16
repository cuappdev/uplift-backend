import unittest

from graphene import Schema
from graphene.test import Client
from snapshottest import TestCase

from src.constants import CLASS_HISTORY_LIMIT, GYMS_BY_ID, PAGE_LIMIT
from src.schema import Data, Query
import src.data as data
import src.scraper as scraper

schema = Schema(query=Query)
client = Client(schema)


class TestQuery(TestCase):
    def setUp(self):
        gyms = {gym.id: gym for gym in data.check_for_special_hours()}
        class_details, classes = scraper.scrape_classes(PAGE_LIMIT)
        Data.update_data(gyms=gyms, classes=classes, class_details=class_details, limit=CLASS_HISTORY_LIMIT)
        Data.update_pool_hours(gyms, scraper.scrape_pool_hours(gyms))

    def test_gyms(self):
        query = """
        query GymsQuery {
            gyms {
                facilities {
                    name
                    details {
                        detailsType
                        subFacilityNames
                        equipment {
                            name
                        }
                        times {
                            day
                            timeRanges {
                                startTime
                                endTime
                            }
                        }
                        items
                        prices
                    }
                }
            }
        }
    """
        self.assert_match_snapshot(client.execute(query))

    def test_classes(self):
        query = """
        query ClassesInfoQuery {
          classes {
            date
            startTime
            endTime
            isCancelled
          }
        }
    """
        self.assertIsNotNone(client.execute(query))


if __name__ == "__main__":
    unittest.main()
