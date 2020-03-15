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
import equan.fund.tl as tl
import equan.fund.DataAPI_CI as CI

# 全局参数
DATE_FORMAT = CI.DATE_FORMAT

FUND_DATA_DIR = CI.FUND_DATA_DIR     # 基金数据存放目录

CAL_DATA_FILE = CI.CAL_DATA_FILE  # 日历文件存放目录

log = tl.get_logger()


class DataAPI:

    @staticmethod
    def get_cal(start, end, only_trade_date=True, return_type='list'):
        """返回时间期间内的所有日期

        数据存放在 %CAL_DATA_FILE% 文件中

        Arguments:
            start {str, %Y-%M-%d} -- 符合DATE_FORMAT格式的日期文本
            end {str, %Y-%M-%d} -- 符合DATE_FORMAT格式的日期文本

        Keyword Arguments:
            only_trade_date {bool} -- 返回仅交易日 (default: {True})
            return_type {str} -- 返回值类型 list，日期列表 | df 所有字段的dataframe

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

        if return_type == 'list':
            return df['cal_date'].to_list()
        else:
            return df

    @staticmethod
    def load_fund_daily(fund_id, start_date, end_date):
        """
        读取基金日线数据，仅包括交易日数据

        - 返回的日期仅是交易日，非交易日不返回
        - 如果当日无数据，则当日数据不返回
        - 按交易日期，由早到晚排序

        # FIXME 目前仍返回，有错误

        返回的DataFrame格式：
        index: date, 2020-03-12格式
        Data columns (total 3 columns):
        date             2 non-null object  日期，交易日
        price            0 non-null float64 单位净值
        pretrade_date    1 non-null object  前一交易日

        # FIXME 前一日计算有误，会有Nan的情况
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
            log.error('数据不存在，无法获得数据! ' + str(data_file))
            return None
        else:
            # 读取日历
            df_cal = DataAPI.get_cal(start_date, end_date, only_trade_date=True, return_type='df')            
            # 读取基金数据文件
            df_data = pd.read_csv(filepath_or_buffer=data_file, usecols=['FSRQ', 'DWJZ'])
            df_data.rename(columns={"FSRQ": "date", "DWJZ": "price"}, inplace=True)
            # 日期过滤：
            df_data = df_data.loc[(df_data.date >= start_date) & (df_data.date <= end_date)]

            # merge:
            df = df_cal.merge(df_data, how='right', left_on='cal_date', right_on='date')

            # 排序
            df = df.sort_values(by=['date'], ascending=True)
            # 将日期设置为index
            df.set_index(['date'], drop=False, inplace=True)

            return df[['date', 'pretrade_date', 'price']]


if __name__ == "__main__":
    # days = DataAPI.get_cal('2020-01-01', '2020-01-05')
    # print(days)
    df = DataAPI.load_fund_daily('005918', '2020-04-09', '2020-03-15')
    print(df)
    # print(df.info())
