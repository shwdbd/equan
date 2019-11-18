#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_hammer.py
@Time    :   2019/11/18 17:34:35
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   锤子线策略 单元测试
'''
import unittest
import equan.demo.hammer.hammer as hammer
import pandas as pd


class Test_SetHammerFlag(unittest.TestCase):
    """
    单元测试：找到锤子线日期
    """

    def test_find_hammer(self):
        """
        情况1: YES, 锤子形
        情况2: NO, 上影线=Bar=下影线
        情况3: NO, Bar过长
        情况4：NO, 上影线过长
        情况5: YES，十字星
        """
        data_dict = {
            "date": pd.date_range('20190101', periods=5),
            "high": [11, 11, 10.1, 20, 11],
            "open": [10.01, 10, 10, 10.01, 10],
            "close": [10, 9, 8, 10, 10],
            "low": [1, 8, 0.1, 1, 2],
        }
        data = pd.DataFrame(data_dict)

        sty = hammer.HammerStrategy()
        data = sty.find_hammer(data)
        self.assertListEqual(data['hammer'].to_list(), [True, False, False, False, True])
