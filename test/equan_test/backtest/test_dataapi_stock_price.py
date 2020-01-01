#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_dataapi_stock_price.py
@Time    :   2020/01/01 16:19:31
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   单元测试 数据API 取股票价格
'''
import unittest
import equan.backtest.data_api as dapi


class Test_Get_Stock_Price(unittest.TestCase):

    def test_get_price(self):
        """
        测试 取的单个股票价格
        """
        # 600016, 2019-1-3, 5.63(open), 5.67(close)
        self.assertEqual(5.63, dapi.stock_price('600016.SH', '20190103'))
        self.assertEqual(5.67, dapi.stock_price(
            '600016.SH', '20190103', 'close'))

    def test_unkown_stockid(self):
        """
        取股票价格 股票代码不存在的情况 [反例]
        """
        self.assertIsNone(dapi.stock_price('xxxxx.SH', '20190103'))

    def test_unkown_tradedate(self):
        """
        取股票价格 日期取不到的情况 [反例]
        """
        self.assertIsNone(dapi.stock_price('600016.SH', '99990101'))

    def test_multi_stockid(self):
        """
        取股票价格 取得多个股票的情况
        """
        stock_list = ['600016.SH', '600036.SH']
        price = dapi.stock_price(stock_list, '20190103', 'close')
        self.assertDictEqual({'600016.SH': 5.67, '600036.SH': 24.88}, price)

    def test_error_price_type(self):
        """
        取股票价格 价格类型不合法的情况 [反例]
        """
        self.assertIsNone(dapi.stock_price('600016.SH', '20190103', 'xxxxx'))
