# -*- coding: utf-8 -*-
import random
import unittest
from datetime import datetime, timedelta

from shapely.geometry import Point as sPoint

from paegan.cdm.dsg.member import Member
from paegan.cdm.dsg.features.base.point import Point
from paegan.cdm.dsg.features.base.profile import Profile
from paegan.cdm.dsg.collections.base.profile_collection import ProfileCollection

class ProfileCollectionTest(unittest.TestCase):
    def test_profile_collection(self):

        day = 1
        pc = ProfileCollection()
        dt = None

        # 10 profiles
        for x in range(0,10):
            lat = random.randint(40,44)
            lon = random.randint(-74,-70)
            loc = sPoint(lon,lat,0)
            hour = 0
            minute = 0
            dt = datetime(2012, 4, day, hour, minute)

            prof = Profile()
            prof.location = loc
            prof.time = dt

            # Each with 20 depths
            for y in range(0,20):
                p = Point()
                p.time = dt
                p.location = sPoint(loc.x, loc.y, y)
                m1 = Member(value=random.uniform(30,40), unit='°C', name='Water Temperature', description='water temperature', standard='sea_water_temperature')
                m2 = Member(value=random.uniform(80,100), unit='PSU', name='Salinity', description='salinity', standard='salinity')
                p.add_member(m1)
                p.add_member(m2)
                prof.add_element(p)
                # Next depth is 2 minutes from now
                dt = dt + timedelta(minutes=2)

            pc.add_element(prof)

        pc.calculate_bounds()

        assert pc.size == 10
        assert pc.point_size == 200

        assert len(pc.time_range) == 200
        assert pc.time_range[0] == datetime(2012, 4, 1, 0, 0)
        assert pc.time_range[-1] == dt - timedelta(minutes=2)

        assert len(pc.depth_range) == 200
        assert pc.depth_range[0] == 0
        assert pc.depth_range[-1] == 19

        for profile in pc:
            assert profile.type == "Profile"
            for point in profile:
                assert point.type == "Point"

        for point in pc.flatten():
            assert point.type == "Point"
