#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   zfb_fund.py
@Time    :   2020/03/29 19:07:22
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   支付宝HS300指数基金 定投策略计算
'''

from equan.fund.fund_backtesting import FundBackTester
from equan.fund.fund_backtesting_impl import Account, FundUnverise
import equan.fund.tl as tl
import pandas as pd
import datetime

log = tl.get_logger()


class ZFB_HS300Index_Fund(FundBackTester):
    """支付宝HS300指数基金 定投策略

    基于移动平均线，加减标准差的做法，2020年2月开始

    """

    def __init__(self):
        super().__init__()
        # 账户
        fund_acct = Account('基金定投账户', initial_capital=10*10000)
        self.get_context().add_account(fund_acct)

        # 资产池
        self.set_unverise(FundUnverise(['000000']))

        self.pr_input = 1000     # 每期预期投入资金
        self.sma_window = 20     # 移动平均窗口大小

    def initialize(self):
        # 回测前准备
        # 准备数据
        log.info('计算移动平均线 和 标准差 ... ')
        df = self.get_context().data['005918']
        df['SMA_20'] = df['price'].rolling(window=self.sma_window, min_periods=1).mean()
        df['std_20'] = df['price'].rolling(window=self.sma_window, min_periods=1).std()
        df['price_ysd'] = df['price'].shift(1)     # 计算昨天的价格
        # print(df.head())
        # print(df.loc['2020-01-07', '星期'])

        # 星期数据的计算
        df['星期'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').weekday()+1)

    def date_handle(self, context):
        # 日间业务逻辑

        # log.info('today = ' + context.today)
        today = context.today
        df = self.get_context().data['005918']
        acct = context.get_account('基金定投账户')

        week = df.loc[context.today, '星期']
        if week == 5:       # 周5运行，决定下周1是否买入
            nap = (df.loc[today, 'price'] - df.loc[today, 'SMA_20'])/df.loc[today, 'std_20']
            log.info('{0} nap = {1} '.format(today, nap))
            if nap >= -0.1 and nap <= 0.1:
                buy_amount = self.pr_input
            elif nap > 0.1 and nap <= 1:
                buy_amount = self.pr_input * 0.5
            elif nap > 1:
                buy_amount = self.pr_input * 0
            elif nap < -0.1 and nap >= -1:
                buy_amount = self.pr_input * 1.5
            elif nap < -1:
                buy_amount = self.pr_input * 2
            else:
                buy_amount = 0

            if buy_amount != 0:
                # 下单
                order_price = df.loc[today, 'price']   # 按当日价格买入
                order_amount = round(buy_amount/order_price)
                acct.order(date=today, securiy_id='005918', amount=order_amount, price=order_price)
                log.info('{0} 买入 {1} '.format(today, buy_amount))

    def after_dayend(self, context):
        # 日终后业务逻辑
        pass

    def end(self):
        # 策略最后的处理
        pass


if __name__ == "__main__":
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180)         # 设置打印宽度(**重要**)
    pd.set_option('display.max_columns', 500)

    # 开始回测
    start_date = '2019-11-01'
    end_date = '2020-03-27'
    strategy = ZFB_HS300Index_Fund()
    strategy.start_date = start_date
    strategy.end_date = end_date
    strategy.set_unverise(FundUnverise(['005918']))    # 定义资产池
    # 策略运行
    strategy.run()
