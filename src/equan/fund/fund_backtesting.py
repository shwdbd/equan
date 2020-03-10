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
import os
import equan.fund.tl as tl
from equan.fund.fund_backtesting_impl import Order, Account, Position, StrategyResult
import datetime
from equan.fund.data_api import DataAPI

DATA_DIR = r'src/equan/fund/data/'

log = tl.get_logger()


class FundBackTester:

    DATE_FORMAT = '%Y-%M-%d'

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

            self.fm_log('---- {0} OVER -------'.format(date))
            previous_day = date
            number_of_day += 1
        self.fm_log('策略运行完毕 【共{0}个交易日】'.format(number_of_day))

        # 全部结束后的处理
        self.finish()

    def finish(self):
        # 全部结束后的处理
        # 生成汇总result对象
        # 导出结果

        # FIXME 【变为多account后，要改】计算汇总对象：
        # result = StrategyResult(acct=self.account)
        # result.summary()

        # TODO 策略结果输出到文本：
        pass

    def _initialize_by_framework(self):
        # 策略执行前的准备工作
        # 1. 准备数据
        # 按universe逐个准备数据
        for sec_id in self.get_unverise().get_symbol():
            self.get_context().data[sec_id] = self._load_data(sec_id)       # FIXME 要改！
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
            # 初始化position
            if len(account.position_record) == 1:
                # 第一日情况：
                # TODO 第一日，初始化，是否可以在init函数中完成
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

            # 订单处理
            # FEATURE 目前仅支持市价单
            for order in account.get_orders(date):
                # 按order逐一处理：

                # 1. 明确价格
                # 2. 双边，调整position
                # 3. 加入佣金的计算
                # 4. 更新order的成交值和状态

                # 价格：
                if order.order_price is None:
                    # 按市价执行，按上一日价格执行
                    if self.get_context().previous_day is None:
                        log.error('取上日为空，则此order无法按市场定价，则此order被拒绝')
                        order.status = Order.STATUS_FAILED
                        break
                    else:
                        order.order_price = self.get_context().data[order.security_id].loc[self.get_context().previous_day, 'price']     # 此处会出现上一日价格为None的情况

                # 扣减现金position，按成交价扣减
                cash_p = account.get_position_by_id(date, Account.CASH_SEC_ID)
                if cash_p:
                    cash_p.amount += -1 * order.direction * (order.order_amount * order.order_price)
                else:
                    log.error('no cash')
                # 增加基金position，按当日市价计算
                fund_p = account.get_position_by_id(date, order.security_id)
                if fund_p:
                    fund_p.amount += order.direction * order.order_amount
                    fund_p.today_price = order.order_price   # 按订单价格计算
                else:
                    log.error('no fund')

                # 更新order的成交值和状态
                order.turnover_amount = order.order_amount
                order.turnover_price = order.order_price
                order.status = Order.STATUS_SUCCESS

                # # 有order才输出，否则不要输出
                # log.info('{0} orders :'.format(date))
                # log.info(account.get_orders(date))
                # log.info('{0} position :'.format(date))
                # log.info(account.get_position(date))
                # log.info('-'*20)
            # end of order

            # 每日日终，计算账户的收益率等结果数据：
            # '总资产', '累计投入资金', '收益率'
            total_asset = 0     # 总资产
            for p in account.get_position(date):
                if p.security_id != Account.CASH_SEC_ID:
                    total_asset += p.get_value()
            accumulated_investment = 0      # 累计投入资金
            accumulated_investment = account.initial_capital - account.get_position_by_id(date, Account.CASH_SEC_ID).get_value()    
            # FIXME 此处算法有问题，其前提是基于只买不卖基金的基础上
            # 收益率
            return_ratio = 0
            if accumulated_investment != 0:
                return_ratio = (total_asset-accumulated_investment)*100/accumulated_investment
            # 交易次数
            number_of_order = len(account.get_orders(date))
            # log.info('{0} 收益率 {1} {2} / {3}:'.format(date, round(return_ratio, 4), total_asset, accumulated_investment))
            # 写入account的result对象
            s_result = pd.Series(data={'总资产': total_asset, '累计投入资金': accumulated_investment, '收益率': return_ratio, '交易次数': number_of_order}, name=date)
            account.result = account.result.append(s_result)


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
