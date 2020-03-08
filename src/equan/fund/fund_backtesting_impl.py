#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fund_backtesting_impl.py
@Time    :   2020/03/07 19:31:01
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   回测具体实现类
'''
import pandas as pd
from equan.fund.tl import log


class Account:
    """账户类
    """

    CASH_SEC_ID = 'cash'
    CASH_DAY0 = "0000-00-00"

    def __init__(self, name, initial_capital=0):
        self.name = name                    # 账户名称
        self.initial_capital = initial_capital      # 账户初始资金

        # 调仓记录清单
        self.order_record = {}    # '2019-03-01: [order1, order2]'
        # 持仓记录清单，默认有一个cash的账户
        self.position_record = {}       # '2019-03-01: [position1, position2]'
        cash_postion = Position(acct=self)
        cash_postion.date = Account.CASH_DAY0
        cash_postion.security_id = Account.CASH_SEC_ID
        cash_postion.amount = self.initial_capital
        cash_postion.today_price = 1
        self.position_record['0000-00-00'] = [cash_postion]

        # 统计结果的数值
        cols_of_result = ['date', '总资产', '累计投入资金', '收益率', '交易次数']
        self.result = pd.DataFrame(columns=cols_of_result)
        self.result.set_index('date', inplace=True)


    def get_orders(self, date):
        try:
            return self.order_record[date]
        except KeyError:
            self.order_record[date] = []
            return self.order_record[date]

    def get_position(self, date):
        try:
            return self.position_record[date]
        except KeyError:
            self.position_record[date] = []
            return self.position_record[date]

    def get_position_by_id(self, date, sec_id):
        try:
            for p in self.position_record[date]:
                if p.security_id == sec_id:
                    return p
        except KeyError:
            return None

    def cash_change(self, date, cash):
        # 现金账户资金变动，存钱、取钱
        # 其实是一个特殊的order，必然成功的order（取钱会出现不成功）
        # TODO 待实现
        pass

    def order(self, date, securiy_id, amount=0, price=None):
        # 下单
        # 如果price==None，则说明是市价单
        # 新建一个Order对象，加入self.orders清单
        # TODO 待实现

        # 只是新建Order对象，不做position的调整：
        order = Order(acct=self, securiy_id=securiy_id)
        if amount > 0:
            self.direction = Order.DIRECTION_BUY
        else:
            self.direction = Order.DIRECTION_SELL
        order.order_amount = amount       # 下单数量
        order.order_price = price     # 下单价格
        order.status = Order.STATUS_WAIT            # 是否成交？ 等待处理/成交/拒绝

        # 加到列表中
        self.get_orders(date).append(order)

        return True
    
    def marchmaking(self, date):
        # 日终，撮合交易
        # FIXME 此处要改到日终处理里去
        # 首先处理 现金postion，然后再处理资产position
        # 逐个order进行处理
        pass

    def __repr__(self):
        return '<Acct {name}, b={balance} >'.format(name=self.name, balance=self.balance)


class Order:
    """订单类，纯数据存放类
    """
    DIRECTION_BUY = 1
    DIRECTION_SELL = -1

    STATUS_WAIT = 'WAIT'    # 等待处理
    STATUS_SUCCESS = 'SUCCESS'    # 等待处理
    STATUS_FAILED = 'FAILED'    # 等待处理

    def __init__(self, acct, securiy_id):
        self.date = ""  # 订单日期
        self.security_id = securiy_id   # 购买资产symbol
        self.direction = Order.DIRECTION_BUY     # 购买方向，buy/sell
        self.order_amount = 0       # 下单数量
        self.order_price = 0.00     # 下单价格
        self.status = Order.STATUS_WAIT            # 是否成交？ 等待处理/成交/拒绝
        self.turnover_amount = 0    # 成交数量
        self.turnover_price = 0.00  # 成交价格
        self.commission = 0.00      # 佣金

        self.account = acct         # 对账户对象的引用

    def __repr__(self):
        return '<Order {date} {security_id}, ({amount} * {price}) {status} >'.format(date=self.date, security_id=self.security_id, amount=self.order_amount, price=self.order_price, status=self.status)


class Position:
    # 仓位

    def __init__(self, acct):
        self.date = ""  # 订单日期
        self.security_id = ""   # 购买资产symbol

        self.amount = 0         # 持仓数量
        self.today_price = 0    # 今日单价

        self.account = acct         # 对账户对象的引用

    def get_value(self):
        return self.amount*self.today_price

    def __repr__(self):
        return '<Position {security_id}, ({amount} * {today_price}) >'.format(security_id=self.security_id, amount=self.amount, today_price=self.today_price)


class StrategyResult:
    """策略总结果

    # FIXME 策略的计算应该放到此处

    """

    def __init__(self, acct):
        self.account = acct

        self.return_rate = 0        # 总收益率
        self.total_capital_input = 0.00     # 总资金投入
        self.total_number_of_transactions = 0     # 买交易次数

        # 每日收益率清单
        cols_of_return = ['date', '总资产', '累计投入资金', '收益率', '交易次数']
        self.return_record = pd.DataFrame(columns=cols_of_return)
        self.return_record.set_index('date', inplace=True)

        # TODO 未来要实现的：
        # 最大回撤
        # 基准收益率

    def summary(self):
        # 汇总统计:

        # 汇总账户的收益率清单
        self.return_record = self.account.result.copy()
        # print(self.return_record)

        # 买交易次数
        self.total_number_of_transactions = self.return_record['交易次数'].sum()
        # print(self.total_number_of_transactions)

        # 总收益率、总资金投入
        self.return_rate = round(float(self.return_record.tail(1)['收益率']), 2)
        # print(self.return_rate)
        self.total_capital_input = round(float(self.return_record.tail(1)['累计投入资金']), 2)
        # print(self.total_capital_input)

        log.info('总收益率 = {0} %'.format(self.return_rate))
        log.info('总投入资金 = {0}'.format(self.total_capital_input))
        log.info('交易次数 = {0}'.format(self.total_number_of_transactions))
