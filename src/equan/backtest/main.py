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
from equan.backtest.runner import StrategyRunner


class OrderTestCase(model.BaseStrategy):
    """
    测试用 策略
    """

    def __init__(self):
        self.name = 'MY策略'
        self.start = '20191104'
        self.end = '20191105'
        self.benchmark = 'HS300'
        self.freq = 'd'
        self.refresh_rate = 1

        # 资产池
        self.universe = model.StockUniverse(['600016.SH', '600320.SH'])

        # 设定账户
        self.accounts = {
            'my_account': model.StockAccount('my_account', capital_base=10000)
        }

    def initialize(self, context):
        print('策略 初始化')

    def handle_data(self, context):
        # account = context.get_account('my_account')
        print('{0} 策略执行'.format(context.today))


if __name__ == "__main__":
    case = OrderTestCase()
    runner = StrategyRunner()
    runner.back_test_run(case)

    # 检查各阶段函数是否调用
    # 检查各模块的参数是否计算正确，如today、account等
