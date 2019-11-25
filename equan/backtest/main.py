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


class MyCase(api.StrategyCase):
    start = '20190101'
    end = '20190107'
    benchmark = 'HS300'
    freq = 'd'
    refresh_rate = 1

    # 资产池
    universe = api.StockUniverse(['600016', '600320'])

    # 设定账户
    accounts = {
        'my_account': api.StockAccount('my_account', capital_base=10000000)
    }

    def initialize(self, context):
        print('策略 初始化')
        pass

    def handle_data(self, context):
        # account = context.get_account('my_account')
        # universe = context.get_universe()

        # print('handle_data')
        pass
        # 策略：40%资金买民生银行，60%资金买五粮液


if __name__ == "__main__":

    fnf = runner.StrategyRunner
    fnf.back_test_run(MyCase())

    # # context 初始化
    # day = '20190105'
    # context = api.Context(day, accounts={})
    # print(type(context.now))
    # print(context.now)
    # print(type(context.previous_date))
    # print(context.previous_date)

    # # str_now = "20171123"
    # # str_now += ' 000000'
    # # dt_now = datetime.datetime.strptime(str_now, "%Y%m%d %H%M%S")
    # # print(type(dt_now))
    # # print(dt_now)
