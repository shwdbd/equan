#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fund_backtesting.py
@Time    :   2020/03/07 19:23:51
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基金回测框架

'''
import pandas as pd
import os
from equan.fund.tl import log
from equan.fund.fund_backtesting_impl import Order, Account, Position, StrategyResult

DATA_DIR = r'src/equan/fund/data/'


class FundBackTester:

    def __init__(self):
        # 全局参数：
        self.start_date = ""
        self.end_date = ""
        self.unverise = ''   # 资产池
        # benchmark
        self.account = None
        self.commission = 0.001     # 佣金，千分之一

        # 内部参数：
        self.__version__ = "0.0.1"

    def fm_log(self, msg):
        # 框架的日志
        log.info('【回测】' + msg)

    def run(self):
        self.fm_log('回测启动')
        # 策略运行
        self._initialize_by_framework()   # 准备数据等
        # self.fm_log('调用用户 initialize() ')
        self.initialize()   # 调用用户的策略初始化
        # self.fm_log('用户 initialize() 结束')

        number_of_day = 0
        for date in self.context.df.index:
            # 切日操作：
            self._date_switch(date)

            # self.fm_log('策略 {0} 执行 ... '.format(date))
            self.date_handle(self.context)   # 调用用户的策略初始化

            # 日终处理：
            # self.fm_log('日终处理 {0} ... '.format(date))
            self._dayend_handle(date)   # 调用用户的策略初始化

            # self.fm_log('---- {0} END -------'.format(date))
            number_of_day += 1
        self.fm_log('策略运行完毕 【共{0}个交易日】'.format(number_of_day))

        # 全部结束后的处理
        self.finish()

    def finish(self):
        # 全部结束后的处理
        # 生成汇总result对象
        # 导出结果

        # 计算汇总对象：
        result = StrategyResult(acct=self.account)
        result.summary()

        # TODO 策略结果输出到文本：




    def _date_switch(self, date):
        # 切日操作
        self.context.today = date
        self.context.previous_day = self.context.df.loc[date, '上一日']
        # print('{0} , {1}'.format(self.context.previous_day, self.context.today))

    def _initialize_by_framework(self):
        # 最初的准备：

        # 准备数据
        self.context = Context()
        self.context.df = self.get_data()
        self.fm_log('准备数据')

        # 初始化Account
        self.context.account = self.account

    def get_data(self):
        # 取得基金日线数据
        # 返回df: date|price,  order by date desc
        data_file = DATA_DIR + '{fund_symbol}.csv'.format(fund_symbol=self.unverise)
        if not os.path.exists(data_file):
            print('数据不存在，无法获得数据! ' + str(data_file))
            return None
        else:
            df = pd.read_csv(filepath_or_buffer=data_file, usecols=['FSRQ', 'DWJZ'])
            df.rename(columns={"FSRQ": "date", "DWJZ": "price"}, inplace=True)
            # 日期过滤
            df = df.loc[(df.date >= self.start_date) & (df.date <= self.end_date)]
            # 计算昨日:
            df['上一日'] = df['date'].shift(-1)

            # 排序
            df = df.sort_values(by=['date'], ascending=True)

            # 将日期设置为index
            df.set_index(['date'], drop=False, inplace=True)
            # df.reset_index(inplace=True, drop=True)
            self._df = df.copy()
            self.data = df.copy()   # TODO 要检查 self.data修改后不能影响self._df
            return df

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
        account = self.context.account

        # 初始化position
        if len(account.position_record) == 1:
            # 第一日情况：
            # TODO 第一日，初始化，是否可以在init函数中完成
            account.get_position(date).append(account.get_position(Account.CASH_DAY0)[0])    # 现金账户
            fund_postion = Position(acct=account)
            fund_postion.date = date
            fund_postion.security_id = self.unverise
            fund_postion.amount = 0
            fund_postion.today_price = 0
            account.get_position(date).append(fund_postion)
        else:
            # 非第一日，则今日复制上一日
            # account.get_position(date).append(account.get_position(self.context.previous_day))
            account.position_record[date] = account.get_position(self.context.previous_day)

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
                if self.context.previous_day is None:
                    log.error('取上日为空，则此order无法按市场定价，则此order被拒绝')
                    order.status = Order.STATUS_FAILED
                    break
                else:
                    order.order_price = self.context.df.loc[self.context.previous_day, 'price']     # 此处会出现上一日价格为None的情况

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
                fund_p.today_price = self.context.df.loc[self.context.today, 'price']  # 按今日牌价
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

    def __init__(self):
        self.today = ""     # 当前日
        self.previous_day = ""  # 前一日

        self.df = None    # 供用户使用的df
        self.account = None     # 账户

    def get_account(self):
        return self.account
