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


class Account:

    def __init__(self, name, initial_capital=0):
        self.name = name                    # 账户名称
        self.balance = initial_capital      # 账户余额

        # 调仓记录清单
        self.order_record = {}    # '2019-03-01: [order1, order2]'
        # 持仓记录清单，默认有一个cash的账户
        self.position_record = {}       # '2019-03-01: [position1, position2]'
        cash_postion = Position(acct=self)
        cash_postion.date = "0000-00-00"
        cash_postion.security_id = "cash"
        cash_postion.amount = self.balance
        cash_postion.today_price = 1
        cash_postion.value = self.balance
        self.position_record['0000-00-00'] = [cash_postion]

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
    DIRECTION_BUY = 'BUY'
    DIRECTION_SELL = 'SELL'

    STATUS_WAIT = 'WAIT'    # 等待处理
    STATUS_SUCCESS = 'SUCCESS'    # 等待处理
    STATUS_FAILED = 'FAILED'    # 等待处理

    def __init__(self, acct, securiy_id):
        self.date = ""  # 订单日期
        self.security_id = securiy_id   # 购买资产symbol
        self.direction = Order.DIRECTION_BUY     # 购买方向，buy/sell
        self.order_amount = 0       # 下单数量
        self.order_price = 0.00     # 下单价格
        self.status = ""            # 是否成交？ 等待处理/成交/拒绝
        self.turnover_amount = 0    # 成交数量
        self.turnover_price = 0.00  # 成交价格
        self.commission = 0.00      # 佣金

        self.account = acct         # 对账户对象的引用

    def __repr__(self):
        return '<Order {date} {security_id}, ({amount} * {price}) >'.format(date=self.date, security_id=self.security_id, amount=self.order_amount, price=self.order_price)


class Position:
    # 仓位

    def __init__(self, acct):
        self.date = ""  # 订单日期
        self.security_id = ""   # 购买资产symbol

        self.amount = 0         # 持仓数量
        self.today_price = 0    # 今日单价
        self.value = 0          # 今日价值

        self.account = acct         # 对账户对象的引用

    def __repr__(self):
        return '<Position {security_id}, ({amount} * {today_price}) >'.format(security_id=self.security_id, amount=self.amount, today_price=self.today_price)


class StrategyResult:
    """策略结果
    """

    def __init__(self):
        self.return_rate = 0        # 收益率
        self.bm_return_rate = 0     # 基准收益率
        self.total_capital_input = 0.00     # 总资金投入
        self.total_number_of_transactions = 0     # 买交易次数
        # TODO 最大回撤

        # TODO 调仓记录清单
        # 按日期，每笔order明细
        self.orders = {}    # '2019-03-01: [order1, order2]'

        # TODO 持仓记录清单
        # 按日期，每个资产的持有明细
        self.position_record = {}       # '2019-03-01: [position1, position2]'

    