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
    data_basic = ts_pro.stock_basic()
    data_basic = data_basic[data_basic['symbol'].isin(stock_pool.code)]     # 选择在stock_pool中
    data_basic = data_basic.loc[:, ['symbol', 'industry']]
    data_basic.rename({'symbol':'code'})
    # print(data_basic.head())

    # 每日指标, pe, pb, 总市值
    df_index = ts_pro.daily_basic(trade_date='20191025').loc[:, ['ts_code','close','pe', 'pb', 'total_mv'] ]
    df_index['code'] = df_index['ts_code'].apply(lambda x : x[ : x.index('.')]) # 整理ts_code的后缀
    df_index = df_index[df_index['code'].isin(stock_pool.code)]
    # print(df_index.head())

    # 合并成总的df
    # df = stock_pool.merge(df_index, how='left', on='code')
    # print(df.head())

    df_merge = lambda x, y : x.merge(y, how='left', on='code')
    df = np.array([stock_pool, df_index]).apply( df_merge )
    print(df.head())




if __name__ == "__main__":
    get_equity_pool()
