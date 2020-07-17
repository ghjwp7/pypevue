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
    scadPath = os.path.normpath(f'./tmp_output_files')
    examplesPath = os.path.normpath(f'{testPath}/../src/pypevue/examples')

    def test_00_instantiate(self):
        print(f'\nSystemTest:   To view 3D results say "openscad pypeVue.scad&"\nin pypevue project directory\n') 
        if self.skipThisTest(inspect.stack()[0][3]): return
        print ()
        scadf = os.path.normpath(f'{scadPath}/to-instance')
        err = os.system(f'{pypePath}/pypevu.py scadFile={scadf}')
        self.assertEqual(0, err)

    def test_01_freq_1(self):
        if self.skipThisTest(inspect.stack()[0][3]): return
        print ()
        # Get list of eg-* files in  ../src/pypevue/examples/
        egls =  os.listdir(self.examplesPath)
        egeg = [f for f in egls if f.startswith('eg-')]
        gmls = os.listdir(self.testPath)
        gmgm = [f for f in gmls if f.startswith('gm-eg-')]
        for fname in egeg:
            # If we have a golden master for the example, then test it,
            # else say that example doesn't have a golden master
            if f'gm-{fname}' not in gmgm:
                print (f"sad, can't test {fname} due to non-golden")
            else:
                print (f'A++, would test {fname}')
                # We have a golden master so run a test
                scriptPath = os.path.normpath(f'{self.examplesPath}/{fname}')
                scadf = os.path.normpath(f'{scadPath}/to-{fname}')
                # Run the example and see if pypevue exits ok
                err = os.system(f'{pypePath}/pypevu.py f={scriptPath} scadFile={scadPath}')
                self.assertEqual(0, err)
                # Compare 

    def test_99_run_all_on(self):
        testName = inspect.stack()[0][3]
        print(f'\n  {testName}' + ' ' * (77 - len(testName)), end='')
        self.assertTrue(self.runAll)

if __name__ == '__main__':
    unittest.main()
