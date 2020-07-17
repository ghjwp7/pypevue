#!/usr/bin/env python3
import unittest
import sys

class BaseTest(unittest.TestCase):
    runAll = True # overriden by each Test Case
    runTestCounts = list(range(99)) # overriden by each Test Case
    def skipThisTest(self, test_name):
        '''
        Each test uses introspection to find its test name, i.e. inspect.stack()[0][3].
        The test name containing the test number is passed as 'test_name'.
        Each test also can set runAll and runTestCounts to control which tests are run.

        If this test is to be skipped:
          return False
        If this test is to be run:
          print the test name
          return True
        '''
        skip = True
        if self.runAll:
            skip = False
        else:
            testNum = int(test_name.split('_')[1])
            if testNum in self.runTestCounts:
                skip = False
        if skip == False:
            print(f'\n  {test_name}' + ' ' * (77 - len(test_name)), end='')
            sys.stdout.flush()
        return skip
    
