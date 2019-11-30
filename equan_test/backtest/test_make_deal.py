#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_make_deal.py
@Time    :   2019/11/29 23:56:41
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   交易撮合功能测试
'''
import unittest
# import equan.backtest.biz_tools as bt
import equan.backtest.backtest_api as api
# import equan.backtest.runner as runner
# from equan.backtest.tl import log


class OrderTestCase(api.StrategyCase):
    """测试用 策略
    """

    start = '20191104'
    end = '20191105'
    benchmark = 'HS300'
    freq = 'd'
    refresh_rate = 1

    universe = None
    accounts = None

    def __init__(self):
        # 资产池
        self.universe = api.StockUniverse(['600016.SH', '600320.SH'])

        # 设定账户
        self.accounts = {
            'my_account': api.StockAccount('my_account', capital_base=10000)
        }

    def initialize(self, context):
        print('策略 初始化')

    def handle_data(self, context):
        # account = context.get_account('my_account')
        pass


class Test_Make_Deal(unittest.TestCase):
    """交易撮合功能测试
    """

    case = None
    context = None

    def setUp(self):
        self.case = None
        self.context = None
        self.case = OrderTestCase()
        self.context = api.Context(self.case.accounts, self.case.universe)
        self.context.set_date('20191105')   # 当日股价：6.2

    def tearDown(self):
        self.case = None
        self.context = None

    def test_make_deal(self):
        """
        测试 股票账户下单股票的情况
        """
        # 第一天
        self.context.set_date('20191105')
        # 账户下单
        acct = self.context.get_account('my_account')
        acct.order(symbol='600016.SH', amount=300,
                   order_type=api.Order.ORDER_LONG)
        acct.order(symbol='600016.SH', amount=100,
                   order_type=api.Order.ORDER_SHORT)
        # 交易撮合
        self.context.make_deal()

        # 检查第一天撮合后情况
        # 各order的情况
        order1 = acct.get_order('000001')
        self.assertEqual(api.OrderState.FILLED, order1.state)
        self.assertEqual(300, order1.filled_amount)
        order2 = acct.get_order('000002')
        self.assertEqual(api.OrderState.FILLED, order2.state)
        self.assertEqual(100, order2.filled_amount)
        # 各postion情况
        p_600016 = acct.get_position('600016.SH')
        self.assertIsNotNone(p_600016)
        self.assertEqual(0, p_600016.profit)
        self.assertEqual(1240.0, p_600016.cost)
        # acct现金账户:
        self.assertEqual(acct.capital_base-(6.2*200), acct.get_cash())
        # acct的总市价
        self.assertEqual(acct.capital_base, acct.get_value())

        # 第2天， 6.11元
        self.context.set_date('20191118')
        acct = self.context.get_account('my_account')
        acct.order(symbol='600016.SH', amount=100,
                   order_type=api.Order.ORDER_SHORT)
        # 交易撮合
        self.context.make_deal()

        # 检查：
        # 各order的情况
        order3 = acct.get_order('000003')
        self.assertEqual(api.OrderState.FILLED, order3.state)
        self.assertEqual(100, order3.filled_amount)
        # 各postion情况
        p_600016 = acct.get_position('600016.SH')
        self.assertIsNotNone(p_600016)
        self.assertEqual(-18.0, p_600016.profit)
        self.assertEqual(629.0, p_600016.cost)
        # acct现金账户:
        self.assertEqual(9371, acct.get_cash())
        # acct的总市价
        self.assertEqual(9982.0, acct.get_value())

    def test_no_cash(self):

        # TODO 测试，买入钱不够，卖出股票数不够的情况
        # 第一天
        self.context.set_date('20191105')
        # 账户下单
        acct = self.context.get_account('my_account')
        order = acct.order(symbol='600016.SH', amount=5000000,
                           order_type=api.Order.ORDER_LONG)
        # 交易撮合
        self.context.make_deal()

        # 检查第一天撮合后情况
        # 各order的情况
        # order1 = acct.get_order('000004')
        self.assertEqual(api.OrderState.CANCELED, order.state)
        self.assertEqual(0, order.filled_amount)
        self.assertEqual('现金不足', order.state_message[:4])
        # 各postion情况
        p_600016 = acct.get_position('600016.SH')
        self.assertIsNotNone(p_600016)
        self.assertEqual(0, p_600016.profit)
        self.assertEqual(0, p_600016.cost)
        self.assertEqual(0, p_600016.amount)
        # acct现金账户:
        self.assertEqual(acct.capital_base, acct.get_cash())
        # acct的总市价
        self.assertEqual(acct.capital_base, acct.get_value())

    def test_no_position(self):
        # TODO 测试，没有足够股票卖出的情况
        pass
