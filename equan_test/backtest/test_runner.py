#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_runner.py
@Time    :   2019/12/03 14:25:08
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试 回测运行框架
'''
import equan.backtest.backtest_api as api
import equan.backtest.runner as runner
import unittest


class SimpleCase(api.StrategyCase):
    start = '20190101'
    end = '20190103'
    benchmark = 'HS300'
    freq = 'd'
    refresh_rate = 1

    def __init__(self):
        self.count_of_init_func = 0         # init函数运行次数
        self.count_of_handle_data_func = 0  # handle_data函数运行次数
        self.seq_of_func = []               # 函数运行的序列

    # 资产池
    universe = api.StockUniverse(['600016', '600320'])

    # 设定账户
    accounts = {
        'my_account': api.StockAccount('my_account', capital_base=1000)
    }

    def initialize(self, context):
        self.count_of_init_func += 1
        self.seq_of_func.append('initialize')

    def handle_data(self, context):
        # account = context.get_account('my_account')
        # universe = context.get_universe()

        self.count_of_handle_data_func += 1
        self.seq_of_func.append('handle_data_' + context.today)


class Test_BackTestRunner(unittest.TestCase):

    def test_run_simple_case(self):
        """测试运行最简单框架
        """
        the_case = SimpleCase()
        fnf = runner.StrategyRunner
        fnf.back_test_run(the_case)

        # 检查:
        self.assertIsNotNone(the_case)
        self.assertEqual(1, the_case.count_of_init_func)
        self.assertEqual(2, the_case.count_of_handle_data_func)
        func_list = ['initialize', 'handle_data_20190102',
                     'handle_data_20190103']
        self.assertListEqual(func_list, the_case.seq_of_func)
        # 检查case属性：
        self.assertEqual('20190101', the_case.start)
        # 检查context
        context = the_case.get_context()
        self.assertIsNotNone(context)


if __name__ == "__main__":
    the_case = SimpleCase()
    fnf = runner.StrategyRunner
    fnf.back_test_run(the_case)

    print(the_case.seq_of_func)
