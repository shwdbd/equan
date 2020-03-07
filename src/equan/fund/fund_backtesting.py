#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fund_backtesting.py
@Time    :   2020/03/07 19:23:51
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基金回测框架

# FIXME print改log

'''
import pandas as pd
import datetime
import numpy as np
import os
from equan.fund.tl import log

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
        log.debug('【回测】' + msg)

    def run(self):
        self.fm_log('回测启动')
        # 策略运行
        self._initialize_by_framework()   # 准备数据等
        self.fm_log('调用用户 initialize() ')
        self.initialize()   # 调用用户的策略初始化
        self.fm_log('用户 initialize() 结束')

        # previous_day = None
        for date in self.context.df.index:
            # 切日操作：
            self._date_switch(date)

            self.fm_log('策略 {0} 执行 ... '.format(date))
            self.date_handle(self.context)   # 调用用户的策略初始化

            # 日终处理：
            self.fm_log('日终处理 {0} ... '.format(date))
            self._dayend_handle(date)   # 调用用户的策略初始化

            self.fm_log('---- {0} END -------'.format(date))
        # TODO 全部结束后的处理
        print(self.account.order_record)


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

            # TODO 星期字段要去除
            # df['星期'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').weekday()+1)

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
        # TODO 交易撮合
        self.fm_log('撮合交易 {0}'.format(date))
        # FIXME 逐账户进行处理
        # 首先处理 现金 order ，然后再处理资产 order
        # 逐个order进行处理
        # 结果是完成cash、资产的当日position计算


        pass


class Context:
    # 客户访问的数据包

    def __init__(self):
        self.today = ""     # 当前日
        self.previous_day = ""  # 前一日

        self.df = None    # 供用户使用的df
        self.account = None     # 账户

    def get_account(self):
        return self.account
