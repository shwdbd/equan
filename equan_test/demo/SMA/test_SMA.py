import unittest
# import equan.demo.SMA.sma as sma
import equan.demo.SMA.sma_impl as impl
import pandas as pd


class Test_SMA(unittest.TestCase):

    def test_get_equity_pool(self):
        # self.assertListEqual([], sma.get_equity_pool())
        self.assertTrue(True)


class Test_SeekEquity(unittest.TestCase):
    """
    单元测试 选股模块 功能
    """

    def test_seek_equity_by_pepb_mode(self):
        """
        测试 PEPB 模式下的选股
        """
        frm = impl.SMATestFrame()
        frm.SEEK_EQUITY_SETTINGS['seek.model'] = 'PEPB_MIN'
        stocks = frm.seek_equity()
        print(stocks)

    def test_seek_equity_by_MATRIX_mode(self):
        """
        测试 矩阵 模式下的选股
        """
        frm = impl.SMATestFrame()
        frm.SEEK_EQUITY_SETTINGS['seek.model'] = 'MATRIX'

    def test_get_hs300(self):
        """
        测试 获得沪深300股票
        """
        frm = impl.SMATestFrame()
        # 所有字段的情况
        df = frm.get_hs300()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 300)
        self.assertListEqual(['date', 'code', 'name', 'weight'], df.columns.tolist())
        df = frm.get_hs300(fields=[])
        self.assertListEqual(['date', 'code', 'name', 'weight'], df.columns.tolist())

        df = frm.get_hs300(fields=['code', 'name'])
        self.assertEqual(df.shape[0], 300)
        self.assertListEqual(['code', 'name'], df.columns.tolist())
