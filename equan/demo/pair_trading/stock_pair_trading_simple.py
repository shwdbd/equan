#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   stock_pair_trading_simple.py
@Time    :   2019/11/05 15:27:05
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   股票配对交易 最简单的实现

函数说明:
- get_data      取得策略需要的tushare数据；
- strategy      策略实现，计算仓位
- stat          策略评估

'''
import pandas as pd
import tushare as ts
import numpy as np
import matplotlib.pyplot as plt


STOCKS_PAIR = ['600199', '600702']  # 酒业，金种子酒，舍得酒

# 回测数据日期范围
START_DATE = '20100101'
END_DATE = '20180131'

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
    返回DataFrame:
    date | price_A, price_B
    """
    df_A = ts_pro.daily(
        ts_code=STOCKS_PAIR[0] + '.SH', start_date=START_DATE, end_date=END_DATE, fields='trade_date, close')
    # print(df_A.shape[0])
    df_B = ts_pro.daily(
        ts_code=STOCKS_PAIR[1] + '.SH', start_date=START_DATE, end_date=END_DATE, fields='close')
    # print(df_A.shape[0])
    data = pd.concat([df_A, df_B], axis='columns')

    # 修改列名
    data.columns = ['date', 'price_A', 'price_B']
    # 设置index
    data.set_index('date', inplace=True)
    # TODO 写set_index的demo， set_index('列名')和set_index(df['列名'])的区别
    # 排序
    data.sort_index(inplace=True)

    # TODO 要考虑到某些日期，有一个股票无价格数据，如20100130、20100131

    return data


def strategy(data):
    """
    执行策略

    入参：从get_data获得的dataframe
    返回：df: date| price_A, price_B, position_A, position_B
    """
    # if not data or data.empty():
    #     raise Exception('数据为空！')

    # 计算价差
    data['priceDelta'] = data['price_A'] - data['price_B']
    # # 绘制价差图
    # data['priceDelta'].plot(figsize=[8, 6])
    # plt.ylabel('spread')
    # plt.axhline(data['priceDelta'].mean())
    # plt.show()

    # 标准化价差
    data['zscore'] = (data['priceDelta'] -
                      np.mean(data['priceDelta'])) / np.std(data['priceDelta'])
    # 绘图
    # data[['zscore']].plot(figsize=[8, 6])
    # plt.ylabel('spread')
    # plt.axhline(data['zscore'].mean())
    # plt.show()

    # 计算仓位
    # TODO np.where 函数示例
    # TODO np.sign 函数示例
    data['position_1'] = np.where(data['zscore'] > 1, -1, np.nan)
    data['position_1'] = np.where(data['zscore'] < 1,  1, data['position_1'])
    data['position_1'] = np.where(
        abs(data['zscore']) < 0.5, 0, data['position_1'])
    data['position_1'] = data['position_1'].fillna(method='ffill')
    data['position_2'] = -1 * np.sign(data['position_1'])

    # 删除不需要返回的字段
    # del(data['priceDelta', 'zscore']) # TODO 修改这部分错误
    print(data.head(20))

    return data


def stat(data):
    """
    统计收益
    """
    # 股票收益
    data['return_A'] = np.log(data['price_A'] / data['price_A'].shift(1))
    data['return_B'] = np.log(data['price_B'] / data['price_B'].shift(1))

    # 策略收益，假设AB股票各持50%
    data['return_strategy'] = 0.5 * ( data['position_1'].shift(1) * data['return_A'] ) +  0.5 * ( data['position_2'].shift(1) * data['return_B'] )

    # 绘图
    data[['return_A', 'return_B', 'return_strategy']].dropna().cumsum().apply(np.exp).plot()
    plt.show()


if __name__ == "__main__":
    data = get_data()
    # print(data.head())
    df_position = strategy(data)
    stat(df_position)
