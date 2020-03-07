#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   aip.py
@Time    :   2020/03/07 10:22:31
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基金定投初步研究 automatic investment plan

想法：
0. 每周一购买基金1000元；
1. 计算基金前20日的净值移动平均数A和标准差S
2. 如果基金当日价格P：
   if P-A in [-0.2S, +0.2S] then 买入1000元；
   if P-A in (0.2S, 1S] then 买入500元；（少买）
   if P-A in (1S, ) then 买入0元；（不买）
   if P-A in (-1S, -0.2S] then 买入1500元；（多买）
   if P-A in (, -1S] then 买入2000元；（多买）
3. 如果目前总盈利Pr:
   Pr > 30%，全部卖出；止盈
   Pr < -30%，全部卖出。止亏
4. 年底全部账户卖出清空。
OVER

主要函数：
+ get_data  准备数据
+ backtesting   策略回测

'''
import pandas as pd
import datetime
import numpy as np


# 全局参数：
start_date = '2020-03-01'
end_date = '2020-03-04'
# 买的参数：
fund_symbol = '005918'  # 005918 天弘沪深300ETF连接C

# TODO 考虑手续费问题
# 资金:
pr_input = 1000     # 每期预期投入资金


def get_data():
    # 取得基金日线数据
    # 返回df: date|price,  order by date desc
    data_file_dir = r'src/equan/fund/'
    data_file = data_file_dir + '{fund_symbol}.csv'.format(fund_symbol=fund_symbol)
    df = pd.read_csv(filepath_or_buffer=data_file, usecols=['FSRQ', 'DWJZ'])
    df.rename(columns={"FSRQ": "date", "DWJZ": "price"}, inplace=True)
    # 日期过滤
    df = df.loc[(df.date >= start_date) & (df.date <= end_date)]

    df['星期'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').weekday()+1)
    # df = df.set_index('date')
    df = df.sort_values(by=['date'], ascending=True)
    df.reset_index(inplace=True, drop=True)
    return df


def run_stragy():
    # 策略运行

    df = get_data()

    # 计算移动平均线
    df['SMA_20'] = df['price'].rolling(window=20, min_periods=1).mean()
    df['std_20'] = df['price'].rolling(window=20, min_periods=1).std()
    # df['SMA_60'] = df['price'].rolling(window=60, min_periods=1).mean()
    # df['std_60'] = df['price'].rolling(window=60, min_periods=1).std()
    # 计算昨天的价格
    df['price_ysd'] = df['price'].shift(-1)

    # 其他参数：
    df['投入资金'] = 0      # 应当投入资金
    df['购买份数'] = 0      # 买入基金份数
    df['持仓总份数'] = 0      # 持仓总份数
    df['资产价格'] = 0           # 资产价格
    df['当日成交金额'] = 0           # 成交金额
    # print(df.tail())
    # print(df.head())

    # 按日期大轮询：
    total_in = 0        # 总投入资金
    yestday_hold = 0    # 上一日总持仓数
    for row in range(0, len(df)):
        record = df.loc[row]
        # print('{0} , {1}'.format(record["date"], record["price"], ))

        # TODO 将策略抽象成一个函数
        # 只有周一才进行买卖：
        position = 0
        if record['星期'] == 1:
            nap = (record['price'] - record['SMA_20'])/record['std_20']
            print('{0} nap = {1} '.format(record['date'], nap))
            if nap >= -0.2 and nap <= 0.2:
                position = pr_input
            elif nap > 0.2 and nap <= 1:
                position = pr_input * 0.5
            elif nap > 1:
                position = pr_input * 0
            elif nap < -0.2 and nap >= -1:
                position = pr_input * 1.5
            elif nap < -1:
                position = pr_input * 2
            else:
                position = 0
            print('{0} 买入 {1} '.format(record['date'], position))
        # TODO 要考虑 止盈、止亏

        # 日终后处理：
        # TODO 要考虑当日是否可买入
        df.loc[row, '投入资金'] = position
        df.loc[row, '购买份数'] = round(position/record['price'])
        df.loc[row, '当日成交金额'] = round(df.loc[row, '购买份数'] * record['price'], 2)
        total_in += df.loc[row, '当日成交金额']
        df.loc[row, '持仓总份数'] = yestday_hold + df.loc[row, '购买份数']
        yestday_hold = df.loc[row, '持仓总份数']

    # 计算每日的资产价格：
    df['资产价格'] = np.round(df['持仓总份数']*df['price'], 2)
    print('总投入:' + str(total_in))

    # TODO 生成策略结果，导出文件
    # 输出结果包括：
    # TODO 总业绩，包括：收益率、benchmark收益率、交易次数、最大回撤回
    # TODO 仓位变更记录表
    # TODO 每日明细记录表
    # TODO 曲线图


    print(df.tail(10))

if __name__ == "__main__":
    df = get_data()
    print(df.head(5))

    # run_stragy()
