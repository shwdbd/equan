#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_order.py
@Time    :   2019/11/27 14:22:19
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   针对下单工作的单元测试
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

    # 资产池
    universe = api.StockUniverse(['600016.SH', '600320.SH'])

    # 设定账户
    accounts = {
        'my_account': api.StockAccount('my_account', capital_base=10000)
    }

    def initialize(self, context):
        print('策略 初始化')

    def handle_data(self, context):
        # account = context.get_account('my_account')
        pass


class Test_StockOrder(unittest.TestCase):
    """
    测试 股票下单功能
    """

    case = None
    context = None

    def setUp(self):
        self.case = OrderTestCase()
        self.context = api.Context(self.case.accounts, self.case.universe)
        self.context.set_date('20191105')

    def tearDown(self):
        self.case = None
        self.context = None

    def test_order_by_amount(self):
        """
        测试 股票账户下单股票的情况
        """
        acct = self.context.get_account('my_account')
        order1 = acct.order(symbol='600016.SH', amount=300,
                            order_type=api.Order.ORDER_LONG)
        order2 = acct.order(symbol='600016.SH', amount=100,
                            order_type=api.Order.ORDER_SHORT)
        # order3 = acct.order(symbol='600099.SH', amount=100, order_type=api.Order.ORDER_SHORT)

        # 检查：
        self.assertEqual(2, len(acct.get_orders()))
        # 订单1：买单
        self.assertIsNotNone(order1)
        self.assertEqual('000001', order1.order_id)
        self.assertIsNotNone(order1.get_account())
        self.assertEqual(self.context.now, order1.order_time)
        self.assertEqual(6.2, order1.order_price)   # 价格
        self.assertEqual(300, order1.order_amount)  # 订单数量
        self.assertEqual(0, order1.filled_amount)
        self.assertEqual(api.OrderState.OPEN, order1.state)     # 状态
        self.assertEqual(1, order1.direction)
        self.assertEqual("", order1.state_message)
        self.assertEqual("open", order1.offset_flag)
        # 订单2：卖单
        self.assertIsNotNone(order2)
        self.assertEqual('000002', order2.order_id)
        self.assertEqual(6.2, order2.order_price)   # 价格
        self.assertEqual(100, order2.order_amount)  # 订单数量
        self.assertEqual(0, order2.filled_amount)
        self.assertEqual(api.OrderState.OPEN, order2.state)     # 状态
        self.assertEqual(-1, order2.direction)
        self.assertEqual("", order2.state_message)
        self.assertEqual("open", order2.offset_flag)

    def test_order_by_amount_with_error_symbol(self):
        """
        测试 股票下单，股票id不在资产池内的情况
        """
        acct = self.context.get_account('my_account')
        order = acct.order(symbol='600099.SH', amount=100,
                           order_type=api.Order.ORDER_SHORT)

        # 检查
        self.assertIsNotNone(order)
        self.assertEqual('000003', order.order_id)  # TODO 此处要改进
        self.assertEqual(0, order.order_price)   # 价格
        self.assertEqual(0, order.order_amount)  # 订单数量
        self.assertEqual(api.OrderState.REJECTED, order.state)     # 状态
        self.assertEqual(0, order.direction)
        self.assertEqual("股票600099.SH不在可交易的资产池中，不能下单", order.state_message)

    def test_order_by_amount_with_wrong_amount(self):
        """
        测试 股票下单，下单数量不是按“手”为单位的情况
        """
        acct = self.context.get_account('my_account')
        order = acct.order(symbol='600016.SH', amount=123,
                           order_type=api.Order.ORDER_SHORT)
        # 检查
        self.assertIsNotNone(order)
        self.assertEqual(api.OrderState.REJECTED, order.state)     # 状态
        self.assertEqual("股票单交易数量必须以100为单位(amount=123)", order.state_message)



