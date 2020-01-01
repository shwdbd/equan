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

        if context.today == '20191105':
            acct = context.get_account('stock_A')
            acct.order('600016.SH', 100, 'close')   # 下单
        

class test_Stock_Order(unittest.TestCase):
    """
    股票账户下单测试
    """

    def test_stock_order(self):
        """
        股票账户按市价下单
        """
        pass

    def test_error_unit(self):
        """
        股票账户下单不按手为单位 [反例]
        """
        pass    

    def test_error_universe(self):
        """
        股票账户下单，股票id不在资产池中 [反例]
        """
        pass    

    def test_cant_get_data(self):
        """
        股票账户获取股价数据失败 [反例]
        """
        pass   
