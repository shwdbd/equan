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
import tushare as ts
import equan.demo.SMA.sma_impl as impl


# 全局参数
DATA_SOURCE = 'local'   # 数据来源，tushare | local


def get_equity_pool():
    """
    取得选股后的股票列表

    Returns:
        list -- 股票代码列表
    """
    hs300 = impl.get_hs300()
    print(hs300.head())

    return []


if __name__ == "__main__":
    get_equity_pool()
