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

规则：
1. 统计的交易次数，仅包括成功的交易；



'''
import pandas as pd
import equan.fund.tl as tl
from equan.fund.fund_backtesting_impl import Order, Account, Position, StrategyResult
import equan.fdata as fd
import equan.fund.result_exportor as exporter
import math
import datetime

log = tl.get_logger()


class FundBackTester:

    def __init__(self):
        # 全局参数：
        self.start_date = ""
        self.end_date = ""
        self._unverise = None   # 资产池
        # benchmark
        self.commission = 0.001     # 佣金，千分之一

        # 内部参数：
        self.__version__ = "0.2"

        # 客户端可修改参数：
        self.settings = {
            # 回测结果HTML输出参数
            "html-exporter.enabled": True,              # 是否输出到HTML
            "html-exporter.path": r"temp/",
            "html-exporter.file_name": r"我的策略.html",
        }
        self._running_dates = []    # 需要轮询执行的日期列表

        # 初始化上下文
        self._context = Context()

        # 测试结果
        self.result = StrategyResult()

    # ------------------------
    # 客户端需要继承实现的函数
    def initialize(self):
        # 用户初始化
        pass

    def date_handle(self, context):
        # 需要具体实现继承
        pass

    def after_dayend(self, context):
        # 需要具体实现继承
        pass

    def end(self):
        # 策略之后后的代码
        # 需要具体实现继承
        pass
    # ------------------------

    def fm_log(self, msg):
        # 框架的日志
        log.info('【回测】' + msg)

    def get_unverise(self):
        return self._unverise

    def set_unverise(self, unverise):
        self._unverise = unverise

    def get_context(self):
        return self._context

    def get_running_dates(self):
        # 返回指定运算的日期列表
        return self._running_dates

    def run(self):
        self.fm_log('回测启动')

        start_time = datetime.datetime.now()    # 开始执行时间戳

        # 策略运行
        self._initialize_by_framework()   # 准备数据等

        # self.fm_log('调用用户 initialize() ')
        self.initialize()   # 调用用户的策略初始化
        # self.fm_log('用户 initialize() 结束')

        pre_trade_day = None   # 前一日
        self._running_dates = fd.get_cal(self.start_date, self.end_date)
        for date in self.get_running_dates():
            # 切日操作：
            self.get_context().today = date
            self.get_context().pre_trade_day = pre_trade_day

            # 如当日无数据，则跳过并日志报错
            if self._check_account_data_lack(self.get_context().today):
                # 客户：每日逻辑
                self.date_handle(self.get_context())

                # 日终处理：
                self._dayend_handle(date)

                # 客户：日终后处理
                self.after_dayend(self.get_context())

            # 日期切换
            pre_trade_day = date
        self.fm_log('策略运行完毕 【共{0}个交易日】'.format(len(self.get_running_dates())))

        # 计算策略总体收益
        self._calculate_strategy_earnings()

        # 结果输出到控制台(日志文件中)
        exporter.export_to_console(self.result, self)

        # 结果输出到HTML
        if self.settings['html-exporter.enabled']:
            exporter.export_to_html(self.result, self)

        # 客户端实现的结果输出
        self.end()
        # ------------------------策略运行完成----------------------------
        end_time = datetime.datetime.now()
        self.fm_log('策略运行时间 ：{0} 秒'.format((end_time-start_time).seconds))

    def _check_account_data_lack(self, date):
        # 判断账户数据是否有缺失，默认返回True
        # 如果date日有任一账户有缺失，则返回False
        for symbol in self.get_unverise().get_symbol():
            if date not in self.get_context().data[symbol].index:
                log.error('资产{symbol} 在 {date} 缺失数据，策略在当时跳过执行，请关注！'.format(symbol=symbol, date=date))
                return False
        return True

    def result_export_to_console(self, result):
        self.fm_log('='*20)
        self.fm_log('策略总收益 ：{0} %'.format(result.return_rate))
        self.fm_log('交易次数 ：{0} '.format(round(result.total_number_of_transactions)))
        self.fm_log('期末收益资金 ：{0}'.format(result.value))
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
        return fd.fund_daily_price(symbol, self.start_date, self.end_date)

    def _dayend_handle(self, date):
        """日终处理
        每日日终后要做的事情如下：
        - 撮合当日订单Order
        - 计算每个账户的收益率
        - 计算策略总的收益率

        Arguments:
            date {str} -- 日期
        """
        # 日终处理
        # 每日日终后，主要做交易撮合
        # 计算每日后account的 资产总值
        df_acct_return = pd.DataFrame(data={})
        for account in self.get_context().get_accounts():
            # 初始化当日头寸
            self._init_daily_position(account, date)

            # 订单撮合
            for order in account.get_orders(date):
                self._matchmaking_order(order, date, account)
            # end of order

            # 更新头寸中的资产价格
            for p in account.get_position(date):
                if p.security_id != Account.CASH_SEC_ID:
                    p.today_price = self.get_context().data[p.security_id].loc[date, 'price']

            # 计算账户当日收益
            return_data = self._calculate_account_earnings(date, account)
            df_acct_return = df_acct_return.append(return_data, ignore_index=True)

        # 填，策略每日收益率表格
        # ['日期', '总资产', '当期收益率', '累计收益率', '交易次数']
        data = {
            '总资产': round(df_acct_return['总资产'].sum(), 2),
            '当期收益率': round(df_acct_return['当期收益率'].sum() / len(self.get_context().get_accounts()), 2),    # 策略收益率按账户数量取绝对平均
            '交易次数': round(df_acct_return['交易次数'].sum())}
        self.result.append(date, data)

    def _calculate_strategy_earnings(self):
        """计算策略总体收益
        """
        # 计算每个账户每天的收益
        for account in self.get_context().get_accounts():
            # 计算每日的累计收益率
            account.get_daily_return()['累计收益率'] = account.get_daily_return()['当期收益率'].cumsum()

            # 账户总收益率（看最后一天的累计收益率）
            account.return_ratio = float(account._daily_return.tail(1)['累计收益率'])
            # 总交易次数
            account.number_of_transactions = account._daily_return['交易次数'].sum()

            # 策略累计
            self.result.return_rate += account.return_ratio
            self.result.total_capital_input += account.initial_capital
            self.result.total_number_of_transactions += account.number_of_transactions
            self.result.value += round(float(account._daily_return.tail(1)['总资产']), 2)

        # 计算策略总参数：
        # 1. 策略每日累计收益率：
        self.result.get_return_table()['累计收益率'] = self.result.get_return_table()['当期收益率'].cumsum()
        # 2. 策略收益率：
        self.result.return_rate = round(float(self.result.get_return_table().tail(1)['累计收益率']), 2)
        # 3. 策略期末资产总价值：
        self.result.value = round(float(self.result.get_return_table().tail(1)['总资产']), 2)
        # 4. 总交易次数
        self.result.total_number_of_transactions = int(self.result.get_return_table()['交易次数'].sum())

    def _calculate_account_earnings(self, date, account):
        """计算账户日终收益

        在 account.cols_of_return 中添加一行
        计算：'日期', '总资产', '当期收益率', '累计收益率', '交易次数'

        并返回当日的数据，用dict格式返回

        Arguments:
            date {[type]} -- [description]
            account {[type]} -- [description]
        """
        # 计算 总资产
        total_value = 0
        for p in account.get_position(date):
            total_value += p.get_value()

        # 计算每日的账户收益率
        # 账户当日收益率
        if account._daily_return.empty:
            return_ratio = 0        # 首日收益率为0
        else:
            p2 = total_value
            p1 = float(account._daily_return.loc[self.get_context().pre_trade_day, '总资产'])
            return_ratio = round(math.log(p2/p1) * 100, 2)
        # print('acct return ={0}  [{1}]'.format(return_ratio, date))

        # 交易次数，仅成功交易
        number_of_order = 0
        for order in account.get_orders(date):
            if order.status == Order.STATUS_SUCCESS:
                number_of_order += 1

        # 汇总加入
        return_data = {
            '总资产': total_value,
            '当期收益率': return_ratio,
            '交易次数': number_of_order}
        s_result = pd.Series(data=return_data, name=date)
        account._daily_return = account.get_daily_return().append(s_result)

        return return_data

    def _matchmaking_order(self, order, date, account):
        # 订单撮合

        # 按order逐一处理：

        # 1. 明确价格
        # 2. 双边，调整position
        # 3. 加入佣金的计算
        # 4. 更新order的成交值和状态
        # FEATURE 目前仅支持市价单

        # 计算拟成交价格
        # 如果是市价单，则当日close价格成交
        if order.order_price is None:
            # 按市价执行，则当日close价格成交
            closing_price = self.get_context().data[order.security_id].loc[self.get_context().today, 'price']  # close价格
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
                    # order.order_price = closing_price
                    cash_p.amount += -1 * volume_of_amount
                    fund_p.amount += order.order_amount
                    fund_p.today_price = order.order_price   # 按订单价格计算
                    order.turnover_amount = order.order_amount
                    order.turnover_price = closing_price
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
                    # order.order_price = closing_price
                    cash_p.amount += 1 * volume_of_amount
                    fund_p.amount += order.order_amount
                    fund_p.today_price = order.order_price   # 按订单价格计算
                    order.turnover_amount = order.order_amount
                    order.turnover_price = closing_price
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
            for p in account.get_position(self.get_context().pre_trade_day):
                new_p = Position.copy(p)
                new_p.date = date
                # 此处要更新今日价格
                if new_p.security_id != Account.CASH_SEC_ID:
                    new_p.today_price = self.get_context().data[new_p.security_id].loc[date, 'price']

                account.position_record[date].append(new_p)


class Context:
    # 客户访问的数据包
    # context中含有数据，是{'资产id', df}
    # df的内容：date|date,price,上一日
    # 数据的时间范围是 [start-windows, end]

    def __init__(self):
        self.today = ""     # 当前日
        self.pre_trade_day = ""  # 前一日(交易日)

        self.data = {}    # 数据池     symbol: dataframe
        self._accounts = {}     # 账户，支持多账户, name:acct_obj

    def get_accounts(self):
        # 返回所有的账户的对象列表
        return list(self._accounts.values())

    def add_account(self, name, acct_obj):
        if not name:
            name = acct_obj.name
        if name in self._accounts:
            raise KeyError('同名账户已存在')
        self._accounts[name] = acct_obj

    def get_account(self, name):
        return self._accounts[name]
