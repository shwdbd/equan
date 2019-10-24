import unittest
import equan.demo.SMA.sma as sma


class Test_SMA(unittest.TestCase):

    def test_get_equity_pool(self):
        self.assertListEqual([], sma.get_equity_pool())


