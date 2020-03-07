#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   my_aip.py
@Time    :   2020/03/07 19:31:43
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   使用框架计算
'''
from equan.fund.fund_backtesting import FundBackTester
import pandas as pd
from equan.fund.fund_backtesting_impl import Account
from equan.fund.tl import log
import datetime


class MyTest(FundBackTester):

    def __init__(self, start=None, end=None, fund_symbol=None):
        super().__init__()
        self.start_date = start
        self.end_date = end
        self.unverise = fund_symbol

        # 初始化账户
        self.account = Account('定投账户', 10000*10)    # 初始账户10W元
        log.info('初始化账户')

        self.pr_input = 1000     # 每期预期投入资金

    def initialize(self):
        # 准备数据
        log.info('计算移动平均线 和 标准差 ... ')
        self.context.df['SMA_20'] = self.context.df['price'].rolling(window=20, min_periods=1).mean()
        self.context.df['std_20'] = self.context.df['price'].rolling(window=20, min_periods=1).std()
        self.context.df['price_ysd'] = self.context.df['price'].shift(1)     # 计算昨天的价格
        # print(self.context.df.head())
        # print(self.context.df.loc['2020-01-07', '星期'])

        # 星期数据的计算
        self.context.df['星期'] = self.context.df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').weekday()+1)

    def date_handle(self, context):
        # 每日执行
        # log.info('today = ' + context.today)
        today = context.today
        df = context.df
        acct = context.get_account()
        # log.info('week = {0}'.format(df.loc[context.today, '星期']))
        # log.info('account = ' + str(context.account))

        week = df.loc[context.today, '星期']
        if week == 1:       # 仅周一运行
            nap = (df.loc[today, 'price'] - df.loc[today, 'SMA_20'])/df.loc[today, 'std_20']
            log.info('{0} nap = {1} '.format(today, nap))
            if nap >= -0.2 and nap <= 0.2:
                buy_amount = self.pr_input
            elif nap > 0.2 and nap <= 1:
                buy_amount = self.pr_input * 0.5
            elif nap > 1:
                buy_amount = self.pr_input * 0
            elif nap < -0.2 and nap >= -1:
                buy_amount = self.pr_input * 1.5
            elif nap < -1:
                buy_amount = self.pr_input * 2
            else:
                buy_amount = 0

            if buy_amount != 0:
                # 下单
                acct.order(date=today, securiy_id=self.unverise, amount=buy_amount, price=None)
                log.info('{0} 买入 {1} '.format(today, buy_amount))
        
        # TODO 要考虑 止盈、止亏


if __name__ == "__main__":
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180)         # 设置打印宽度(**重要**)
    pd.set_option('display.max_columns', 500)

    # 开始回测
    tc = MyTest()
    tc.start_date = '2020-01-01'
    tc.end_date = '2020-01-31'
    tc.unverise = '005918'  # 基金
    # print(tc.get_data().head())
    tc.run()

    # # 下单操作：
    # acct = Account('wjj', initial_capital=2000)
    # # print(acct)
    # # print(acct.get_orders('2019-01-01'))
    # # print(acct.get_position('0000-00-00'))
    # # order
    # r = acct.order("2019-01-01", "000001", amount=100)
    # print(r)
    # print(acct.get_orders('2019-01-01'))
    # r = acct.order("2019-01-01", "000002", amount=-100)
    # print(r)
    # print(acct.get_orders('2019-01-01'))

    

