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
import equan.backtest.backtest_api as model
from equan.backtest.runner import StrategyRunner, StrategyResult


class StockOrderStrategy(model.BaseStrategy):
    """
    测试用 策略

    资源池：600016民生银行
    账户 stock_A，初始资金10000元

    策略：
    1. 20191104:买1手(100股)
    2. 20191105:卖1手(100股)
    3. 20191106:买10股（失败，拒绝）
    4. 20191107:买浦发银行（失败，拒绝）
    5. 20191108:买民生银行，通讯失败(系统错误)
    """

    def __init__(self):
        self.name = '股票下单策略'
        self.start = '20191103'
        # self.end = '20191108'
        self.end = '20191105'
        self.benchmark = 'HS300'
        self.freq = 'd'
        self.refresh_rate = 1

        # 资产池
        self.universe = model.StockUniverse(['600016.SH'])

        # 设定账户
        self.accounts = {
            'stock_A': model.StockAccount('stock_A', capital_base=10000)
        }

    def initialize(self, context):
        print('策略 初始化')

    def handle_data(self, context):
        print('{0} 策略执行'.format(context.today))

        if context.today == '20191104':
            acct = context.get_account('stock_A')
            acct.order('600016.SH', 100, 1)   # 买入
        elif context.today == '20191105':
            acct = context.get_account('stock_A')
            acct.order('600016.SH', 100, -1)   # 卖出
        # elif context.today == '20191106':   # 买10股（失败，拒绝）
        #     acct = context.get_account('stock_A')
        #     acct.order('600016.SH', 10, 1)
        # elif context.today == '20191107':   # 买浦发银行（失败，拒绝）
        #     acct = context.get_account('stock_A')
        #     acct.order('600999.SH', 100, 1)
        # elif context.today == '20191108':   # 买民生银行，通讯失败(系统错误)
        #     acct = context.get_account('stock_A')
        #     acct.order('600016.SH', 10, 1)  # TODO 此处要做特殊处理，形成通讯失败的情况


if __name__ == "__main__":
    # # 策略执行
    # case = StockOrderStrategy()
    # runner = StrategyRunner()
    # runner.back_test_run(case)

    # 生成return
    case = StockOrderStrategy()
    runner = StrategyRunner()
    result = StrategyResult(case)
