#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sma.py
@Time    :   2019/10/24 22:08:02
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   移动平均线策略



'''
# import pandas as pd
# import tushare as ts


# 全局参数
DATA_SOURCE = 'local'   # 数据来源，tushare | local
BASE_DATE = '20191025'  # 基准日期


class EquityTradingStrategyFrame:
    """
    股票交易回测框架
    """

    def seek_equity(self):
        """
        选股函数

        Returns:
            list of str -- 股票代码列表
        """
        return []


    def strategy(stock_list):
        """
        策略实现接口，本函数需要被实现
        
        返回的DataFrame有字段:
        date, code, position
        其中：
        date, datetime64格式日期
        code, 6位数字股票代码
        position，仓位标志, 1买入,-1卖出,0平仓

        Arguments:
            stock_list {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """

        return None
