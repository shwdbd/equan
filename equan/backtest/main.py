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
from equan.backtest.tl import log


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

        log.debug('handle_data {0}'.format(context.today))

        # 策略：40%资金买民生银行，60%资金买五粮液


class OrderTestCase(api.StrategyCase):
    start = '20191104'
    end = '20191105'
    benchmark = 'HS300'
    freq = 'd'
    refresh_rate = 1

    # 资产池
    universe = api.StockUniverse(['600016.SH', '600320.SH'])

    # 设定账户
    accounts = {
        'my_account': api.StockAccount('my_account', capital_base=10000)
    }

    def initialize(self, context):
        print('策略 初始化')

    def handle_data(self, context):
        account = context.get_account('my_account')


if __name__ == "__main__":

    # fnf = runner.StrategyRunner
    # fnf.back_test_run(MyCase())


    # 账户下单
    case = OrderTestCase()
    context = api.Context(case.accounts, case.universe)
    # 第一天
    context.set_date('20191105')
    # 账户下单
    acct = context.get_account('my_account')
    order1 = acct.order(symbol='600016.SH', amount=300, order_type=api.Order.ORDER_LONG)
    order2 = acct.order(symbol='600016.SH', amount=100, order_type=api.Order.ORDER_SHORT)
    print(order1)
    # 交易撮合
    context.make_deal()
    print('cash = {0}'.format(context.get_account('my_account').get_cash()))
    print(context.get_account('my_account').get_position('600016.SH'))


    # 第2天
    context.set_date('20191118')
    acct = context.get_account('my_account')
    order3 = acct.order(symbol='600016.SH', amount=100, order_type=api.Order.ORDER_SHORT)
    # 交易撮合
    context.make_deal()
    print('cash = {0}'.format(context.get_account('my_account').get_cash()))
    print(context.get_account('my_account').get_position('600016.SH'))

    print(acct.get_value())
    print(acct.get_order('000003'))

    # # 头寸变动
    # # amount (price) value_change   |cost     value   profit
    # # 100    1       100             1*100    100     0
    # # 100    2       200             300      400     400-300=100
    # # -100   1                       200      100     -100
    # p = api.Position('600016.SH')
    # print(p)
    # p.change(direct=1, the_amount=100, the_price=1)
    # print(p)
    # p.change(direct=1, the_amount=100, the_price=2)
    # print(p)
    # p.change(direct=-1, the_amount=100, the_price=1)
    # print(p)
