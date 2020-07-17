#!/usr/bin/env python3
'''Adapted for pypevue 16 July 2020 by jiw from sn's version for
pypevue.'''

import unittest
import shutil
from pypevue.makeIcosaGeo import IcosaGeoPoint
from math import degrees, radians, cos, sin, pi
import os
import sys
import xml.etree.ElementTree as ET
import time
import inspect
from base_test import BaseTest
from re import search

class SystemTest(BaseTest):
    '''to run:
      - cd  pypeVue   (The project dir, not pypeVue/src/pypeVue)
      - to run just this test:
           python3 -m unittest discover tests -p system_test.py
      - to run all tests:
           python3 setup.py test

    Each test should generate a scad file or files in
    tmp_output_files/, then continue to the next test

    '''
    runAll = True
    runTestCounts = [2]
    testPath = os.path.dirname(__file__)
    pypePath = os.path.normpath(f'{testPath}/../src/pypevue')
    scadPath = os.path.normpath(f'{testPath}/tmp_output_files')
    examplesPath = os.path.normpath(f'{testPath}/../src/pypevue/examples')

    def test_00_instantiate(self):
        print(f'\nSystemTest:   To view 3D results, in  tmp_output_files/  say "openscad fn&"\nwhere fn is a file in that directory.\n') 
        if self.skipThisTest(inspect.stack()[0][3]): return
        print ()
        scadf = os.path.normpath(f'{self.scadPath}/to-instance')
        err = os.system(f'{self.pypePath}/pypevu.py; mv pypevu.scad {scadf}')
        self.assertEqual(0, err)

    def doRegexGroup(self, rex):        
        if self.skipThisTest(inspect.stack()[0][3]): return
        print ()
        # Get list of eg-* files in  ../src/pypevue/examples/
        egls =  os.listdir(self.examplesPath)
        egeg = [f for f in egls if f.startswith('eg-')]
        gmls = os.listdir(self.testPath)
        gmgm = [f for f in gmls if f.startswith('gm-eg-')]
        for fname in egeg:
            if not search(rex, fname):
                continue        # Skip if name doesn't match regex
            # If we have a golden master for the example, then test it,
            # else say that example doesn't have a golden master
            if f'gm-{fname}' not in gmgm:
                print (f"\nNot running {fname} due to non-golden.")
            else:
                print (f'\nTest example {fname}')
                # We have a golden master so run a test
                scriptPath = os.path.normpath(f'{self.examplesPath}/{fname}')
                scadf = os.path.normpath(f'{self.scadPath}/to-{fname}')
                # Run the example and see if pypevue exits ok
                err = os.system(f'{self.pypePath}/pypevu.py f={scriptPath}; mv pypevu.scad {scadf}')
                self.assertEqual(0, err)
                # Compare output file to golden file
                with open(f'{self.testPath}/gm-{fname}') as fg:
                    with open(scadf) as ft:
                        # Read and discard first two lines of each file
                        for ff in (fg, fg, ft, ft):  dc = ff.readline()
                        # Compare rest of files line-by-line
                        for gline in fg:                            
                            tline = ft.readline()
                            self.assertEqual(tline, gline)


    def test_aap(self):     self.doRegexGroup('arith|auto|pentagon')
    def test_fts(self):     self.doRegexGroup('fat|two|several')
    def test_cap(self):     self.doRegexGroup('cap')
    def test_freq(self):    self.doRegexGroup('freq')
    def test_geo(self):     self.doRegexGroup('geo')
         
if __name__ == '__main__':
    unittest.main()
