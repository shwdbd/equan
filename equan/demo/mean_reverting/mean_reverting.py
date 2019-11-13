#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   mean_reverting.py
@Time    :   2019/11/13 15:04:37
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   均值回归 临摹代码

- get_data                  取得沪深300的数据
- strategy                  均值反转策略
- strategy_estimator        策略评估

'''
import pandas as pd
import tushare as ts
import numpy as np
import matplotlib.pyplot as plt

# 回测指数
INDEX_CODE = '000300.SH'
# 回测数据日期范围
START_DATE = '20100101'
END_DATE = '20140630'
# 均值SMA计算天数
SMA_DAYS = 50
# 开仓距离
THESHOLD = 250


token = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'


def get_pro_api():
    """
    取得pro 的 python api接口
    :return: 接口对象
    """
    ts.set_token(token)
    return ts.pro_api()


def get_data():
    """
    取得 策略基础数据 的数据

    df: date|price ;  按date升序排序
    price为收盘价,close

    """
    df = get_pro_api().index_daily(ts_code=INDEX_CODE, start_date=START_DATE,
                                   end_date=END_DATE, fields=['trade_date', 'close'])
    df.rename(columns={'trade_date': 'date', 'close': 'price'}, inplace=True)
    df.sort_values(by='date', ascending=True, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    return df


def strategy(data):
    """
    执行策略计算

    返回data:
    date|price,position
    """
    # 计算SMA均线
    data['SMA'] = data['price'].rolling(SMA_DAYS).mean()

    # 计算price距离SMA均线的价差
    data['distance'] = data['price'] - data['SMA']

    # 绘制价差与SMA的关系图
    # draw_distance(data)

    # 根据价差计算仓位标识
    data['position'] = np.where(data['distance'] > THESHOLD, -1, np.nan)
    data['position'] = np.where(
        data['distance'] < -THESHOLD, 1, data['position'])
    data['position'] = np.where(
        data['distance']*data['distance'].shift(1) < 0, 0, data['position'])
    data['position'] = data['position'].ffill().fillna(0)

    # 绘制仓位图
    # draw_position(data)

    return data


def strategy_estimator(data):
    """
    计算策略收益    
    """

    # 计算股票收益
    data['return'] = np.log(data['price']/data['price'].shift(1))

    # 计算策略收益
    data['sgy_return'] = data['position'].shift(1) * data['return']
    data['sgy_return_cum'] = data['sgy_return'].dropna().cumsum()

    # TODO 计算最终收益率

    # TODO 计算交易次数，列出买卖清单

    # TODO 计算最大回撤

    # 绘制收益图
    draw_return(data)


def draw_return(data):
    data[['sgy_return', 'return']].dropna().cumsum().apply(np.exp).plot(figsize=(10, 6))
    plt.show()


def draw_position(data):
    """
    绘制仓位图

    TODO 子图绘制：价差与SMA的关系图
    """
    data[['position']].dropna().plot(figsize=(10, 6))
    plt.show()


def draw_distance(data):
    """
    绘制价差与SMA的关系图
    """
    data[['distance']].dropna().plot(figsize=(10, 6))
    plt.axhline(THESHOLD, color='r')
    plt.axhline(-THESHOLD, color='r')
    plt.axhline(0, color='r')
    plt.show()


def draw_price(data):
    """绘制价格走势图
    """
    data[['price']].dropna().plot(figsize=(10, 6))
    plt.show()


if __name__ == "__main__":
    data = get_data()
    # draw_price(data)    # 绘制价格走势图
    data = strategy(data)

    strategy_estimator(data)    # 计算收益

    print(data.tail(100))
