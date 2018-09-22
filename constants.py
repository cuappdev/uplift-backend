from datetime import datetime as dt

from schema import DayTimeRangeType, GymType

GYMS = {
    'Helen Newman': GymType('Helen Newman',
                            'description',
                            [
                                [19, 31, 32, 23, 26, 43, 59, 57, 51, 51, 47, 34, 17, 3], 
                                [15, 25, 27, 22, 21, 31, 47, 53, 45, 34, 36, 52, 70, 75, 60, 35, 14, 0],
                                [16, 26, 36, 45, 50, 50, 46, 40, 38, 42, 52, 59, 59, 56, 51, 36, 15],
                                [17, 23, 23, 17, 14, 23, 40, 50, 45, 35, 33, 42, 52, 55, 47, 33, 17, 5],
                                [12, 20, 28, 34, 37, 37, 37, 39, 47, 57, 67, 70, 62, 47, 34, 32, 26, 5],
                                [19, 25, 21, 17, 19, 26, 34, 38, 38, 40, 46, 56, 64, 64, 54, 37, 20, 6],
                                [26, 44, 42, 30, 29, 35, 42, 43, 38, 28, 17, 8]
                            ],
                            [
                                DayTimeRangeType(0, dt.time(10), dt.time(23, 30)), 
                                DayTimeRangeType(1, dt.time(6), dt.time(23, 30)),
                                DayTimeRangeType(2, dt.time(6), dt.time(23, 30)),
                                DayTimeRangeType(3, dt.time(6), dt.time(23, 30)),
                                DayTimeRangeType(4, dt.time(6), dt.time(23, 30)),
                                DayTimeRangeType(5, dt.time(6), dt.time(23, 30)),
                                DayTimeRangeType(6, dt.time(10), dt.time(22))
                            ])
}
