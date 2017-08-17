import unittest
from utils import get_call_ids_keys_by_max_values


class TestGetMaxResponseTime(unittest.TestCase):
    def setUp(self):
        self.total = {
        0: 1000000,
        1: 2000000,
        2: 3000000,
        3: 4000000,
        4: 5000000,
        5: 6000000,
        6: 9000000,
        7: 8000000,
        8: 7000000,
        9: 6100000,
       10: 63000000,
       11: 33000000,
        }

        self.expected_result = [10, 11, 6, 7, 8, 9, 5, 4, 3, 2]

    def test_get_max_response_times_list(self):

        res = get_call_ids_keys_by_max_values(self.total)
        self.assertTrue(len(res) == 10)
        self.assertEqual(res, self.expected_result)
