#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_simple_strategy_runner.py
@Time    :   2019/12/31 23:58:30
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试最简单的策略，检查各函数是否会按需求逐一运行

测试最简单的策略执行情况，重点在测试Runner情况，非具体的下单等操作
- 无下单动作

检查的内容：
- context
- account
- account.position
- account.order



'''
import unittest
import equan.backtest.backtest_api as model
from equan.backtest.runner import StrategyRunner


class OrderTestCase(model.BaseStrategy):
    """
    测试用 策略
    """

    # 单元测试用探针
    result = {
        'initialize': None,
        'handle_data': {},
    }

    def __init__(self):
        self.name = 'MY策略'
        self.start = '20191103'
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
        self.result['initialize'] = {
            'strategy.name': self.name,
            'strategy.start': self.start,
            'strategy.end': self.end,
            'strategy.benchmark': self.benchmark,
        }
        print('策略 初始化')

    def handle_data(self, context):
        # account = context.get_account('my_account')
        handle_data = {
            'context.today': context.today,
            'context.previous_date': context.previous_date,
        }
        self.result['handle_data'][context.today] = handle_data
        print('{0} 策略执行'.format(context.today))


class Test_SimpleStrategyRun(unittest.TestCase):

    def test_strategy_run(self):
        """
        策略运行

        使用result探针检查其运行结果和顺序
        """

        case = OrderTestCase()
        runner = StrategyRunner()
        runner.back_test_run(case)

        # 初始化操作：
        self.assertEquals('MY策略', case.result['initialize']['strategy.name'])
        self.assertEquals('20191103', case.result['initialize']['strategy.start'])
        self.assertEquals('20191105', case.result['initialize']['strategy.end'])
        self.assertEquals('HS300', case.result['initialize']['strategy.benchmark'])

        # 检查资产池
        self.assertIsInstance(case.universe, model.Universe)
        self.assertListEqual(['600016.SH', '600320.SH'], case.universe.get_symbols(''))

        # 每日执行：
        self.assertEqual(2, len(case.result['handle_data']))  # 总执行2个交易日
        # 自然日，非交易日，不能被调用：
        self.assertTrue('20191103' not in case.result['handle_data'].keys())
        # 第1天：(检查是按交易日执行，非自然日)
        d1 = case.result['handle_data']['20191104']
        self.assertEqual('20191104', d1['context.today'])
        self.assertEqual('20191101', d1['context.previous_date'])   # 前一交易日
        # 第2天：
        d2 = case.result['handle_data']['20191105']
        self.assertEqual('20191105', d2['context.today'])
        self.assertEqual('20191104', d2['context.previous_date'])

        # Account检查
        acct = case.get_context().get_account('my_account')
        self.assertIsNotNone(acct)
        self.assertEqual(10000, acct.get_value())   # 市值应等于初始金额
        self.assertEqual(10000, acct.get_cash())
        # 检查头寸和订单
        self.assertEqual(1, len(acct.get_positions()))  # 仅现金头寸
        self.assertEqual('CASH', acct.get_position('CASH').symbol)
        self.assertEqual(0, len(acct.get_orders()))     # 无订单

        # TODO 检查历史头寸
        
        # TODO 检查策略结果的输出
        