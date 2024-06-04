import unittest

class BasicTests(unittest.TestCase):

    def test_basic_assert(self):
        self.assertEqual(1, 1)

    def test_basic_true(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
