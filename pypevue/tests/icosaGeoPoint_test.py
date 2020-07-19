#!/usr/bin/env python3
'''
history
5/25/20 - created
'''
#import context
import unittest
import shutil
from pypevue.makeIcosaGeo import IcosaGeoPoint
from math import degrees, radians, cos, sin, pi
import inspect
from base_test import BaseTest

class IcosaGeoPointTest(BaseTest):
    runAll = True
    runTestCounts = list(range(15))
    runTestCounts = [1]
    def test_00_instantiate(self):
        print('\nIcosaGeoPointTest')
        if self.skipThisTest(inspect.stack()[0][3]): return
        p = IcosaGeoPoint(0,0,0,1)

    def test_01_nutation(self):
        if self.skipThisTest(inspect.stack()[0][3]): return
        show = False
        epsilon = 0.0000001
        freq = 3
        data = (
            #   p        q     angle
            ((0, 1,-1), (0, 1,0), -45),
            ((0, 1, 1), (0, 1,0), -45),
            ((0, 1, 1), (0, 2,0),   0),
            ((0, 1, 1), (0, 3,0), 18.43494882292201),
            ((0,-1, 1), (0,-1,0), -45),
            ((0,-1, 1), (0,-2,0), 0),
            ((0,-1, 1), (0,-3,0), 18.43494882292201),
            )
        for (px,py,pz), (qx,qy,qz), expAngle in data:
            p = IcosaGeoPoint(px,py,pz, freq)
            q = IcosaGeoPoint(qx,qy,qz, freq)
            actAngle = degrees(p.nutation(q))
            if show:
                print(f'  exp: {expAngle}, act: {actAngle}', end=' ')
                if expAngle - epsilon < actAngle < expAngle + epsilon:
                    print()
                else: print('**********************ERROR***********************')

            else: 
                self.assertAlmostEqual(expAngle, actAngle)
                
    def test_02_precession(self):
        if self.skipThisTest(inspect.stack()[0][3]): return
        show = False
        freq = 3
        data = (
            #   p        q     angle
            # go all the way around with the default plane, i.e. x z axis
            ((0,0,1), (1,0,0), 0.0),
            ((0,0,1), (cos(radians(30)),sin(radians(30)),0), 30),
            ((0,0,1), (1,1,0), 45),
            ((0,0,1), (0,1,0), 90),
            ((0,0,1), (-1,1,0), 135),
            ((0,0,1), (-cos(radians(30)),sin(radians(30)),0), 150),
            ((0,0,1), (-1,0,0), 180),
            ((0,0,1), (-cos(radians(30)),-sin(radians(30)),0), 210),
            ((0,0,1), (-1,-1,0), 225),
            ((0,0,1), (0,-1,0), 270),
            ((0,0,1), (1,-1,0), 315),
            ((0,0,1), (cos(radians(30)),-sin(radians(30)),0), 330),
            ((0,1,1), (0,0,1), 90),
            ((0,1,1), (0,-1,1), 90),
            ((0,1,1), (0,-1,0), 90),
            ((0,1,1), (0,1,0), 270),
            ((-523.16, 0.00, 1431.39), (0.00, 0.00, 1746.80), 90), # post 1 to 0
            ((-161.66, 497.55, 1431.39), (0.00, 0.00, 1746.80), 90), # post 2 to 0
            ((423.24, 307.50, 1431.39), (0.00, 0.00, 1746.80), 90), # post 3 to 0
            ((423.24, -307.50, 1431.39), (0.00, 0.00, 1746.80), 90), # post 4 to 0
            ((-161.66, -497.55, 1431.39), (0.00, 0.00, 1746.80), 90), # post 5 to 0
            (( 306.79,  944.20, 1299.58), (-323.33, 995.10, 1108.06), 0), # post 7 to 8

#       0H, weave: LHL, nutations:  -31.1deg -31.1deg -31.1deg -31.1deg -31.1deg, precessions:   36.0deg 252.0deg  36.0deg 324.0deg 252.0deg, (0.00, 0.00, 1746.80)
            
            ((0.00, 0.00, 1746.80), (-523.16,    0.00, 1431.39), 180), # post 0H to 1L
            ((0.00, 0.00, 1746.80), (-161.66,  497.55, 1431.39), 108), # post 0 to 2
            ((0.00, 0.00, 1746.80), ( 423.24,  307.50, 1431.39), 36), # post 0 to 3
            ((0.00, 0.00, 1746.80), ( 423.24, -307.50, 1431.39), 324), # post 0 to 4
            ((0.00, 0.00, 1746.80), (-161.66, -497.55, 1431.39), 252), # post 0 to 5
        )
        for (px,py,pz), (qx,qy,qz), expAngle in data:
            p = IcosaGeoPoint(px,py,pz, freq)
            q = IcosaGeoPoint(qx,qy,qz, freq)
            actAngle = degrees(p.precession(q))
            if show:
                print(f'  exp: {expAngle}, act: {actAngle}', end=' ')
                if expAngle == round(actAngle,2):
                    print()
                else: print('**********************ERROR***********************')

            else: 
                self.assertAlmostEqual(expAngle, actAngle, 3, ' p ' + str(p) + ', q ' + str(q))

    def test_99_run_all_on(self):
        testName = inspect.stack()[0][3]
        print(f'\n  {testName}' + ' ' * (77 - len(testName)), end='')
        self.assertTrue(self.runAll)

if __name__ == '__main__':
    unittest.main()
