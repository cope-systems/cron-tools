import unittest


class NullTestCase(unittest.TestCase):
    def test_nothing(self):
        """
        Stand in test case to do nothing before we start writing real tests.
        """
        print("null test")
