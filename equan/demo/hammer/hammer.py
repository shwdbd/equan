#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   hammer.py
@Time    :   2019/11/18 13:32:05
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   锤子线策略实现
'''
import pandas as pd
import numpy as np


class HammerStrategy:
    """
    锤子线 策略回测
    """

    # 参数
    settings = {
        'STOCK_CODES': ['600016'],     # 待回测的股票代码
        'START_DATE': '20120101',     # 回测起始日期
        'END_DATE': '20170101',
        'HAMMER.ENTITY_TO_PRICE': 0.03,   # 实体/股价 的上限
        'HAMMER.HEADER_TO_TAIL': 0.5,   # 上影线长度/下影线长度
        'HAMMER.TAIL_TO_ENTITY': 2,   # 下影线长度/实体
        'MA.windows' : 10,   # 观察窗口
        'STOPLOSE_TRIGGER' : 1,  # 表示当价格偏离均线满足几倍标注按察时止损
    }

    def get_data(self):
        """
        取得数据包

        df: index|date,open,close,high,low;order by date
        """
        pass

    def find_hammer(self, data):
        """
        识别 锤子线 标志

        在 data 中新增一列：hammer,1表示当日是锤子线，0表示不是
        """
        # 计算K Bar的各部分长度
        data['k_body'] = abs( data['open']-data['close'] )


        return data

    def get_return(self):
        """
        汇总计算收益
        """
        pass

    def back_test(self):
        """
        交易回测

        1、股票代码
        2、回测周期
        3、其他参数

        """
        # TODO wait for impl
        pass


if __name__ == "__main__":
    # sty = HammerStrategy()
    # sty.back_test()

    # 判断是否锤子
    sty = HammerStrategy()

    # DAY1: YES, 锤子形
    # DAY2: NO, 上影线=Bar=下影线
    # DAY3: NO, Bar过长
    # DAY4：NO, 上影线过长
    # DAY5: YES，十字星
    # df: index|date,open,close,high,low;order by date
    data_dict = {
        "date": pd.date_range('20190101', periods=5),
        "high": [10.01, 11, 11, 11, 11],
        "open": [10, 10, 10, 10, 10],
        "close": [9, 9, 9, 9, 9],
        "low": [1, 2, 2, 2, 2],
    }
    data = pd.DataFrame(data_dict)
    print(data)

    data = sty.find_hammer(data)
    print(data)
