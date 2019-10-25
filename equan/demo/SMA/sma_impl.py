#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sma_impl.py
@Time    :   2019/10/25 16:53:30
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   SMA回测 实现工具函数
'''
import pandas as pd
import tushare as ts
import equan.demo.SMA.sma as sma


def get_hs300():
    """
    取得沪深300数据

    Returns:
        pd.DataFrame -- 数据集合，code, name
    """
    data_file = r'data\hs300.csv'   # 本地文件路径
    field_list = ['code', 'name']   # 要返回的列名

    df = None
    if sma.DATA_SOURCE == 'tushare':
        df = ts.get_hs300s()
    elif sma.DATA_SOURCE == 'local':
        df = pd.read_csv(data_file)

    # df.to_csv(path_or_buf=r'data\hs300.csv')
    return df.loc[:, field_list]
