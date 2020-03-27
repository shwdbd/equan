#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fund_backtesting_impl.py
@Time    :   2020/03/07 19:31:01
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   回测具体实现类


策略结果体系：
- StrategyResult 策略总结果
    - daily_return  每日收益清单
- Account 分账户
    - daily_return  每日收益清单
    - order_record  订单明细
    - position_record 头寸明细




'''
import pandas as pd
from equan.fund.tl import log


class Unverise:
    """资产库，基类
    所有具体的资产库，都要继承这个类
    """
    _security_symbol_list = []     # 证券id清单

    def get_symbol(self):
        """返回所有的资产id

        Returns:
            [type] -- [description]
        """
        return self._security_symbol_list


class FundUnverise(Unverise):
    """基金资产库
    """

    def __init__(self, list_of_fund):
        super().__init__()
        self._security_symbol_list = list_of_fund


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

        # 总收益率
        self.return_ratio = 0
        # 总交易次数
        self.number_of_transactions = 0
        # 每日收益明细表：
        self._daily_return = StrategyResult._get_empty_return_table()

    def get_daily_return(self):
        # 返回收益表
        return self._daily_return

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
        # TODO 待实现，现金账户存入、支出
        pass

    def order(self, date, securiy_id, amount=0, price=None):
        # 下单
        # 如果price==None，则说明是市价单
        # 新建一个Order对象，加入self.orders清单

        # 只是新建Order对象，不做position的调整：
        order = Order(acct=self, date=date, securiy_id=securiy_id)
        if amount > 0:
            order.direction = Order.DIRECTION_BUY
        elif amount < 0:
            order.direction = Order.DIRECTION_SELL
        order.order_amount = amount       # 下单数量
        order.order_price = price     # 下单价格
        order.status = Order.STATUS_WAIT            # 是否成交？ 等待处理/成交/拒绝

        # 加到列表中
        self.get_orders(date).append(order)

        return True

    def __repr__(self):
        return '<Acct {name} >'.format(name=self.name)


class Order:
    """订单类，纯数据存放类
    """
    DIRECTION_BUY = 1
    DIRECTION_SELL = -1

    STATUS_WAIT = 'WAIT'    # 等待处理
    STATUS_SUCCESS = 'SUCCESS'    # 等待处理
    STATUS_FAILED = 'FAILED'    # 等待处理

    def __init__(self, acct, date, securiy_id):
        self.date = date  # 订单日期
        self.security_id = securiy_id   # 购买资产symbol
        self.direction = 0     # 购买方向，buy/sell
        self.order_amount = 0       # 下单数量
        self.order_price = 0.00     # 下单价格
        self.status = Order.STATUS_WAIT            # 是否成交？ 等待处理/成交/拒绝
        self.turnover_amount = 0    # 成交数量
        self.turnover_price = 0.00  # 成交价格
        self.commission = 0.00      # 佣金
        self.failed_messge = ""     # 订单失败原因

        self.account = acct         # 对账户对象的引用

    def __repr__(self):
        return '<Order {date} {security_id}, {d} ({amount} * {price}) {status} >'.format(date=self.date, security_id=self.security_id, amount=self.order_amount, price=self.order_price, status=self.status, d=self.direction)


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
        return '<Position {date} {security_id}, ({amount} * {today_price}) >'.format(date=self.date, security_id=self.security_id, amount=self.amount, today_price=self.today_price)

    @staticmethod
    def copy(the_position):
        if not the_position:
            return None
        else:
            new_p = Position(the_position.account)
            new_p.date = the_position.date
            new_p.security_id = the_position.security_id
            new_p.amount = the_position.amount
            new_p.today_price = the_position.today_price
            return new_p


class StrategyResult:
    """策略总结果

    是整个回测的总结果
    """

    def __init__(self):
        self.return_rate = 0                        # 总收益率
        self.total_capital_input = 0.00             # 总资金投入
        self.value = 0                              # 期末资产总价值

        self.total_number_of_transactions = 0       # 买交易次数

        # 每日收益率清单
        self._daily_return = StrategyResult._get_empty_return_table()

        # TODO 未来要实现的，计算最大回撤、基准收益率
        # 最大回撤
        # 基准收益率

    @staticmethod
    def _get_empty_return_table():
        # 返回一个空的收益率明细表格
        cols_of_return = ['日期', '总资产', '累计投入资金', '收益率', '交易次数']
        return_table = pd.DataFrame(columns=cols_of_return)
        return_table.set_index('日期', inplace=True)
        return return_table

    def get_return_table(self):
        return self._daily_return

    def append(self, date, dict_data):
        # 添加一天的数据
        record = pd.Series(dict_data, name=date)
        self._daily_return = self._daily_return.append(record)

    def summary(self):
        # 汇总统计:

        # 汇总账户的收益率清单
        self.return_record = self.account.result.copy()     # FIXME 结果要多账户累加
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
