#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_picker.py
@Time    :   2019/10/30 13:29:13
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据获取工具

本模块通过一组函数，提供数据服务读服务，并通过参数空值从tushare读取，或从本地缓存文件读取

如果是local模式，则先从本地缓存文件到读取，如果没有则从tushare下载，然后再从缓存文件读取

本地文件生成csv，无index列，有标题列

'''
import pandas as pd
import os
import tushare as ts


DATA_SOURCE = 'local'   # tushare | local
DATA_FILE_DIR = r'data/tushare_cache/'    # 本地文件存放地址

CVS_INDEX = False   # 生成cvs文件是否有index列


def ts_pro():
    """
    取得pro 的 python api接口
    :return: 接口对象
    """
    token = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'
    ts.set_token(token)
    return ts.pro_api()


# 沪深300
def get_hs300s(fields=None):
    """
    根据tushare获取沪深300股票

    Keyword Arguments:
        fields {list} -- 返回的字段列表 (default: {None})

    Returns:
        pd.DataFrame -- 沪深300股票(结构同tushare)
    """
    # 加入本地缓存功能，找本地文件如没有，则网上下载
    CACHE_FILE_NAME = r'hs300.csv'
    if DATA_SOURCE == 'local':
        file_path = DATA_FILE_DIR + CACHE_FILE_NAME
        if not os.path.exists(file_path):
            print('从tushare上缓存hs300')
            ts.get_hs300s().to_csv(file_path, index=CVS_INDEX)
        df = pd.read_csv(file_path, parse_dates=['date'], dtype={
                         'code': 'str', 'name': 'str', 'weight': 'float64'})
    else:
        df = ts.get_hs300s()

    # 按字段要求返回
    if fields is None or len(fields) == 0:
        return df
    else:
        return df.loc[:, fields]


# 股票基本信息
def get_stock_basic():
    """
    取得tushare股票基本信息 （pro.stock_basic）

    返回字段参考：https://tushare.pro/document/2?doc_id=25

    Returns:
        pd.DataFrame -- pro.stock_basic返回的df
    """
    CACHE_FILE_NAME = r'stock_basic.csv'
    if DATA_SOURCE == 'local':
        file_path = DATA_FILE_DIR + CACHE_FILE_NAME
        if not os.path.exists(file_path):
            print('从tushare上缓存 股票列表stock_basic ')
            ts_pro().stock_basic().to_csv(file_path, index=CVS_INDEX)
        df = pd.read_csv(file_path, dtype={
                         'symbol': 'str', 'industry': 'str'})
    else:
        df = ts_pro().stock_basic()

    return df


def get_daily_basic_by_date(trade_date):
    CACHE_FILE_NAME = r'daily_basic_{0}.csv'.format(trade_date)
    if DATA_SOURCE == 'local':
        file_path = DATA_FILE_DIR + CACHE_FILE_NAME
        if not os.path.exists(file_path):
            print('从tushare上缓存 全部股票{0}指标  '.format(trade_date))
            ts_pro().daily_basic(trade_date=trade_date).to_csv(file_path, index=CVS_INDEX)
        df = pd.read_csv(file_path, dtype={'ts_code': 'str'})
    else:
        df = ts_pro().daily_basic(trade_date=trade_date)

    return df


# 每日指标
def get_daily_basic(ts_code, start_date, end_date, fields=None):
    """
    根据tushare获取股票每日指标

    字段参考：https://tushare.pro/document/2?doc_id=32

    Arguments:
        ts_code {string} -- 股票代码(tushare格式)
        start_date {yyyyMMdd日期} -- 开始日期
        end_date {yyyyMMdd日期} -- 结束日期

    Keyword Arguments:
        fields {[list of string]} -- 所需要的字段 (default: {None})

    Returns:
        pd.DataFrame -- 沪深300股票(结构同tushare)
    """
    CACHE_FILE_NAME = r'daily_basic_{0}_{1}_{2}.csv'.format(
        ts_code, start_date, end_date)
    if DATA_SOURCE == 'local':
        file_path = DATA_FILE_DIR + CACHE_FILE_NAME
        if not os.path.exists(file_path):
            print('从tushare上缓存 每日指标 {0} {1} {2} '.format(
                ts_code, start_date, end_date))
            ts_pro().daily_basic(ts_code=ts_code, start_date=start_date,
                                 end_date=end_date).to_csv(file_path, index=CVS_INDEX)
        df = pd.read_csv(file_path, dtype={'ts_code': 'str'})
    else:
        df = ts_pro().daily_basic(ts_code=ts_code, start_date=start_date, end_date=end_date)

    return df


# if __name__ == "__main__":
#     df = get_daily_basic(ts_code='600016.SH',
#                          start_date='20191028', end_date='20191029')

#     print(df.info())
#     print(df.head())

#     # print(df[df['ts_code'] == '600016.SH'].to_dict())
