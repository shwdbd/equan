#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_dataapi.py
@Time    :   2020/03/10 16:19:56
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据接口的单元测试
测试，从天天基金网上下载数据的功能
'''
import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal
from equan.fund.data_api import DataAPI
import equan.fund.data_api as data_api
import shutil
import os


class TestDataAPI_get_cal(unittest.TestCase):
    """测试，取日历清单
    """

    def setUp(self):
        self.test_path = r'test/equan_test/fund/'   # 当前用例的路径
        self.data_path = r'test/equan_test/fund/fund_data'  # 测试文件存放路径

        shutil.copy2(self.test_path + r'cal_test_dataapi.csv', self.data_path + r'cal.csv')
        self.bak_of_filepath = data_api.CAL_DATA_FILE
        data_api.CAL_DATA_FILE = self.data_path + r'cal.csv'
        return super().setUp()

    def tearDown(self):
        data_api.CAL_DATA_FILE = self.bak_of_filepath
        os.remove(self.data_path + r'cal.csv')
        return super().tearDown()

    def test_get_cal_bylist(self):
        """测试按list格式取日历
        """
        # 测试正常取出
        dates = DataAPI.get_cal(start='2020-01-01', end='2020-01-05')
        self.assertListEqual(['2020-01-02', '2020-01-03'], dates)

        # 测试，参数日期格式错误的情况
        dates = DataAPI.get_cal(start='20200101', end='20200105')
        self.assertListEqual([], dates)

        # 测试，取自然日
        dates = DataAPI.get_cal(
            start='2020-01-01', end='2020-01-05', only_trade_date=False)
        self.assertListEqual(
            ['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-04', '2020-01-05'], dates)

        # 测试，文件数据缺失的情况
        dates = DataAPI.get_cal(
            start='1900-01-01', end='1901-01-05', only_trade_date=False)
        self.assertListEqual([], dates)

        # 测试，文件不存在的情况
        data_api.CAL_DATA_FILE = 'xxxx.xxx'
        dates = DataAPI.get_cal(start='2020-01-01', end='2020-01-05')
        self.assertIsNone(dates)

    def test_get_cal_bydf(self):
        """测试按dataframe格式取日历
        """
        df_sample = pd.DataFrame({'cal_date': ['2020-01-01', '2020-01-02'],
                                  'is_open': [0, 1],
                                  'pretrade_date': ['2019-12-31', '2019-12-31']})
        df = DataAPI.get_cal(start='2020-01-01', end='2020-01-02',
                             return_type='df', only_trade_date=False)
        assert_frame_equal(df_sample, df)


class TestDataAPI_load_fund_daily(unittest.TestCase):
    """测试，取基金日线数据
    """

    def setUp(self):
        self.test_path = r'test/equan_test/fund/'   # 当前用例的路径
        self.data_path = r'test/equan_test/fund/fund_data'  # 测试文件存放路径

        # 准备测试数据
        shutil.copy2(self.test_path + r'005918_test_dataapi.csv', self.data_path + r'005918.csv')
        shutil.copy2(self.test_path + r'cal_test_dataapi.csv', self.data_path + r'cal.csv')
        self.bak_of_filepath = data_api.CAL_DATA_FILE
        data_api.CAL_DATA_FILE = self.data_path + r'cal.csv'
        self.bak_of_dirpath = data_api.FUND_DATA_DIR
        data_api.FUND_DATA_DIR = self.data_path
        return super().setUp()

    def tearDown(self):
        data_api.CAL_DATA_FILE = self.bak_of_filepath
        data_api.FUND_DATA_DIR = self.bak_of_dirpath
        # 删除测试用文件
        os.remove(self.data_path + r'005918.csv')
        os.remove(self.data_path + r'cal.csv')
        return super().tearDown()

    def test_normal(self):
        """测试基金文件存在的情况
        """
        # 测试正常取出
        df = DataAPI.load_fund_daily(
            fund_id='005918', start_date='2020-01-01', end_date='2020-01-03')
        df_sample = pd.DataFrame({'date': ['2020-01-02', '2020-01-03'],
                                  'pretrade_date': ['2019-12-31', '2020-01-02'],
                                  'price': [1.1213, 1.1194]},
                                 index=pd.Series(['2020-01-02', '2020-01-03'], name='date'))
        assert_frame_equal(df_sample, df)

    def test_fundfile_not_exsit(self):
        """测试基金文件不存在的情况
        """
        df = DataAPI.load_fund_daily(
            fund_id='000000', start_date='2020-01-01', end_date='2020-01-03')
        self.assertIsNone(df)
