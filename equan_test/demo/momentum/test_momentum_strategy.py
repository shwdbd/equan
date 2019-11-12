#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_momentum_strategy.py
@Time    :   2019/11/12 09:56:07
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   单元测试 动量策略 临摹程序
'''
import unittest
import equan.demo.momentum.momentum_strategy as sgy
import os
import pandas as pd
from pandas.util.testing import assert_frame_equal


class TestGetData(unittest.TestCase):

    def get_sample_data(self):
        data_file = os.getcwd() + r'/equan_test/demo/momentum/hs300_daily.cvs'
        df = pd.read_csv(data_file, index_col='date', parse_dates=['date'])
        return df

    def test_get_data(self):
        """
        测试数据源获取
        """
        df_sample = self.get_sample_data()

        sgy.INDEX_CODE = '000300.SH'    # 沪深300
        sgy.START_DATE = '20190101'
        sgy.END_DATE = '20190110'
        df = sgy.get_data()

        assert_frame_equal(df_sample, df)


# if __name__ == "__main__":
#     tc = TestGetData()
#     tc.test_get_data()
