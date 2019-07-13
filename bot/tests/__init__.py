import unittest
from .test_triggers import all_triggers
from .test_exceptions import TestExceptions


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for test_class in all_triggers:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    tests = loader.loadTestsFromTestCase(TestExceptions)
    suite.addTests(tests)
    return suite
