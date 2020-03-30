#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_api.py
@Time    :   2020/03/30 20:15:46
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基于本地文件系统的数据API
'''
import equan.fdata.local_file.localfile_dataapi as localfile_api


def get_cal(start, end, only_trade_date=True, return_type='list'):
    """返回时间期间内的所有日期，前后都包括

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
    # 本地文件实现
    return localfile_api.get_cal(start=start, end=end, only_trade_date=only_trade_date, return_type=return_type)


def fund_daily_price(fund_id, start_date, end_date):
    """
    返回基金日线数据，仅包括交易日数据

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
    return localfile_api.fund_daily_price(fund_id, start_date=start_date, end_date=end_date)
