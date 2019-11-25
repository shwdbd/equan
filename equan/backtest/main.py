#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2019/11/25 13:28:20
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   代码执行
'''
import equan.backtest.backtest_api as api
import equan.backtest.runner as runner
import pandas as pd
from equan.backtest.tl import *


class MyCase(api.StrategyCase):
    start = '20190101'
    end = '20190201'
    benchmark = 'HS300'
    freq = 'd'
    refresh_rate = 1

    # 设定账户
    accounts = {
        'my_account': api.StockAccount('my_account', capital_base=10000000)
    }

    def initialize(self, context):
        print('策略 初始化')
        pass

    def handle_data(self, context):
        account = context.get_account('my_account')
        universe = context.get_universe()

        print('handle_data')
        # 策略：40%资金买民生银行，60%资金买五粮液


if __name__ == "__main__":
   
    # fnf = runner.StrategyRunner
    # fnf.back_test_run(MyCase())

    # print( pd.date_range(start='20180101', end='20180131') )

    log.info('rizhi ')

