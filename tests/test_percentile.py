import unittest
from utils import percentile as my_percentile


class TestPercentile(unittest.TestCase):
    def setUp(self):
        self.sequence = [1390950160808136,
                         1390950160810164,
                         1390950160810179,
                         1390950160841530,
                         1390950160938308,
                         1390950160948308,
                         1390950161841530,
                         1390950161842604,
                         1390950161928218,
                         1390950162464394,
                         1390950162475798,
                         1390950162536865,
                         1390950162890134]

        self.work_time = [self.sequence[-1] - self.sequence[0]]

    def test_my_percentile_is_equal_to_numpy_percentile(self):
        self.assertEqual(
            my_percentile(self.work_time, .95),
            2081998
        )
