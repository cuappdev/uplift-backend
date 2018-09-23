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
                            ]),
    'Appel': GymType('Appel',
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
                                DayTimeRangeType(0, dt.time(9), dt.time(13)),
                                DayTimeRangeType(1, dt.time(15), dt.time(23, 30)),
                                DayTimeRangeType(2, dt.time(15), dt.time(23, 30)),
                                DayTimeRangeType(3, dt.time(15), dt.time(23, 30)),
                                DayTimeRangeType(4, dt.time(15), dt.time(23, 30)),
                                DayTimeRangeType(5, dt.time(15), dt.time(23, 30)),
                                DayTimeRangeType(6, dt.time(9), dt.time(13))
                            ]),
    'Noyes': GymType('Noyes',
                     'description',
                     [
                         [18, 36, 44, 39, 33, 38, 45, 52, 63, 75, 70, 45, 18],
                         [4, 11, 20, 26, 26, 24, 24, 29, 39, 48, 51, 48, 47, 52, 52, 38, 17],
                         [8, 13, 17, 17, 17, 20, 27, 36, 45, 50, 51, 51, 56, 64, 67, 55, 33],
                         [5, 11, 18, 23, 23, 20, 20, 26, 38, 48, 56, 63, 71, 70, 56, 34, 14],
                         [9, 16, 21, 21, 17, 13, 16, 26, 41, 53, 54, 51, 55, 67, 69, 51, 24],
                         [2, 7, 14, 17, 17, 15, 19, 32, 50, 58, 56, 51, 52, 52, 45, 30, 15],
                         [25, 36, 46, 56, 58, 50, 47, 53, 58, 50, 35]
                     ],
                     [
                         DayTimeRangeType(0, dt.time(11, 30), dt.time(23, 30)),
                         DayTimeRangeType(1, dt.time(7), dt.time(23, 30)),
                         DayTimeRangeType(2, dt.time(7), dt.time(23, 30)),
                         DayTimeRangeType(3, dt.time(7), dt.time(23, 30)),
                         DayTimeRangeType(4, dt.time(7), dt.time(23, 30)),
                         DayTimeRangeType(5, dt.time(7), dt.time(23, 30)),
                         DayTimeRangeType(6, dt.time(11, 30), dt.time(22))
                     ]),
    'Teagle Up': GymType('Noyes',
                         'description',
                         [
                             [3, 13, 21, 24, 34, 36, 14],
                             [14, 27, 41, 53, 60, 58, 50, 44, 45, 56, 69, 74, 64, 43, 22, 8],
                             [16, 26, 35, 43, 53, 63, 67, 61, 53, 50, 52, 51, 44, 30, 16, 6],
                             [21, 46, 38, 40, 58, 62, 48, 34, 35, 51, 68, 75, 65, 47, 26, 11],
                             [16, 26, 37, 46, 52, 53, 52, 51, 53, 53, 47, 45, 58, 59, 32, 7],
                             [12, 26, 32, 38, 48, 56, 54, 50, 52, 53, 44, 26, 11],
                             [9, 17, 27, 36, 41, 36, 24]
                         ],
                         [
                             DayTimeRangeType(0, dt.time(12), dt.time(17, 45)),
                             DayTimeRangeType(1, dt.time(7), dt.time(22, 45)),
                             DayTimeRangeType(2, dt.time(7), dt.time(22, 45)),
                             DayTimeRangeType(3, dt.time(7), dt.time(22, 45)),
                             DayTimeRangeType(4, dt.time(7), dt.time(22, 45)),
                             DayTimeRangeType(5, dt.time(7), dt.time(20)),
                             DayTimeRangeType(6, dt.time(12), dt.time(17, 45))
                         ]),
    'Teagle Down': GymType('Noyes',
                           'description',
                           [
                               [3, 13, 21, 24, 34, 36, 14],
                               [14, 27, 41, 53, 60, 58, 50, 44, 45, 56, 69, 74, 64, 43, 22, 8],
                               [16, 26, 35, 43, 53, 63, 67, 61, 53, 50, 52, 51, 44, 30, 16, 6],
                               [21, 46, 38, 40, 58, 62, 48, 34, 35, 51, 68, 75, 65, 47, 26, 11],
                               [16, 26, 37, 46, 52, 53, 52, 51, 53, 53, 47, 45, 58, 59, 32, 7],
                               [12, 26, 32, 38, 48, 56, 54, 50, 52, 53, 44, 26, 11],
                               [9, 17, 27, 36, 41, 36, 24]
                           ],
                           [
                               DayTimeRangeType(0, dt.time(12), dt.time(17, 45)),
                               DayTimeRangeType(1, dt.time(7), dt.time(22, 45)),
                               DayTimeRangeType(2, dt.time(7), dt.time(22, 45)),
                               DayTimeRangeType(3, dt.time(7), dt.time(22, 45)),
                               DayTimeRangeType(4, dt.time(7), dt.time(22, 45)),
                               DayTimeRangeType(5, dt.time(7), dt.time(20)),
                               DayTimeRangeType(6, dt.time(12), dt.time(17, 45))
                           ])
}
