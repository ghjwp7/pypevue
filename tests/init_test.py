#!/usr/bin/env python3
'''Tests for __init__.py and some of its classes'''
# jiw 28 Aug 2020

import unittest
#import shutil
from pypevue import ssq, sssq, rotate2, isTrue, Point, IcosaGeoPoint
from math import sqrt, degrees, radians, cos, sin, pi
import os, sys, random
from base_test import BaseTest

class Init_Test(BaseTest):
    '''to run:
      - cd pypeVue   (The project dir, not pypeVue/src/pypeVue)
      - to run just this test:
           python3 -m unittest discover tests -p init_test.py
      - to run all tests:
           python3 setup.py test
    '''
    testPath = os.path.dirname(__file__)
    pypePath = os.path.normpath(f'{testPath}/../src/pypevue')
    
    def test_00_instantiate(self):
        print('\nPoint and IcosaGeoPoint instantiation test')
        p = Point(1,2,3)
        q = IcosaGeoPoint(1,2,3,4)

    def test_01_isTrue(self):
        print('\nTests for false result from isTrue()')
        self.assertFalse(isTrue(None))
        self.assertFalse(isTrue(False))
        self.assertFalse(isTrue(''))
        self.assertFalse(isTrue('fa so la'))
        self.assertFalse(isTrue('Faro'))
        self.assertFalse(isTrue('N'))
        self.assertFalse(isTrue('Nu'))
        self.assertFalse(isTrue('non'))        
        print('Tests for true result from isTrue()')
        self.assertTrue(isTrue(True))
        self.assertTrue(isTrue(' '))
        self.assertTrue(isTrue('hey'))
        self.assertTrue(isTrue('Yep'))
        self.assertTrue(isTrue(0))
        self.assertTrue(isTrue(17))

    def test_02_ssq(self):
        print('\nssq, sssq, mag, mag2, p*p Tests')
        points = ((0,0,0, 0),   (1,1,1, 3), (2,2,2, 12),  (3,4,5, 50))
        for x,y,z, css in points:
            p = Point(x,y,z)
            self.assertEqual(ssq(x,y,z),        css)
            self.assertAlmostEqual(sssq(x,y,z), sqrt(css))            
            self.assertEqual(p.mag2(),      css)
            self.assertAlmostEqual(p.mag(), sqrt(css))
            self.assertEqual(p*p, css)        # inner product
            self.assertEqual(p.inner(p), css) # inner product
        
    def checkAE(self, p, q):  # Test if point p almost equals q.
        # Require 14 decimals to match instead of the default 7.
        self.assertAlmostEqual(p.x, q.x, places=14)
        self.assertAlmostEqual(p.y, q.y, places=14)
        self.assertAlmostEqual(p.z, q.z, places=14)

    def test_03_add_sub(self):
        print('\n +, -, add, diff Tests')
        random.seed(4253)
        for i in range(99):
            ax, ay, az, bx, by, bz = (random.random() for i in range(6))
            a = Point(ax, ay, az)
            b = Point(bx, by, bz)
            c = Point(ax+bx, ay+by, az+bz)
            self.checkAE(a+b, c)
            self.checkAE(b+a, c)
            self.checkAE(a.add(b), c)
            self.checkAE(b.add(a), c)
            self.checkAE(c-a, b)
            self.checkAE(c-b, a)
            self.checkAE(c.diff(a), b)
            self.checkAE(c.diff(b), a)
            
        
    '''
    def test_04_(self): pass        
    
    def test_05_(self): pass
        
    def test_06_(self): pass        
    
    def test_07_(self): pass        
    
    def test_08_(self): pass        
    
    def test_09_(self): pass        
    
    def test_10_(self): pass        
    
    def test_11_(self): pass
    '''
    
if __name__ == '__main__':
    unittest.main()
