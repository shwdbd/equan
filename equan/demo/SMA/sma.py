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
BASE_DATE = '20191025'  # 基准日期


def get_equity_pool():
    """
    取得选股后的股票列表

    Returns:
        list -- 股票代码列表
    """
    # 取得股票池，默认沪深300
    stock_pool = impl.get_hs300()
    print('取得沪深300股票, 数量={0}'.format( stock_pool.shape[0] ))
    # print(stock_pool.head())

    # 取得股票池的pe、pb等信息
    # 取 BASE_DATE 的数据


    return []


if __name__ == "__main__":
    get_equity_pool()
    # impl.download_tushare_data()
