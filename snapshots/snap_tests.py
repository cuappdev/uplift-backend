# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestQuery::test_gyms 1"] = {
    "data": {
        "gyms": [
            {
                "name": "Appel",
                "facilities": [
                    {
                        "name": "Fitness Center",
                        "details": [
                            {
                                "detailsType": "Equipment",
                                "subFacilityNames": [],
                                "equipment": [
                                    {"name": "Precor treadmills"},
                                    {"name": "Elliptical trainers"},
                                    {"name": "AMTs"},
                                    {"name": "Recumbent and upright bikes"},
                                    {"name": "C2 rowing machines"},
                                    {"name": "Dumbbells"},
                                    {"name": "Kettleweights"},
                                    {"name": "Flat benches"},
                                    {"name": "Bench Press"},
                                    {"name": "Squat Rack"},
                                    {"name": "VMX Rope Trainer"},
                                    {"name": "Paramount Cable Machine"},
                                    {"name": "Octogon Functional Trainer"},
                                    {"name": "Turf with Sled Push"},
                                    {"name": "Jump ropes"},
                                    {"name": "Jungle Gym Bars"},
                                    {"name": "TRX Strap"},
                                    {"name": "Pylo Boxes"},
                                    {"name": "Core Bags"},
                                    {"name": "Griprs"},
                                    {"name": "Medicine Ball"},
                                    {"name": "Exercise Ball"},
                                    {"name": "Elastic Bands"},
                                    {"name": "Sand Bags"},
                                    {"name": "Bulgarian Bags"},
                                    {"name": "Mat"},
                                    {"name": "Exercise Ball Platform"},
                                    {"name": "Tire"},
                                    {"name": "Powerlift Boxes"},
                                ],
                                "times": [],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                    {"name": "Miscellaneous", "details": []},
                ],
            },
            {
                "name": "Helen Newman",
                "facilities": [
                    {
                        "name": "Bowling Alley",
                        "details": [
                            {
                                "detailsType": "Hours",
                                "subFacilityNames": [],
                                "equipment": [],
                                "times": [
                                    {"day": 1},
                                    {"day": 2},
                                    {"day": 3},
                                    {"day": 4},
                                    {"day": 5},
                                    {"day": 6},
                                    {"day": 0},
                                ],
                                "items": [],
                                "prices": [],
                            },
                            {
                                "detailsType": "Prices",
                                "subFacilityNames": [],
                                "equipment": [],
                                "times": [],
                                "items": ["Price per game", "Shoe rental"],
                                "prices": ["$3.50 ", "$2.50 "],
                            },
                        ],
                    },
                    {
                        "name": "Fitness Center",
                        "details": [
                            {
                                "detailsType": "Equipment",
                                "subFacilityNames": [],
                                "equipment": [
                                    {"name": "Precor treadmills"},
                                    {"name": "Elliptical trainers"},
                                    {"name": "AMTs"},
                                    {"name": "Expresso bikes"},
                                    {"name": "Recumbent and upright bikes"},
                                    {"name": "C2 rowing machines"},
                                    {"name": "Upper Body Ergometer"},
                                    {"name": "Leg Press"},
                                    {"name": "Seated Calf Raise"},
                                    {"name": "Seated Leg Curl"},
                                    {"name": "Leg Extension"},
                                    {"name": "Inner/Outer Thigh"},
                                    {"name": "Glute Extension"},
                                    {"name": "Rotary Torso"},
                                    {"name": "Back Extension"},
                                    {"name": "Converging Shoulder Press"},
                                    {"name": "Converging Chest Press"},
                                    {"name": "Dip/Chin Assist"},
                                    {"name": "Rear Deltoid/Pectoral Fly"},
                                    {"name": "Flat benches"},
                                    {"name": "Dumbbells"},
                                    {"name": "Bench Press"},
                                    {"name": "Squat Rack"},
                                    {"name": "Jungle Gym Bars"},
                                    {"name": "Lat Pull"},
                                    {"name": "Seated Cable Row"},
                                    {"name": "Cable Pull"},
                                    {"name": "Core Bags"},
                                    {"name": "Griprs"},
                                    {"name": "TRX Strap"},
                                    {"name": "Ab Roller"},
                                    {"name": "Exercise Ball"},
                                    {"name": "Mat"},
                                ],
                                "times": [],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                    {
                        "name": "Gymnasium",
                        "details": [
                            {
                                "detailsType": "Hours",
                                "subFacilityNames": [],
                                "equipment": [],
                                "times": [
                                    {"day": 1},
                                    {"day": 2},
                                    {"day": 3},
                                    {"day": 4},
                                    {"day": 5},
                                    {"day": 6},
                                    {"day": 0},
                                ],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                    {
                        "name": "Miscellaneous",
                        "details": [
                            {
                                "detailsType": "Sub-Facilities",
                                "subFacilityNames": ["Classroom/Dance Studio"],
                                "equipment": [],
                                "times": [],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                    {
                        "name": "Pool",
                        "details": [
                            {
                                "detailsType": "Hours",
                                "subFacilityNames": [],
                                "equipment": [],
                                "times": [
                                    {"day": 1},
                                    {"day": 2},
                                    {"day": 3},
                                    {"day": 4},
                                    {"day": 5},
                                    {"day": 6},
                                    {"day": 0},
                                ],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                ],
            },
            {
                "name": "Noyes",
                "facilities": [
                    {
                        "name": "Fitness Center",
                        "details": [
                            {
                                "detailsType": "Equipment",
                                "subFacilityNames": [],
                                "equipment": [
                                    {"name": "Ab Powerlift"},
                                    {"name": "Ab Rollers"},
                                    {"name": "AMTs"},
                                    {"name": "Bench Press"},
                                    {"name": "Bosu Ball"},
                                    {"name": "C2 rowing machines"},
                                    {"name": "Cable Pulls"},
                                    {"name": "Core Bags"},
                                    {"name": "Dip/Chin Assist"},
                                    {"name": "Dumbbells"},
                                    {"name": "Elliptical trainers"},
                                    {"name": "Exercise Ball"},
                                    {"name": "Expresso bikes"},
                                    {"name": "Flat benches"},
                                    {"name": "Griprs"},
                                    {"name": "Jungle Gym Bars"},
                                    {"name": "Lat Pull"},
                                    {"name": "Leg Extension"},
                                    {"name": "Leg Press"},
                                    {"name": "Mat"},
                                    {"name": "Medicine Ball"},
                                    {"name": "Powerlift Boxes"},
                                    {"name": "Precor treadmills"},
                                    {"name": "Recumbent and upright bikes"},
                                    {"name": "Seated Cable Row"},
                                    {"name": "Seated Leg Curl"},
                                    {"name": "Squat Racks"},
                                    {"name": "TRX Strap"},
                                    {"name": "Upper Body Ergometer"},
                                ],
                                "times": [],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                    {
                        "name": "Gymnasium",
                        "details": [
                            {
                                "detailsType": "Hours",
                                "subFacilityNames": [],
                                "equipment": [],
                                "times": [
                                    {"day": 6},
                                    {"day": 0},
                                    {"day": 1},
                                    {"day": 2},
                                    {"day": 3},
                                    {"day": 4},
                                    {"day": 5},
                                ],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                    {
                        "name": "Miscellaneous",
                        "details": [
                            {
                                "detailsType": "Sub-Facilities",
                                "subFacilityNames": [
                                    "Bouldering Wall",
                                    "Convenience Store",
                                    "Game Area",
                                    "Multi-Purpose Room",
                                    "Outdoor Basketball Court",
                                ],
                                "equipment": [],
                                "times": [],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                ],
            },
            {
                "name": "Teagle Up",
                "facilities": [
                    {
                        "name": "Fitness Center",
                        "details": [
                            {
                                "detailsType": "Equipment",
                                "subFacilityNames": [],
                                "equipment": [
                                    {"name": "Precor Treadmills"},
                                    {"name": "Elliptical Trainers"},
                                    {"name": "AMTs"},
                                    {"name": "Recumbent Bikes"},
                                    {"name": "Upright Bikes"},
                                    {"name": "C2 Rowing Machines"},
                                    {"name": "VMX Rope Trainer"},
                                    {"name": "Dumbbells"},
                                    {"name": "Flat Benches"},
                                    {"name": "Leg Extension"},
                                    {"name": "Seated Leg Curl"},
                                    {"name": "Leg Press"},
                                    {"name": "Inner / Outer Thigh"},
                                    {"name": "Converging Chest Press"},
                                    {"name": "Rear Deltoid/Pectoral Fly"},
                                    {"name": "Lat Pull"},
                                    {"name": "Tricep Dip"},
                                    {"name": "Seated Cable Row"},
                                    {"name": "Cable Pull"},
                                    {"name": "Paramount Functional Trainer"},
                                    {"name": "Core Bags"},
                                    {"name": "Griprs"},
                                    {"name": "Bulgarian Bags"},
                                    {"name": "Medicine Balls"},
                                    {"name": "Balance Discs"},
                                    {"name": "Bosu Ball"},
                                    {"name": "Mat"},
                                    {"name": "Exercise Balls"},
                                    {"name": "Ab Rollers"},
                                ],
                                "times": [],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                    {"name": "Miscellaneous", "details": []},
                ],
            },
            {
                "name": "Teagle Down",
                "facilities": [
                    {
                        "name": "Fitness Center",
                        "details": [
                            {
                                "detailsType": "Equipment",
                                "subFacilityNames": [],
                                "equipment": [
                                    {"name": "Powerlift Boxes"},
                                    {"name": "Flat Benches"},
                                    {"name": "Bench Press"},
                                    {"name": "Dumbbells"},
                                    {"name": "Bicep Curl"},
                                    {"name": "Squat Rack"},
                                    {"name": "Powerlift Boxes"},
                                    {"name": "Medicine Balls"},
                                    {"name": "Triceps Dip"},
                                    {"name": "Seated Cable Row"},
                                    {"name": "Cable Pull"},
                                    {"name": "Lat Pull"},
                                    {"name": "Prone Leg Curl"},
                                    {"name": "Leg Extension"},
                                    {"name": "Donkey Calf Station"},
                                    {"name": "Leg Press"},
                                    {"name": "Rear Deltoid / Pectoral Fly"},
                                    {"name": "Ab Extension"},
                                ],
                                "times": [],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                    {
                        "name": "Pool",
                        "details": [
                            {
                                "detailsType": "Hours",
                                "subFacilityNames": [],
                                "equipment": [],
                                "times": [
                                    {"day": 1},
                                    {"day": 2},
                                    {"day": 3},
                                    {"day": 4},
                                    {"day": 5},
                                    {"day": 6},
                                    {"day": 0},
                                ],
                                "items": [],
                                "prices": [],
                            }
                        ],
                    },
                ],
            },
        ]
    }
}
