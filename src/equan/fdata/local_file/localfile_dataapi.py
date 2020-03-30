#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   localfile_dataapi.py
@Time    :   2020/03/30 19:56:32
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   本地文件数据访问API
'''
import os
import pandas as pd
import equan.fdata.fdata_tl as tl
import equan.fdata.fdata_settings as CI

log = tl.get_logger()


def get_cal(start, end, only_trade_date=True, return_type='list'):
    """返回时间期间内的所有日期

    数据存放在 %CAL_DATA_FILE% 文件中

    如原始文件格式出现问题，则抛出异常，不对异常做处理

    Arguments:
        start {str, %Y-%M-%d} -- 符合DATE_FORMAT格式的日期文本
        end {str, %Y-%M-%d} -- 符合DATE_FORMAT格式的日期文本

    Keyword Arguments:
        only_trade_date {bool} -- 返回仅交易日 (default: {True})
        return_type {str} -- 返回值类型 list，日期列表 | df 所有字段的dataframe

    Returns:
        [list of str] -- 返回日期，按日期先后顺序排列
    """
    # 注意文件是否存在
    if not os.path.exists(CI.CAL_DATA_FILE):
        log.error('日历数据文件不存在！')
        return None

    df = pd.read_csv(filepath_or_buffer=CI.CAL_DATA_FILE, encoding='utf-8')
    # 日期格式转换：
    df['cal_date'] = pd.to_datetime(df['cal_date'], format='%Y%M%d')
    df['cal_date'] = df['cal_date'].dt.strftime(CI.DATE_FORMAT)
    df['pretrade_date'] = pd.to_datetime(df['pretrade_date'], format='%Y%M%d')
    df['pretrade_date'] = df['pretrade_date'].dt.strftime(CI.DATE_FORMAT)
    # 日期过滤：
    df = df.loc[(df.cal_date >= start) & (df.cal_date <= end)]
    # 注意是否交易日
    if only_trade_date:
        df = df.loc[df.is_open == 1]
    # 注意返回的日期顺序
    df.sort_values(by='cal_date', inplace=True)
    # 重置index
    df.reset_index(inplace=True, drop=True)

    if return_type == 'list':
        return df['cal_date'].to_list()
    else:
        return df


def fund_daily_price(fund_id, start_date, end_date):
    """
    读取基金日线数据，仅包括交易日数据

    - 返回的日期仅是交易日，非交易日不返回
    - 如果当日无数据，则当日数据不返回
    - 按交易日期，由早到晚排序

    返回的DataFrame格式：
    index: date, 2020-03-12格式
    Data columns (total 3 columns):
    date             2 non-null object  日期，交易日
    price            0 non-null float64 单位净值
    pretrade_date    1 non-null object  前一交易日

    Arguments:
        fund_id {[type]} -- [description]
        start_date {[type]} -- [description]
        end_date {[type]} -- [description]

    Returns:
        [pandas.dataframe] -- 返回的数据，如果没有数据则返回None
    """
    data_file = CI.FUND_DATA_DIR + '{fund_symbol}.csv'.format(fund_symbol=fund_id)
    if not os.path.exists(data_file):
        log.error('数据不存在，无法获得数据! ' + str(data_file))
        return None
    else:
        # 读取日历
        df_cal = get_cal(start_date, end_date, only_trade_date=True, return_type='df')
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


# if __name__ == "__main__":
#     dates = get_cal(start='2019-01-01', end='2019-01-10')
#     print(dates)
