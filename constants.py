import csv
import datetime as dt
import hashlib
import os

from schema import DayTimeRangeType, GymType
from utils import generate_id

GYMS = [
    GymType(
        id=generate_id(),
        name='Helen Newman',
        description='description',
        popular=[
            [0, 0, 0, 0, 0, 0, 15, 25, 27, 22, 21, 31, 47, 53, 45, 34, 36, 52, 70, 75, 60, 35, 14, 0],
            [0, 0, 0, 0, 0, 0, 16, 26, 36, 45, 50, 50, 46, 40, 38, 42, 52, 59, 59, 56, 51, 36, 15, 0],
            [0, 0, 0, 0, 0, 0, 17, 23, 23, 17, 14, 23, 40, 50, 45, 35, 33, 42, 52, 55, 47, 33, 17, 5],
            [0, 0, 0, 0, 0, 0, 12, 20, 28, 34, 37, 37, 37, 39, 47, 57, 67, 70, 62, 47, 34, 32, 26, 5],
            [0, 0, 0, 0, 0, 0, 19, 25, 21, 17, 19, 26, 34, 38, 38, 40, 46, 56, 64, 64, 54, 37, 20, 6],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 26, 44, 42, 30, 29, 35, 42, 43, 38, 28, 17, 80, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 19, 31, 32, 23, 26, 43, 59, 57, 51, 51, 47, 34, 17, 3]
        ],
        times=[
            DayTimeRangeType(day=0, start_time=dt.time(6), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=1, start_time=dt.time(6), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=2, start_time=dt.time(6), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=3, start_time=dt.time(6), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=4, start_time=dt.time(6), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=5, start_time=dt.time(10), end_time=dt.time(22)),
            DayTimeRangeType(day=6, start_time=dt.time(10), end_time=dt.time(23, 30))
        ]
    ),
    GymType(
        id=generate_id(),
        name='Appel',
        description='description',
        popular=[
            [0, 0, 0, 0, 0, 0, 15, 25, 27, 22, 21, 31, 47, 53, 45, 34, 36, 52, 70, 75, 60, 35, 14, 0],
            [0, 0, 0, 0, 0, 0, 16, 26, 36, 45, 50, 50, 46, 40, 38, 42, 52, 59, 59, 56, 51, 36, 15, 0],
            [0, 0, 0, 0, 0, 0, 17, 23, 23, 17, 14, 23, 40, 50, 45, 35, 33, 42, 52, 55, 47, 33, 17, 5],
            [0, 0, 0, 0, 0, 0, 12, 20, 28, 34, 37, 37, 37, 39, 47, 57, 67, 70, 62, 47, 34, 32, 26, 5],
            [0, 0, 0, 0, 0, 0, 19, 25, 21, 17, 19, 26, 34, 38, 38, 40, 46, 56, 64, 64, 54, 37, 20, 6],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 26, 44, 42, 30, 29, 35, 42, 43, 38, 28, 17, 80, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 19, 31, 32, 23, 26, 43, 59, 57, 51, 51, 47, 34, 17, 3, 0]
        ],
        times=[
            DayTimeRangeType(day=0, start_time=dt.time(15), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=1, start_time=dt.time(15), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=2, start_time=dt.time(15), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=3, start_time=dt.time(15), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=4, start_time=dt.time(15), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=5, start_time=dt.time(9), end_time=dt.time(13)),
            DayTimeRangeType(day=6, start_time=dt.time(9), end_time=dt.time(13))
        ]
    ),
    GymType(
        id=generate_id(),
        name='Noyes',
        description='description',
        popular=[
            [0, 0, 0, 0, 0, 0, 0, 4, 11, 20, 26, 26, 24, 24, 29, 39, 48, 51, 48, 47, 52, 52, 38, 17],
            [0, 0, 0, 0, 0, 0, 0, 8, 13, 17, 17, 17, 20, 27, 36, 45, 50, 51, 51, 56, 64, 67, 55, 33],
            [0, 0, 0, 0, 0, 0, 0, 5, 11, 18, 23, 23, 20, 20, 26, 38, 48, 56, 63, 71, 70, 56, 34, 14],
            [0, 0, 0, 0, 0, 0, 0, 9, 16, 21, 21, 17, 13, 16, 26, 41, 53, 54, 51, 55, 67, 69, 51, 24],
            [0, 0, 0, 0, 0, 0, 0, 2, 7, 14, 17, 17, 15, 19, 32, 50, 58, 56, 51, 52, 52, 45, 30, 15],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 36, 46, 56, 58, 50, 47, 53, 58, 50, 35, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 36, 44, 39, 33, 38, 45, 52, 63, 75, 70, 45, 18]
        ],
        times=[
            DayTimeRangeType(day=0, start_time=dt.time(7), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=1, start_time=dt.time(7), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=2, start_time=dt.time(7), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=3, start_time=dt.time(7), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=4, start_time=dt.time(7), end_time=dt.time(23, 30)),
            DayTimeRangeType(day=5, start_time=dt.time(11, 30), end_time=dt.time(22)),
            DayTimeRangeType(day=6, start_time=dt.time(11, 30), end_time=dt.time(23, 30))
        ]
    ),
    GymType(
        id=generate_id(),
        name='Teagle Up',
        description='description',
        popular=[
            [0, 0, 0, 0, 0, 0, 0, 14, 27, 41, 53, 60, 58, 50, 44, 45, 56, 69, 74, 64, 43, 22, 80, 0],
            [0, 0, 0, 0, 0, 0, 0, 16, 26, 35, 43, 53, 63, 67, 61, 53, 50, 52, 51, 44, 30, 16, 6, 0],
            [0, 0, 0, 0, 0, 0, 0, 21, 46, 38, 40, 58, 62, 48, 34, 35, 51, 68, 75, 65, 47, 26, 11, 0],
            [0, 0, 0, 0, 0, 0, 0, 16, 26, 37, 46, 52, 53, 52, 51, 53, 53, 47, 45, 58, 59, 32, 7, 0],
            [0, 0, 0, 0, 0, 0, 0, 12, 26, 32, 38, 48, 56, 54, 50, 52, 53, 44, 26, 11, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 17, 27, 36, 41, 36, 24, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 13, 21, 24, 34, 36, 14, 0, 0, 0, 0, 0]
        ],
        times=[
            DayTimeRangeType(day=0, start_time=dt.time(7), end_time=dt.time(22, 45)),
            DayTimeRangeType(day=1, start_time=dt.time(7), end_time=dt.time(22, 45)),
            DayTimeRangeType(day=2, start_time=dt.time(7), end_time=dt.time(22, 45)),
            DayTimeRangeType(day=3, start_time=dt.time(7), end_time=dt.time(22, 45)),
            DayTimeRangeType(day=4, start_time=dt.time(7), end_time=dt.time(20)),
            DayTimeRangeType(day=5, start_time=dt.time(12), end_time=dt.time(17, 45)),
            DayTimeRangeType(day=6, start_time=dt.time(12),end_time=dt.time(17, 45))
        ]
    ),
    GymType(
        id=generate_id(),
        name='Teagle Down',
        description='description',
        popular=[
            [0, 0, 0, 0, 0, 0, 0, 14, 27, 41, 53, 60, 58, 50, 44, 45, 56, 69, 74, 64, 43, 22, 80, 0],
            [0, 0, 0, 0, 0, 0, 0, 16, 26, 35, 43, 53, 63, 67, 61, 53, 50, 52, 51, 44, 30, 16, 6, 0],
            [0, 0, 0, 0, 0, 0, 0, 21, 46, 38, 40, 58, 62, 48, 34, 35, 51, 68, 75, 65, 47, 26, 11, 0],
            [0, 0, 0, 0, 0, 0, 0, 16, 26, 37, 46, 52, 53, 52, 51, 53, 53, 47, 45, 58, 59, 32, 7, 0],
            [0, 0, 0, 0, 0, 0, 0, 12, 26, 32, 38, 48, 56, 54, 50, 52, 53, 44, 26, 11, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 17, 27, 36, 41, 36, 24, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 13, 21, 24, 34, 36, 14, 0, 0, 0, 0, 0]
        ],
        times=[
            DayTimeRangeType(day=0, start_time=dt.time(7), end_time=dt.time(22, 45)),
            DayTimeRangeType(day=1, start_time=dt.time(7), end_time=dt.time(22, 45)),
            DayTimeRangeType(day=2, start_time=dt.time(7), end_time=dt.time(22, 45)),
            DayTimeRangeType(day=3, start_time=dt.time(7), end_time=dt.time(22, 45)),
            DayTimeRangeType(day=4, start_time=dt.time(7), end_time=dt.time(20)),
            DayTimeRangeType(day=5, start_time=dt.time(12), end_time=dt.time(17, 45)),
            DayTimeRangeType(day=6, start_time=dt.time(12), end_time=dt.time(17, 45))
        ]
    )
]

GYMS_BY_ID = {gym.id: gym for gym in GYMS}

def parse_tags():
  result = {}
  with open('tags-grid-view.csv', 'r') as tags:
    reader = csv.reader(tags)
    next(reader)
    for row in reader:
      class_name = row[0]
      result[class_name] = row[1].lower().split(',') + row[2].lower().split(',')
  return result

TAGS_BY_CLASS_NAME = parse_tags()

PAGE_LIMIT = 10
UPDATE_DELAY = 3600
