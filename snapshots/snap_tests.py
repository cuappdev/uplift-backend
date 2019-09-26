# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestQuery::test_gyms 1"] = {
    "data": {
        "gyms": [
            {
                "name": "Helen Newman",
                "times": [
                    {"day": 0, "endTime": "23:30:00", "startTime": "10:00:00"},
                    {"day": 1, "endTime": "23:30:00", "startTime": "06:00:00"},
                    {"day": 2, "endTime": "23:30:00", "startTime": "06:00:00"},
                    {"day": 3, "endTime": "23:30:00", "startTime": "06:00:00"},
                    {"day": 4, "endTime": "23:30:00", "startTime": "06:00:00"},
                    {"day": 5, "endTime": "23:30:00", "startTime": "06:00:00"},
                    {"day": 6, "endTime": "22:00:00", "startTime": "10:00:00"},
                ],
            },
            {
                "name": "Appel",
                "times": [
                    {"day": 0, "endTime": "13:00:00", "startTime": "09:00:00"},
                    {"day": 1, "endTime": "23:30:00", "startTime": "15:00:00"},
                    {"day": 2, "endTime": "23:30:00", "startTime": "15:00:00"},
                    {"day": 3, "endTime": "23:30:00", "startTime": "15:00:00"},
                    {"day": 4, "endTime": "23:30:00", "startTime": "15:00:00"},
                    {"day": 5, "endTime": "23:30:00", "startTime": "15:00:00"},
                    {"day": 6, "endTime": "13:00:00", "startTime": "09:00:00"},
                ],
            },
            {
                "name": "Noyes",
                "times": [
                    {"day": 0, "endTime": "23:30:00", "startTime": "11:30:00"},
                    {"day": 1, "endTime": "23:30:00", "startTime": "07:00:00"},
                    {"day": 2, "endTime": "23:30:00", "startTime": "07:00:00"},
                    {"day": 3, "endTime": "23:30:00", "startTime": "07:00:00"},
                    {"day": 4, "endTime": "23:30:00", "startTime": "07:00:00"},
                    {"day": 5, "endTime": "23:30:00", "startTime": "07:00:00"},
                    {"day": 6, "endTime": "22:00:00", "startTime": "11:30:00"},
                ],
            },
            {
                "name": "Teagle Up",
                "times": [
                    {"day": 0, "endTime": "17:45:00", "startTime": "12:00:00"},
                    {"day": 1, "endTime": "22:45:00", "startTime": "07:00:00"},
                    {"day": 2, "endTime": "22:45:00", "startTime": "07:00:00"},
                    {"day": 3, "endTime": "22:45:00", "startTime": "07:00:00"},
                    {"day": 4, "endTime": "22:45:00", "startTime": "07:00:00"},
                    {"day": 5, "endTime": "20:00:00", "startTime": "07:00:00"},
                    {"day": 6, "endTime": "17:45:00", "startTime": "12:00:00"},
                ],
            },
            {
                "name": "Teagle Down",
                "times": [
                    {"day": 0, "endTime": "17:45:00", "startTime": "12:00:00"},
                    {"day": 1, "endTime": "22:45:00", "startTime": "07:00:00"},
                    {"day": 2, "endTime": "22:45:00", "startTime": "07:00:00"},
                    {"day": 3, "endTime": "22:45:00", "startTime": "07:00:00"},
                    {"day": 4, "endTime": "22:45:00", "startTime": "07:00:00"},
                    {"day": 5, "endTime": "20:00:00", "startTime": "07:00:00"},
                    {"day": 6, "endTime": "17:45:00", "startTime": "12:00:00"},
                ],
            },
        ]
    }
}
