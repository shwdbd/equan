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

'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


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
    return_by_log()
