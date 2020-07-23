import unittest
from .test_triggers import all_triggers


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for test_class in all_triggers:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite
