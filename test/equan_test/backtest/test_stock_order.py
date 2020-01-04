#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_stock_order.py
@Time    :   2020/01/01 11:50:51
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   股票账户下单功能测试

'''
import unittest
import equan.backtest.backtest_api as model
from equan.backtest.runner import StrategyRunner
import equan.backtest.constant as CONSTANT


class StockOrderStrategy(model.BaseStrategy):
    """
    测试用 策略

    资源池：600016民生银行
    账户 stock_A，初始资金10000元

    策略：
    1. 20191104:买1手
    2. 20191105:买10股（失败）
    3. 20191106：买浦发银行（失败）
    """

    def __init__(self):
        self.name = '股票下单'
        self.start = '20191103'
        self.end = '20191108'
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


class test_Stock_Order(unittest.TestCase):
    """
    股票账户下单测试

    20191105 买民生100股
    20191106 卖民生100股

    检查：
    - 每日的账户市值
    - 每日每个position、Order

    """

    def test_stock_order(self):
        """
        股票账户按市价（open）下单
        """
        case = StockOrderStrategy()
        runner = StrategyRunner()
        runner.back_test_run(case)

        stock_id = '600016.SH'

        acct = case.get_context().get_account('stock_A')

        # 检查Account:
        self.assertEqual(10001, acct.get_cash())
        self.assertEqual(10001, acct.get_value())

        # 检查 订单 Order
        # 共有两个订单：
        self.assertEqual(2, len(acct.get_orders(state=model.OrderState.FILLED)))
        # 订单1， 第1天买入100股
        order_buy = acct.get_order('20191104-000001')
        self.assertIsNotNone(order_buy)
        self.assertEqual(stock_id, order_buy.symbol)
        self.assertEqual('20191104 000000', order_buy.order_time)
        self.assertEqual(100, order_buy.order_amount)   # 委托数量
        self.assertEqual(100, order_buy.filled_amount)   # 成交数量
        self.assertEqual(6.18, order_buy.order_price)   # 委托价格
        self.assertEqual(CONSTANT.ORDER_DIRECTION_LONG, order_buy.direction)    # 买卖方向
        self.assertEqual('open', order_buy.offset_flag)    # 买卖方向
        # 订单2， 第2天卖出100股
        order_sell = acct.get_order('20191105-000002')
        self.assertIsNotNone(order_sell)
        self.assertEqual(stock_id, order_sell.symbol)
        self.assertEqual('20191105 000000', order_sell.order_time)
        self.assertEqual(100, order_sell.order_amount)   # 委托数量
        self.assertEqual(100, order_sell.filled_amount)   # 成交数量
        self.assertEqual(6.19, order_sell.order_price)   # 委托价格
        self.assertEqual(CONSTANT.ORDER_DIRECTION_SHORT, order_sell.direction)    # 买卖方向
        self.assertEqual('close', order_sell.offset_flag)    # 买卖方向

        # 检查即时Position：
        # 共有两个Position:
        self.assertEqual(2, len(acct.get_positions()))
        # 检查Cash头寸
        p_cash = acct.get_position('CASH')
        self.assertIsNotNone(p_cash)
        cash = 10000-6.18*100+6.19*100
        self.assertEqual(cash, p_cash.amount)    # 数量为0
        self.assertEqual(cash, p_cash.available_amount)
        self.assertEqual(cash, p_cash.value)     # 市值为0
        # 检查股票头寸
        p_600016 = acct.get_position('600016.SH')
        self.assertIsNotNone(p_600016)
        self.assertEqual(0, p_600016.amount)    # 数量为0
        self.assertEqual(0, p_600016.available_amount)
        self.assertEqual(0, p_600016.value)     # 市值为0

        # 检查汇总表
        # 汇总的postion


    # def test_error_unit(self):
    #     """
    #     股票账户下单不按手为单位 [反例]
    #     """
    #     pass
    #
    # def test_error_universe(self):
    #     """
    #     股票账户下单，股票id不在资产池中 [反例]
    #     """
    #     pass
    #
    # def test_cant_get_data(self):
    #     """
    #     股票账户获取股价数据失败 [反例]
    #     """
    #     pass
