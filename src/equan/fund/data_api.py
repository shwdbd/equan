#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fund_backtesting.py
@Time    :   2020/03/07 19:23:51
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据提供API

'''
import os
import pandas as pd
import numpy as np
from equan.backtest.tl import log, tushare
from dateutil.parser import parser

DATE_FORMAT = '%Y-%M-%d'


FUND_DATA_DIR = r'data_file/equan/fund/'     # 基金数据存放目录

CAL_DATA_FILE = r'data_file/equan/cal.csv'  # 日历文件存放目录


class DataAPI:

    @staticmethod
    def get_cal(start, end, only_trade_date=True):
        """返回时间期间内的所有日期

        数据存放在 %CAL_DATA_FILE% 文件中

        Arguments:
            start {str, %Y-%M-%d} -- 符合DATE_FORMAT格式的日期文本
            end {str, %Y-%M-%d} -- 符合DATE_FORMAT格式的日期文本

        Keyword Arguments:
            only_trade_date {bool} -- 返回仅交易日 (default: {True})

        Returns:
            [list of str] -- 返回日期，按日期先后顺序排列
        """
        # TODO 单元测试

        # 注意文件是否存在
        if not os.path.exists(CAL_DATA_FILE):
            log.error('日历数据文件不存在！')
            return None

        df = pd.read_csv(filepath_or_buffer=CAL_DATA_FILE, encoding='utf-8')
        # 日期格式转换：
        df['cal_date'] = pd.to_datetime(df['cal_date'], format='%Y%M%d')
        df['cal_date'] = df['cal_date'].dt.strftime(DATE_FORMAT)
        df['pretrade_date'] = pd.to_datetime(df['pretrade_date'], format='%Y%M%d')
        df['pretrade_date'] = df['pretrade_date'].dt.strftime(DATE_FORMAT)
        # 日期过滤：
        df = df.loc[(df.cal_date >= start) & (df.cal_date <= end)]
        # 注意是否交易日
        if only_trade_date:
            df = df.loc[df.is_open == 1]
        # 注意返回的日期顺序
        df.sort_values(by='cal_date', inplace=True)

        return df['cal_date'].to_list()

    @staticmethod
    def load_fund_daily(fund_id, start_date, end_date):
        """
        读取基金日线数据

        Arguments:
            fund_id {[type]} -- [description]
            start_date {[type]} -- [description]
            end_date {[type]} -- [description]

        Returns:
            [pandas.dataframe] -- 返回的数据，如果没有数据则返回None
        """
        # TODO 待单元测试
        data_file = FUND_DATA_DIR + '{fund_symbol}.csv'.format(fund_symbol=fund_id)
        if not os.path.exists(data_file):
            print('数据不存在，无法获得数据! ' + str(data_file))
            return None
        else:
            # 读取日历
            df_cal = pd.DataFrame(DataAPI.get_cal(start_date, end_date, only_trade_date=True), columns=['date'])
            # 读取基金数据文件
            df_data = pd.read_csv(filepath_or_buffer=data_file, usecols=['FSRQ', 'DWJZ'])
            df_data.rename(columns={"FSRQ": "date", "DWJZ": "price"}, inplace=True)

            # merge:
            df = df_cal.merge(df_data, how='left', on='date')

            # 计算昨日:
            df['pretrade_date'] = df['date'].shift(1)   # FIXME 第一天的昨日是NaN
            # 排序
            df = df.sort_values(by=['date'], ascending=True)
            # 将日期设置为index
            df.set_index(['date'], drop=False, inplace=True)

            return df


if __name__ == "__main__":
    # days = DataAPI.get_cal('2020-01-01', '2020-01-05')
    # print(days)

    df = DataAPI.load_fund_daily('005918', '2020-01-01', '2020-01-31')
    print(df.head())


