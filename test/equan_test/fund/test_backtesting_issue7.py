#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_backtesting_issue7.py
@Time    :   2020/03/26 12:08:09
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试，解决Issue7提出的问题

数据文件中日期：2020-01-01 ：2020-01-04
回测周期是： 2020-01-01 ：2020-01-10
且在客户端中，要取每天的价格，应该会出现KeyError异常

'''
from equan.fund.fund_backtesting import FundBackTester
from equan.fund.fund_backtesting_impl import Account, FundUnverise
import equan.fund.tl as tl
import unittest
import equan.fund.data_api as data_api
import shutil
import os

log = tl.get_logger()


class MyTestStrategy(FundBackTester):
    """测试用策略1
    """

    def __init__(self):
        super().__init__()

        # 初始化账户
        fund_acct = Account('基金定投账户', initial_capital=10)
        self.get_context().add_account(fund_acct)

        # 资产池
        self.set_unverise(FundUnverise(['005918']))    # 定义资产池

    def initialize(self):
        """
        1. 在account的数据中，增加一列星期几的字段
        2. 将data复制到self.initialize_data变量中，使得可以单元测试到
        """
        # # 星期数据的计算
        # df = self.get_context().data['005918']
        # df['星期'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').weekday()+1)
        pass

    def date_handle(self, context):
        # 每日执行
        # 查看每日的数据

        df = self.get_context().data['005918']
        print(context.today)
        print(df.loc[context.today, 'price'])
        # week = df.loc[context.today, '星期']
        # print(week)


class TestMyTestStrategy_Issue7(unittest.TestCase):
    """测试Issue7的问题：如果回测日期超过已有数据范围，则会报Key-Error错误
    """

    def setUp(self):
        self.test_path = r'test/equan_test/fund/'   # 当前用例的路径
        self.data_path = r'test/equan_test/fund/fund_data/'  # 测试文件存放路径

        # 准备测试数据
        shutil.copy2(self.test_path + r'005918_backtesting_issue7.csv', self.data_path + r'005918.csv')
        shutil.copy2(self.test_path + r'cal_backtesting_issue7.csv', self.data_path + r'cal.csv')
        self.bak_of_filepath = data_api.CAL_DATA_FILE
        data_api.CAL_DATA_FILE = self.data_path + r'cal.csv'
        self.bak_of_dirpath = data_api.FUND_DATA_DIR
        data_api.FUND_DATA_DIR = self.data_path
        return super().setUp()

    def tearDown(self):
        data_api.CAL_DATA_FILE = self.bak_of_filepath
        data_api.FUND_DATA_DIR = self.bak_of_dirpath
        # 删除测试用文件
        os.remove(self.data_path + r'005918.csv')
        os.remove(self.data_path + r'cal.csv')
        return super().tearDown()

    def test_normal(self):
        start_date = '2019-01-01'
        end_date = '2019-01-10'
        strategy = MyTestStrategy()
        strategy.start_date = start_date
        strategy.end_date = end_date
        strategy.set_unverise(FundUnverise(['005918']))    # 定义资产池

        try:
            # 策略运行
            strategy.run()
        except Exception:
            self.fail()


if __name__ == "__main__":
    # 准备测试数据
    test_path = r'test/equan_test/fund/'   # 当前用例的路径
    data_path = r'test/equan_test/fund/fund_data/'  # 测试文件存放路径
    shutil.copy2(test_path + r'005918_backtesting_issue7.csv', data_path + r'005918.csv')
    shutil.copy2(test_path + r'cal_backtesting_issue7.csv', data_path + r'cal.csv')
    data_api.CAL_DATA_FILE = data_path + r'cal.csv'
    data_api.FUND_DATA_DIR = data_path

    start_date = '2019-01-01'
    end_date = '2019-01-09'
    strategy = MyTestStrategy()
    strategy.start_date = start_date
    strategy.end_date = end_date
    strategy.set_unverise(FundUnverise(['005918']))    # 定义资产池
    # 策略运行
    strategy.run()
