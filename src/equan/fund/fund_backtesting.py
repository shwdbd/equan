#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fund_backtesting.py
@Time    :   2020/03/07 19:23:51
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基金回测框架

v 0.0.1 版本说明：
- 只支持按日（交易日）回测；
- 只支持单一账户，但提供get_account的假函数；
- 数据只支持csv文件导入；
- 没有结果导出，只有日志输出简单结果
- 只支持基金库，可有多个基金，基金编码对应数据文件（csv）文件；


# TODO 数据集合，需要提供前置天数，默认30天


'''
import pandas as pd
import equan.fund.tl as tl
from equan.fund.fund_backtesting_impl import Order, Account, Position, StrategyResult
from equan.fund.data_api import DataAPI

log = tl.get_logger()


class FundBackTester:

    def __init__(self):
        # 全局参数：
        self.start_date = ""
        self.end_date = ""
        self._unverise = None   # 资产池
        # benchmark
        self.account = None
        self.commission = 0.001     # 佣金，千分之一

        # 内部参数：
        self.__version__ = "0.0.1"

        # 初始化上下文
        self._context = Context()

        # 测试结果
        self.result = StrategyResult()

    def fm_log(self, msg):
        # 框架的日志
        log.info('【回测】' + msg)

    def get_unverise(self):
        return self._unverise

    def set_unverise(self, unverise):
        self._unverise = unverise

    def get_context(self):
        return self._context

    def run(self):
        self.fm_log('回测启动')
        # 策略运行
        self._initialize_by_framework()   # 准备数据等

        # self.fm_log('调用用户 initialize() ')
        self.initialize()   # 调用用户的策略初始化
        # self.fm_log('用户 initialize() 结束')

        number_of_day = 0
        previous_day = None   # 前一日
        for date in DataAPI.get_cal(self.start_date, self.end_date):
            # 切日操作：
            self.get_context().today = date
            self.get_context().previous_day = previous_day

            # self.fm_log('策略 {0} 执行 ... '.format(date))
            self.date_handle(self.get_context())   # 调用用户的策略初始化

            # 日终处理：
            # self.fm_log('日终处理 {0} ... '.format(date))
            self._dayend_handle(date)   # 调用用户的策略初始化

            # self.fm_log('---- {0} OVER -------'.format(date))
            previous_day = date
            number_of_day += 1
        self.fm_log('策略运行完毕 【共{0}个交易日】'.format(number_of_day))

        # 计算策略总体收益
        self._calculate_strategy_earnings(date)
        # 结果要输出
        self.result_export_to_console(self.result)

    def result_export_to_console(self, result):
        self.fm_log('='*20)
        self.fm_log('策略总收益 ：{0} %'.format(result.return_rate))
        self.fm_log('交易次数 ：{0} '.format(round(result.total_number_of_transactions)))
        self.fm_log('期初投入资金 ：{0}'.format(result.total_capital_input))
        self.fm_log('期末收益资金 ：{0}'.format(result.value))
        # self.fm_log('每日收益表 : ')
        # for acct in self.get_context().get_accounts():
        #     self.fm_log('账户 {0} ：'.format(acct.name))
        #     self.fm_log('{0}'.format(acct.get_daily_return()))
        self.fm_log('='*20)

    def _initialize_by_framework(self):
        # 策略执行前的准备工作

        # 1. 准备每个资产的历史数据
        # 按universe逐个准备数据
        for sec_id in self.get_unverise().get_symbol():
            self.get_context().data[sec_id] = self._load_data(sec_id)
            self.fm_log('准备{0}数据'.format(sec_id))
        self.fm_log('策略运行前准备完毕')

    def _load_data(self, symbol):
        # 取得基金日线数据
        return DataAPI.load_fund_daily(symbol, self.start_date, self.end_date)

    def initialize(self):
        # 用户初始化
        pass

    def date_handle(self, context):
        # 需要具体实现继承
        pass

    def _dayend_handle(self, date):
        # 日终处理
        # 每日日终后，主要做交易撮合
        # 计算每日后account的 资产总值
        for account in self.get_context().get_accounts():
            # 初始化当日头寸
            self._init_daily_position(account, date)

            # 订单撮合
            for order in account.get_orders(date):
                self._matchmaking_order(order, date, account)
            # end of order

            # 计算账户当日收益
            self._calculate_account_earnings(date, account)

    def _calculate_strategy_earnings(self, date):
        """计算策略总体收益
        """
        self.result = StrategyResult()

        # 计算每个账户每天的收益
        for account in self.get_context().get_accounts():
            account._daily_return['昨日总资产'] = account._daily_return['总资产'].shift(1)
            account._daily_return['收益率'] = (account._daily_return['总资产']/account._daily_return['昨日总资产'] - 1)*100
            # 总收益率
            account.return_ratio = round(account._daily_return['收益率'].sum(), 2)
            # 总交易次数
            account.number_of_transactions = account._daily_return['交易次数'].sum()

            # 策略累计
            self.result.return_rate += account.return_ratio
            self.result.total_number_of_transactions += account.number_of_transactions
            self.result.total_capital_input += round(float(account._daily_return.tail(1)['累计投入资金']), 2)
            self.result.value += round(float(account._daily_return.tail(1)['总资产']), 2)

        # 计算策略总参数：
        self.result.return_rate = self.result.return_rate / len(self.get_context().get_accounts())    # 算数平均

    def _calculate_account_earnings(self, date, account):
        """计算账户日终收益

        在 account.cols_of_return 中添加一行
        计算：'日期', '总资产', '累计投入资金', '收益率', '交易次数'

        Arguments:
            date {[type]} -- [description]
            account {[type]} -- [description]
        """
        # 计算 总资产
        total_value = 0
        for p in account.get_position(date):
            total_value += p.get_value()

        # 累计投入资金，假设只用原始init_balance投资
        accumulated_investment = account.initial_capital

        # 累计收益率
        # account._daily_return['昨日总资产'] = account._daily_return['总资产'].shift(1)
        # return_ratio = round(((total_value/accumulated_investment)-1)*100, 2)
        return_ratio = 0

        # 交易次数，仅成功交易
        number_of_order = 0
        for order in account.get_orders(date):
            if order.status == Order.STATUS_SUCCESS:
                number_of_order += 1

        # 汇总加入
        s_result = pd.Series(data={'总资产': total_value, '累计投入资金': accumulated_investment, '收益率': return_ratio, '交易次数': number_of_order}, name=date)
        account._daily_return = account.get_daily_return().append(s_result)

    def _matchmaking_order(self, order, date, account):
        # 订单撮合

        # 按order逐一处理：

        # 1. 明确价格
        # 2. 双边，调整position
        # 3. 加入佣金的计算
        # 4. 更新order的成交值和状态
        # FEATURE 目前仅支持市价单

        # 计算拟成交价格
        # 如果是市价单，则按前一日市场价计算
        if order.order_price is None:
            # 按市价执行，按上一日价格执行
            if self.get_context().previous_day is None:
                log.error('取上日为空，则此order无法按市场定价，则此order被拒绝')
                order.status = Order.STATUS_FAILED
                return
            else:
                closing_price = self.get_context().data[order.security_id].loc[self.get_context().previous_day, 'price']  # 市价
        else:
            # TODO 要修正，此次为非市价单，默认按订单价格成交
            closing_price = order.order_price

        # 拟交易额
        volume_of_amount = order.direction * (order.order_amount * closing_price)
        cash_p = account.get_position_by_id(date, Account.CASH_SEC_ID)
        fund_p = account.get_position_by_id(date, order.security_id)
        if not cash_p or not fund_p:
            log.error('头寸错误，导致订单撮合失败，请检查 {order}'.format(order=order))
        else:
            if order.direction == Order.DIRECTION_BUY:
                if cash_p.get_value() < volume_of_amount:
                    log.error('现金余额不足，无法买入，交易失败')
                    order.turnover_amount = 0
                    order.turnover_price = None
                    order.status = Order.STATUS_FAILED
                    order.failed_messge = '现金账户余额不足'
                else:
                    # 买入
                    order.order_price = closing_price
                    cash_p.amount += -1 * volume_of_amount
                    fund_p.amount += order.order_amount
                    fund_p.today_price = order.order_price   # 按订单价格计算
                    order.turnover_amount = order.order_amount
                    order.turnover_price = order.order_price
                    order.status = Order.STATUS_SUCCESS
            elif order.direction == Order.DIRECTION_SELL:
                if fund_p.amount < abs(order.order_amount):
                    log.error('资产{0}份数不足，无法卖出，交易失败'.format(order.security_id))
                    order.turnover_amount = 0
                    order.turnover_price = None
                    order.status = Order.STATUS_FAILED
                    order.failed_messge = '持有份数不足'
                else:
                    # 卖出
                    order.order_price = closing_price
                    cash_p.amount += 1 * volume_of_amount
                    fund_p.amount -= order.order_amount
                    fund_p.today_price = order.order_price   # 按订单价格计算
                    order.turnover_amount = order.order_amount
                    order.turnover_price = order.order_price
                    order.status = Order.STATUS_SUCCESS
            else:
                log.error('非法的订单方向，导致订单撮合失败，请检查 {d} {order}'.format(d=order.direction, order=order))

    def _init_daily_position(self, account, date):
        # 初始化当日头寸
        if len(account.position_record) == 1:
            # 第1日情况：
            the_cash_position = account.get_position(Account.CASH_DAY0)[0]
            the_cash_position.date = date
            account.get_position(date).append(the_cash_position)    # 现金账户
            # 资产账户:
            for sec_id in self.get_unverise().get_symbol():
                fund_postion = Position(acct=account)
                fund_postion.date = date
                fund_postion.security_id = sec_id
                fund_postion.amount = 0
                fund_postion.today_price = 0
                account.get_position(date).append(fund_postion)
        else:
            # 非第一日，则今日复制上一日
            account.position_record[date] = []
            for p in account.get_position(self.get_context().previous_day):
                new_p = Position.copy(p)
                new_p.date = date
                account.position_record[date].append(new_p)


class Context:
    # 客户访问的数据包
    # context中含有数据，是{'资产id', df}
    # df的内容：date|date,price,上一日
    # 数据的时间范围是 [start-windows, end]

    def __init__(self):
        self.today = ""     # 当前日
        self.previous_day = ""  # 前一日

        self.data = {}    # 数据池     symbol: dataframe
        self._accounts = {}     # 账户，支持多账户, name:acct_obj

    def get_accounts(self):
        # 返回所有的账户的对象列表
        return list(self._accounts.values())

    def add_account(self, name, acct_obj):
        if name in self._accounts:
            raise KeyError('同名账户已存在')
        self._accounts[name] = acct_obj

    def get_account(self, name):
        return self._accounts[name]
