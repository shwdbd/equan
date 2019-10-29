#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   demo_sma.py
@Time    :   2019/10/26 19:22:59
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   金程教育的演示代码实现


1. 选股
2. 选择某一股票
3. SMA策略实现
4. 策略评估

1.1 取hs300
1.2 获取hs300的close, pe, pb, 行业
1.3 合并成 data_df
    判断 成长性、高风险
1.4 group找出每个行业 PE*PB 的前三名股票
1.5 获得最终待投资股票池, list of stock code

2.1 选择某股票，如：

3.1 获取该股票7年的价格数据 data_df
3.2 计算SMA_20, SMA_60
3.3 根据 金叉、死叉 原理判断 开仓信号position
3.4 计算每天的return
3.5 计算策略每天的return_sma
3.6 绘制 return ， return_sma 的图形
3.7 计算 收益、风险、回撤、总开仓次数
3.8 计算 shape_ration

附加：
0.1 去除 short 的收益，重新计算收益

'''
import pandas as pd
import tushare as ts
import numpy as np
from functools import reduce


token = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'
# 取得tushare api


def get_pro_api():
    """
    取得pro 的 python api接口
    :return: 接口对象
    """
    ts.set_token(token)
    return ts.pro_api()


ts_pro = get_pro_api()


def get_equity_pool():
    """
    1. 选股操作

    1.1 取hs300
    1.2 获取hs300的close, pe, pb, 行业
    1.3 合并成 data_df
        判断 成长性、高风险
    1.4 group找出每个行业 PE*PB 的前三名股票
    1.5 获得最终待投资股票池, list of stock code
    """
    # 1.1 取hs300
    stock_pool = ts.get_hs300s()
    stock_pool = stock_pool.loc[:, ['code', 'name']]
    # print(stock_pool.head())

    # 1.2 获取hs300的close, pe, pb, 行业
    # 600000 浦发银行

    # # 基本信息，行业
    df = _get_stock_info_by_tushare(stock_pool)
    

    # 1.3 TODO 计算基本标识

    # 1.4 group找出每个行业 PE*PB 的前三名股票
    # 添加 pe*pb
    df['PE_PB'] = df['pe'] * df['pb']
    print(df.head())
    # gp_df = df.groupby(['行业'])
    # 列出每个行业的PE*PB前三名
    # TODO 需要去除 NaN 600100
    df.sort_values(by=['PE_PB'], inplace=True)
    df_stock = df.groupby(by='行业').head(3).sort_values(by=['行业'])
    print(df_stock.head(20))
    stock_list = list(df_stock.index)
    return stock_list


def sma(stock_code):
    """
    回测某一股票的SMA策略
    
    """
    # 3.1 获取该股票7年的价格数据 data_df
    # 需要字段 trade_date, close
    df = ts_pro.daily_basic(ts_code='000423.SZ', start_date='20100101', end_date='20191028', fields='trade_date, close')
    # df.to_csv('data\\000423.csv')
    print(df.info())

    # 3.2 计算SMA_20, SMA_60
    


    # 3.3 根据 金叉、死叉 原理判断 开仓信号position
    # 3.4 计算每天的return
    # 3.5 计算策略每天的return_sma
    # 3.6 绘制 return ， return_sma 的图形
    # 3.7 计算 收益、风险、回撤、总开仓次数
    # 3.8 计算 shape_ration

    


def _get_stock_info_by_tushare(stock_pool):
    """
    根据给定的股票池信息

    返回一个df，code为index，其余列有：
    name, industry, ts_code, close, pe, pb, total_mv 

    Arguments:
        stock_pool {pd.DataFrame} -- 给定的股票池信息，'code', 'name' 两列
    """

    # # 基本信息，行业
    df_basic = ts_pro.stock_basic()
    df_basic = df_basic[df_basic['symbol'].isin(
        stock_pool.code)]     # 选择在stock_pool中
    df_basic = df_basic.loc[:, ['symbol', 'industry']]
    df_basic.rename(columns={'symbol': 'code'}, inplace=True)
    # print(df_basic.head())

    # 每日指标, pe, pb, 总市值
    df_index = ts_pro.daily_basic(trade_date='20191025').loc[:, [
        'ts_code', 'close', 'pe', 'pb', 'total_mv']]
    df_index['code'] = df_index['ts_code'].apply(
        lambda x: x[: x.index('.')])  # 整理ts_code的后缀
    df_index = df_index[df_index['code'].isin(stock_pool.code)]
    # print(df_index.head())

    # 合并成总的df
    df = reduce(lambda x, y: x.merge(y, how='left', on='code'),
                [stock_pool, df_basic, df_index])
    df.rename(columns={'code': '股票代码', 'name': '股票名称', 'industry': '行业',
                       'close': '价格', 'total_mv': '总市值'}, inplace=True)
    df.set_index('股票代码', inplace=True)

    return df


if __name__ == "__main__":
    # get_equity_pool()

    # 000423 东阿阿胶
    sma('000423')