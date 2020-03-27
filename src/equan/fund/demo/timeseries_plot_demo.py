#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   timeseries_plot_demo.py
@Time    :   2020/03/27 18:09:59
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   时间序列绘图代码示例
'''
import pandas as pd
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']


if __name__ == "__main__":
    # 绘制基金价格图形
    df = pd.read_csv(r'data_file/ttjj/005918.csv', index_col=['FSRQ'], usecols=['FSRQ', 'DWJZ'])
    df = df[(df.index >= '2019-01-01') & (df.index <= '2019-12-31')]
    print(df.head())
    print(df.shape[0])

    # draw:
    plt.figure(figsize=(6, 6))
    plt.title('005918 基金净值')
    plt.plot(df.index, df['DWJZ'])
    plt.savefig('demo_1.jpg')   # 保存成文件
    plt.show()
    
