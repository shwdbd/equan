#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_biztools_trade_cal.py
@Time    :   2019/11/25 17:12:00
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   业务工具 交易日历方面函数
'''
import unittest
import equan.backtest.biz_tools as bt


class Test_Trade_Cal(unittest.TestCase):
    """
    交易日工具测试

    """

    def test_date_range(self):
        """
        测试 取得一定范围内日期
        """
        dates = bt.Trade_Cal.date_range('20170101', '20170110')
        benchmark = ['20170103', '20170104', '20170105',
                     '20170106', '20170109', '20170110']
        self.assertListEqual(benchmark, dates)

    def test_date_range_2(self):
        """
        测试 取得一定范围内日期(start晚于end)
        """
        dates = bt.Trade_Cal.date_range('20180101', '20170110')
        self.assertListEqual([], dates)

    def test_date_range_3(self):
        """
        测试 取得一定范围内日期(日期参数异常)
        """
        dates = bt.Trade_Cal.date_range('aaa', None)
        self.assertListEqual([], dates)

    def test_date_range_4(self):
        """
        测试 取得一定范围内日期(其他格式的数据形式)
        """
        dates = bt.Trade_Cal.date_range('2017-1-1', '2017-1-10')
        self.assertListEqual([], dates)

    def test_previous_date(self):
        """
        测试取前一个交易日
        """
        dates = bt.Trade_Cal.previous_date('20170104')
        self.assertEquals('20170103', dates)

        # 跨年的情况
        dates = bt.Trade_Cal.previous_date('20170101')
        self.assertEquals('20161230', dates)

        # 未来或太早，没有的情况
        dates = bt.Trade_Cal.previous_date('99990101')
        self.assertEquals(None, bt.Trade_Cal.previous_date('99990101'))
        self.assertEquals(None, bt.Trade_Cal.previous_date('19000101'))
