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


def download_tushare_data():
    """
    下载tushare数据到本地
    """
    # 1.hs300,  中证500，
    # 2. stock_basic( symbol, name , industry,  )  where list_status='L' 仅上市
    # 3. daily_basic( symbol, trade_date, close, pe, pb, total_mv市值)  trade_date 为一个全局参数
    # 4. 希望再加上一个停牌信息

    file_dir = r'data/'
    date = '20191025'

    # # 1
    # file_name = r'stock_basic.csv'
    # df = ts.get_stock_basics().loc[:, [
    #     'symbol', 'name', 'industry']]
    # # print(df.head())
    # df.to_csv(path_or_buf=file_dir + file_name)
    # print('股票清单导出到' + file_name)

    # 2 导出所有的股票的价格数据
    # TODO 按日下载，然后检查
    # FIXME 这里需要使用tushare_pro的api接口
    file_name = r'daily_basic_{date}.csv'.format(date=date)
    df = ts.daily_basic(trade_date = date).loc[:, [
        'ts_code', 'trade_date', 'close', 'pe', 'pb', 'total_mv']]
    print(df.head())
    # df.to_csv(path_or_buf=file_dir + file_name)
    # print('股票清单导出到' + file_name)

