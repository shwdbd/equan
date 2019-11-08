#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   stock_pair_trading_corr.py
@Time    :   2019/11/06 12:26:43
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   股票配对交易 使用 协整回归方式

TODO 在简单临摹基础上，希望能加入以下内容：
1. 计算两个 股价 是否稳定 sationary
2. 

函数：
- get_data  取得基础数据
- strategy  策略执行
- stat      统计策略收益等评估参数
- draw_xxx  绘图函数

'''
import pandas as pd
import tushare as ts
import numpy as np
import matplotlib.pyplot as plt


STOCKS_PAIR = ['600199', '600702']  # 酒业，金种子酒，舍得酒

# 回测数据日期范围
START_DATE = '20100101'
END_DATE = '20130110'

# 交易信号指标
ZSCORE_OPEN = 1.5
ZSCORE_CLOSE = 0.5
# ZSCORE_OPEN = 1.2
# ZSCORE_CLOSE = 0.8


token = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'


def get_pro_api():
    """
    取得pro 的 python api接口
    :return: 接口对象
    """
    ts.set_token(token)
    return ts.pro_api()


ts_pro = get_pro_api()


def get_data():
    """
    取得数据
    返回值：DataFrame date|price_A,price_B
    """
    df_A = ts_pro.daily(
        ts_code=STOCKS_PAIR[0] + '.SH', start_date=START_DATE, end_date=END_DATE, fields='trade_date, close')
    df_B = ts_pro.daily(
        ts_code=STOCKS_PAIR[1] + '.SH', start_date=START_DATE, end_date=END_DATE, fields='close')
    data = pd.concat([df_A, df_B], axis='columns')
    data.rename(columns={'trade_date': 'date'}, inplace=True)    # 改index名
    # data.sort_values(by=['date'], a)
    data.set_index('date', inplace=True)    # 设置index
    data.columns = ['price_A', 'price_B']   # 改列名
    data.sort_index(inplace=True)
    data.dropna(inplace=True)   # TODO dropna函数要示例程序
    # TODO 数据中有NaN的情况

    # print(data.head())

    return data


def strategy(data):
    """
    执行策略

    入参：从get_data获得的dataframe
    返回：df: date| price_A, price_B, position_A, position_B

    1. 计算AB股价的关联系数；
    2. 根据AB股价，一阶拟合，得到斜率、截距
    3. 计算e，符合正态分布；
    4. 标准化e => zscore
    5. 根据zscore产生交易信号

    """
    # 计算关联系数
    df_corr = data.corr()
    print(df_corr)

    # 根据AB股价，一阶拟合，得到斜率、截距
    slope, intercept = np.polyfit(data.iloc[:, 0], data.iloc[:, 1], 1).round(2)
    print('slope = ' + str(slope))
    print('intercept = ' + str(intercept))
    # 绘制图形
    # draw_ABPriece_corr(data)

    # y = slope*x + intercept + e
    # e = y - (slope*x + intercept)
    # e就是AB股价的价差 spread
    data['spread'] = data.iloc[:, 1] - (slope*data.iloc[:, 0] + intercept)
    print(data['spread'].mean())

    # 标准化
    data['zscore'] = (data['spread'] - data['spread'].mean()
                      ) / data['spread'].std()
    print(round(data['zscore'].mean(), 2))
    # 绘制zscore图形
    # draw_zscore(data)

    # 根据zscore产生交易信号
    data['position_1'] = np.where(data['zscore'] > ZSCORE_OPEN, -1, np.nan)
    data['position_1'] = np.where(
        data['zscore'] < ZSCORE_OPEN,  1, data['position_1'])
    data['position_1'] = np.where(
        abs(data['zscore']) < ZSCORE_CLOSE, 0, data['position_1'])
    data['position_1'] = data['position_1'].fillna(method='ffill')
    data['position_2'] = -1 * np.sign(data['position_1'])

    return data


def draw_zscore(data):
    # 绘制zscore图形
    data['zscore'].plot()
    plt.axhline(1.5)
    plt.axhline(-1.5)
    plt.axhline(0)
    plt.axhline(0.5)
    plt.axhline(-0.5)
    plt.show()


def draw_ABPriece_corr(data):
    # 绘制AB两个股票的股价散点图
    plt.figure()
    plt.title('Stock Correlation')
    plt.plot(data['price_A'], data['price_B'], '.')
    plt.xlabel('600199')
    plt.ylabel('600702')
    plt.show()


def stat(data):
    """
    统计收益
    """
    # 股票收益
    data['return_A'] = np.log(data['price_A'] / data['price_A'].shift(1))
    data['return_B'] = np.log(data['price_B'] / data['price_B'].shift(1))

    # 策略收益，假设AB股票各持50%
    data['return_strategy'] = 0.5 * (data['position_1'].shift(
        1) * data['return_A']) + 0.5 * (data['position_2'].shift(1) * data['return_B'])

    # 绘图
    data[['return_A', 'return_B', 'return_strategy']
         ].dropna().cumsum().apply(np.exp).plot()
    plt.show()

# ---------


def draw_prices(data):
    """
    绘制 两个股票的走势图
    """
    # plt.figure(figsize=[8, 6])
    # data['price_A', 'price_B'].plot(figsize=[8, 6])

    plt.plot(data.index.values, data['price_A'])
    # plt.plot(data.index, data['price_B'])
    # data.plot(figsize=[8, 6])
    plt.xlabel('date')
    plt.ylabel('price')

    plt.show()


if __name__ == "__main__":
    data = get_data()
    # print(data.head())
    # draw_prices(data)
    df_position = strategy(data)
    stat(df_position)
