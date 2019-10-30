import unittest
# import equan.demo.SMA.sma as sma
import equan.demo.SMA.sma_impl as impl
import equan.demo.SMA.data_picker as dp
import pandas as pd
from pandas.util.testing import assert_frame_equal
from pandas.api.types import is_string_dtype
import os


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


class Test_data_picker(unittest.TestCase):
    """
    针对服务读取服务的测试
    """

    def test_get_hs300s(self):
        """
        测试 获得沪深300股票
        """
        # 所有字段的情况
        df = dp.get_hs300s()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 300)  # 300条记录
        self.assertListEqual(
            ['date', 'code', 'name', 'weight'], df.columns.tolist())
        is_string_dtype(df['code'])     # 判断该列是否string
        df = dp.get_hs300s(fields=[])
        self.assertListEqual(
            ['date', 'code', 'name', 'weight'], df.columns.tolist())

        # 检查缓存文件是否生成
        self.assertTrue(os.path.exists(dp.DATA_FILE_DIR+r'hs300.csv'))

        # 测试带字段参数的情况
        df = dp.get_hs300s(fields=['code', 'name'])
        self.assertEqual(df.shape[0], 300)
        self.assertListEqual(['code', 'name'], df.columns.tolist())

    def test_get_stock_basic(self):
        """
        测试 取股票信息
        """
        df = dp.get_stock_basic()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.shape[0] > 2000)

        cmbc_record = {'ts_code': {2180: '600016.SH'}, 'symbol': {2180: '600016'}, 'name': {2180: '民生银行'}, 'area': {
            2180: '北京'}, 'industry': {2180: '银行'}, 'market': {2180: '主板'}, 'list_date': {2180: 20001219}}
        self.assertDictEqual(
            cmbc_record, df[df['symbol'] == '600016'].to_dict())

        # 检查缓存文件是否生成
        self.assertTrue(os.path.exists(dp.DATA_FILE_DIR+r'stock_basic.csv'))

    def test_get_daily_basic(self):
        """
        测试 取股票每日指标
        """
        # stock_codes=None, trade_date=None, start_date=None, end_date=None, fields=None
        # TODO 测试单一股票，日期范围
        # TODO 测试多个股票，单一日期
        # TODO 测试取部分字段的情况

        # 参数缺失的情况  TODO 不太懂异常测试，先搁置
        # self.assertRaises(Exception, dp.get_daily_basic, {'trade_date': '12345'})

        # 测试单一股票，日期范围, 600016
