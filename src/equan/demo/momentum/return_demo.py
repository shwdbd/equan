#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   return_demo.py
@Time    :   2019/11/13 13:40:39
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   股票收益计算

TODO df.cumsum示例
file:///C:/wjjNAS/SynologyDrive/07%20dev/pandas_doc/reference/api/pandas.DataFrame.cumsum.html#pandas.DataFrame.cumsum


- return_by_log     对数收益率计算示例
- position_count    仓位统计示例
- max_retreat       最大回撤


'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def position_count():
    """
    仓位统计示例

    1. 交易次数统计（分Long、Short）
    2. 持仓天数计算，[d1, d2, ...]

    统计交易信息，返回一个df：
    1. 交易方向(long or short)|开仓日期|关仓日期|持仓天数(交易日)|买入价|卖出价|期间收益率|
    TODO 此函数做成unittest
    """
    # 准备模拟数据 date|postion
    price_list = [0, 1, 1, 1, 0, 0, -1, -1, 0]  # 1：Long仓位， -1：Short仓位，0关闭仓位
    data = pd.DataFrame(price_list, columns=['交易信号'], index=pd.date_range(
        '20190101', periods=len(price_list)))
    # print(data)

    # 计算买入卖出信号, 返回 [[1, 开仓日期, 关仓日期], ... ]
    data['开关信号'] = np.where(
        (data['交易信号'] != 0) & (data['交易信号'].shift(1) == 0), data['交易信号'], np.nan)
    data['开关信号'] = np.where(
        (data['交易信号'] == 0) & (data['交易信号'].shift(1) != 0), data['交易信号'], data['开关信号'])
    data.dropna(subset=['开关信号'], inplace=True)
    del(data['开关信号'])
    print(data)

    df_open = data[ data['交易信号']!=0 ].reset_index()
    df_open.rename(columns={'index':'开仓日期'}, inplace=True)
    df_close = data[ data['交易信号']==0 ][1:].reset_index()
    df_close.rename(columns={'index':'关仓日期'}, inplace=True)
    print(df_open)
    print(df_close)

    df = pd.concat([df_open, df_close['关仓日期']], axis='columns')
    print(df)
    # print(data[ data['交易信号']!=0 ])
    # print(data[ data['交易信号']==0 ][1:])

    # 按行分割成小的df：
    price_list = [0, 1, 1, 1, 0, 0, -1, -1, 0]  # 1：Long仓位， -1：Short仓位，0关闭仓位
    data = pd.DataFrame(price_list, columns=['交易信号'], index=pd.date_range(
        '20190101', periods=len(price_list)))
    print(data)
    print(data[ (data.index >= '20190102') & (data.index < '20190105') ])


def return_by_log():
    """
    用对数收益率计算 股票收益
    """
    # 准备模拟数据 date|price
    price_list = [10, 10, 15, 12, 17, 15, 10]
    data = pd.DataFrame(price_list, columns=['价格'], index=pd.date_range(
        '20190101', periods=len(price_list)))
    print(data)

    # 买卖方式：当日按前一日价格购买，今日价格卖出
    data['买入价'] = data['价格'].shift(1)
    data['买出价'] = data['价格']

    # 计算连续收益率
    data['连续收益率'] = np.log(data['买出价']/data['买入价'])
    print(data)
    # 累计连续收益率
    data['连续收益率累计'] = data['连续收益率'].dropna().cumsum()
    print(data)

    # 还原为 离散收益率
    data['离散收益率'] = np.exp(data['连续收益率']) - 1
    data['离散收益率累计'] = (1+data['离散收益率'].dropna()).cumprod()
    data['离散收益率累计_从连续收益率累计换算'] = np.exp(data['连续收益率累计'])

    # 离散 转 连续
    data['连续收益率累计_换算'] = np.log(data['离散收益率累计'])

    print(data)
    # 绘图
    data[['价格', '连续收益率累计', '离散收益率累计']].plot()
    plt.show()


if __name__ == "__main__":
    position_count()
