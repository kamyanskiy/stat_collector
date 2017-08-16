import unittest
from utils import get_max_response_time_to_client


class TestGetMaxResponseTime(unittest.TestCase):
    def setUp(self):
        self.total = {
        0: {'percentile': 1390137367559278, 'response_time_to_client': 1000000.0},
        1: {'percentile': 1390137367559278, 'response_time_to_client': 100000.0},
        2: {'percentile': 1390137367532459, 'response_time_to_client': 100000.0},
        3: {'percentile': 1390137367504154, 'response_time_to_client': 400000.0},
        4: {'percentile': 1390137367552055, 'response_time_to_client': 350000.0},
        5: {'percentile': 1390137367550368, 'response_time_to_client': 650000.0},
        6: {'percentile': 1390137367461632, 'response_time_to_client': 1250000.0},
        7: {'percentile': 1390137367462195, 'response_time_to_client': 450000.0},
        8: {'percentile': 1390137367540721, 'response_time_to_client': 800000.0},
        9: {'percentile': 1390137367462693, 'response_time_to_client': 500000.0},
       10: {'percentile': 1390137367601356, 'response_time_to_client': 860000.0},
       11: {'percentile': 1390137367601356, 'response_time_to_client': 890000.0},

        }

        self.expected_result = [6, 0, 11, 10, 8, 5, 9, 7, 3, 4]

    def test_get_max_response_times_list(self):
        res = get_max_response_time_to_client(self.total)
        self.assertTrue(len(res) == 10)
        self.assertEqual(res, self.expected_result)
