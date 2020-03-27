#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_SMA.py
@Time    :   2020/03/27 11:40:45
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   双均线策略 相关单元测试

- PEPB选股 测试
- 针对服务读取服务的测试

'''
import unittest
# import equan.demo.SMA.sma as sma
import equan.demo.SMA.sma_impl as impl
import equan.demo.SMA.data_picker as dp
import pandas as pd
# from pandas.util.testing import assert_frame_equal
from pandas.api.types import is_string_dtype
import os


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
        df = dp.get_daily_basic(ts_code='600016.SH',
                                start_date='20191028', end_date='20191029')
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.shape[0] == 2)

        sample_data = {'ts_code': {0: '600016.SH', 1: '600016.SH'}, 'trade_date': {0: 20191029, 1: 20191028}, 'close': {0: 6.16, 1: 6.18}, 'turnover_rate': {0: 0.1055, 1: 0.1636}, 'turnover_rate_f': {0: 0.1094, 1: 0.1697}, 'volume_ratio': {0: 0.72, 1: 1.15}, 'pe': {0: 5.3589, 1: 5.3763}, 'pe_ttm': {0: 5.1536, 1: 5.1704}, 'pb': {
            0: 0.6541, 1: 0.6562}, 'ps': {0: 1.7204, 1: 1.7259}, 'ps_ttm': {0: 1.5901, 1: 1.5953}, 'total_share': {0: 4378241.8502, 1: 4378241.8502}, 'float_share': {0: 3546212.3213, 1: 3546212.3213}, 'free_share': {0: 3418200.6089999997, 1: 3418200.6089999997}, 'total_mv': {0: 26969969.7972, 1: 27057534.6342}, 'circ_mv': {0: 21844667.8992, 1: 21915592.1456}}
        self.assertDictEqual(
            sample_data, df[df['ts_code'] == '600016.SH'].to_dict())

        # 检查缓存文件是否生成
        self.assertTrue(os.path.exists(dp.DATA_FILE_DIR +
                                       r'daily_basic_600016.SH_20191028_20191029.csv'))
