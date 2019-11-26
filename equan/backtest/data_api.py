#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_api.py
@Time    :   2019/11/26 09:55:32
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   处理处理代码
'''
import datetime
import time
import equan.backtest.biz_tools as bt
from equan.backtest.tl import log, tushare
import pandas as pd


class HistoryDataAPI:
    """
    历史数据调用类
    """

    SAT = 'SAT'  # symbol为key，字段为index，日期为col
    TAS = 'TAS'  # 日期为key，字段为index，symbol为col
    TSA = 'TSA'  # 日期为key，symbol为index，字段为col

    def get_history(self, symbol, date_limit, fields=['open', 'close'], date_range=1, freq='1d', style='sat'):
        """
        获取历史数据

        - 只返回 context.previous_date 之前日期的数据（含previous_date）
        - attribute 返回的字段可以有：open, close
        - style类似优矿，有三种模式可以返回选择

        Arguments:
            symbol {str or list} -- 股票代码或代码列表，格式如：600016.SSE
            date_limit {日期str} -- 数据最晚的一天日期（含）

        Keyword Arguments:
            fields {list of str} -- 返回数据的字段 (default: {['open', 'close']})
            date_range {int} -- 回溯的天数（交易日） [description] (default: {1})
            freq {str} -- [description] (default: {'1d'})
            style {str} -- 返回数据格式 (default: {'sat'})

        Returns:
            [type] -- 特定格式的字典
        """

        data = {}  # 返回数据包
        if style.upper() == HistoryDataAPI.TSA:
            # TSA模式，日期为key，symbol为index，字段为col

            # 按日期从tushare取数据
            # date_list = pd.date_range(end=date_limit, periods=date_range).strftime('%Y%m%d').tolist()
            date_list = bt.Trade_Cal.date_range(
                end=date_limit, periods=date_range)
            print(date_list)

            for date in date_list:
                print(date)
                df = tushare.daily( ts_code=['600016.SH', '600030.SH'], trade_date=date, fields=fields)    # index是股票代码
                # print(df.head())
                data[date] = df

        return data


if __name__ == "__main__":
    data_api = HistoryDataAPI()

    symbol = ['600016', '600030']
    fields = ''
    max_history_window = 5    # 缓存前置的数据天数
    data = data_api.get_history(symbol=symbol, date_limit='20190101',
                                style=HistoryDataAPI.TSA, date_range=(1+max_history_window))
    print(data)
    print(data['20181227'])
