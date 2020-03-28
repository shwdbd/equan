#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_backtesting_1.py
@Time    :   2020/03/10 11:10:45
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   针对 回测第1版功能 单元测试

测试案例1：
- 2019年1个基金全年数据；
- 单一账户，有初始资金
- 规则：周1买入50%买入，周5空仓；
- 策略执行1年2019=

# FIXME 货币精度，当期收益率的精度

'''
from equan.fund.fund_backtesting import FundBackTester
from equan.fund.fund_backtesting_impl import Account, FundUnverise, Order
import equan.fund.tl as tl
import unittest
import datetime
import equan.fund.data_api as data_api
import shutil
import os
import pandas as pd
from pandas.util.testing import assert_frame_equal
import copy

log = tl.get_logger()


class MyTestStrategy(FundBackTester):
    """测试用策略1
    """

    def __init__(self):
        super().__init__()

        # 初始化账户
        fund_acct = Account('基金定投账户', initial_capital=10)
        self.get_context().add_account('基金定投账户', fund_acct)

        # 资产池
        self.set_unverise(FundUnverise(['005918']))    # 定义资产池

        # 函数调用标识
        self.func_called = ['__init__']   # 被调用的函数列表
        self.dates_of_date_handle = []  # 被调用过的日期
        self.dates_of_after_dayend = []

    def initialize(self):
        """
        1. 在account的数据中，增加一列星期几的字段
        2. 将data复制到self.initialize_data变量中，使得可以单元测试到
        """
        self.func_called.append('initialize')   # 证明函数被调用

        # 存个数据包的快照
        self.data_snap = copy.deepcopy(self.get_context().data)

        data_df = self.get_context().data['005918']
        data_df['week'] = data_df['date'].apply(lambda x: datetime.datetime.strptime(x, data_api.DATE_FORMAT).weekday()+1)
        self.testdata_init_datadf = data_df.copy()  # 生成检测用数据
        # print(self.testdata_init_datadf['week'])

    def date_handle(self, context):
        # # 每日执行
        # print(context.today)

        # 证明这个函数，被调用的日期
        self.dates_of_date_handle.append(context.today)

        today = context.today
        acct = context.get_account('基金定投账户')
        if today == '2019-01-03':
            # 正常单，市价单
            acct.order(today, '005918', amount=2)   # 市价单,买2手基金
        elif today == '2019-01-04':
            # 买100手失败，因为现金余额不足
            acct.order(today, '005918', amount=100)
        elif today == '2019-01-07':
            # 卖10手失败，因为资产份额不足
            acct.order(today, '005918', amount=-10)
        elif today == '2019-01-08':
            # 卖1手成功
            acct.order(today, '005918', amount=-1)

    def after_dayend(self, context):
        # print('{0} endday '.format(context.today))
        # acct = context.get_account('基金定投账户')
        # print(acct.get_position(context.today)) # 头寸
        # print(acct.get_orders(context.today))   # 订单
        # # print(acct.get_daily_return())
        # print('-'*10)
        self.dates_of_after_dayend.append(context.today)
        pass


class TestMyTestStrategy(unittest.TestCase):
    """测试最简单的回测逻辑
    """

    def setUp(self):
        self.test_path = r'test/equan_test/fund/'   # 当前用例的路径
        self.data_path = r'test/equan_test/fund/fund_data'  # 测试文件存放路径

        # 准备测试数据
        shutil.copy2(self.test_path + r'005918_backtesting.csv', self.data_path + r'005918.csv')
        shutil.copy2(self.test_path + r'cal_backtesting.csv', self.data_path + r'cal.csv')
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
        end_date = '2019-01-08'
        strategy = MyTestStrategy()
        strategy.start_date = start_date
        strategy.end_date = end_date
        strategy.set_unverise(FundUnverise(['005918']))    # 定义资产池
        # 策略运行
        strategy.run()

        # 检查默认的数据准备
        self.check_data(strategy)

        # 检查各步骤调用次序
        self.check_func_callable(strategy)

        # 检查2019-01-03情况
        self.check_20190103(strategy)

        # 检查2019-01-04情况
        self.check_20190104(strategy)

        # 检查2019-01-07情况
        self.check_20190107(strategy)

        # 检查2019-01-08情况
        self.check_20190108(strategy)

        # 检查策略结果
        self.check_result(strategy)

        # 检查策略输出到HTML的情况
        self.check_exp_to_html(strategy)

    def check_data(self, strategy):
        # 检查回测框架准备的数据集合

        # data_df = strategy.get_context().data['005918']
        data_df = strategy.data_snap['005918']      # 当时留下的历史数据
        print(data_df)
        self.assertIsNotNone(data_df)
        # 检查内容
        data_dict = {
            'date': ['2019-01-02', '2019-01-03', '2019-01-04', '2019-01-07', '2019-01-08'],
            'pretrade_date': ['2018-12-28', '2019-01-02', '2019-01-03', '2019-01-04', '2019-01-07'],
            'price': [0.7997, 0.7985, 0.8163, 0.8209, 0.8192]
        }
        df = pd.DataFrame(data=data_dict, index=pd.Series(name='date', data=data_dict['date']))
        # print(df)
        assert_frame_equal(data_df, df, check_like=True)

    def check_func_callable(self, strategy):
        # 检查各函数执行顺序

        # 客户都函数被调用顺序
        func_called = ['__init__', 'initialize']
        self.assertListEqual(func_called, strategy.func_called)

        # 跑批的日期
        # 检查date_handle被调用情况
        dates = ['2019-01-02', '2019-01-03', '2019-01-04', '2019-01-07', '2019-01-08']
        self.assertListEqual(dates, strategy.dates_of_date_handle)
        self.assertListEqual(dates, strategy.dates_of_after_dayend)

    def check_20190103(self, strategy):
        # 检查2019-01-03情况
        # 01-03 买入2份基金，成功
        date = '2019-01-03'
        security_id = '005918'
        today_close_price = 0.7985

        # Acct
        acct = strategy.get_context().get_account('基金定投账户')
        self.assertIsNotNone(acct)

        # Order
        orders = acct.get_orders(date)
        self.assertEqual(1, len(orders))
        order_buy = orders[0]
        self.assertIsNotNone(order_buy)
        self.assertEqual(date, order_buy.date)
        self.assertEqual(security_id, order_buy.security_id)
        self.assertEqual(Order.DIRECTION_BUY, order_buy.direction)
        self.assertEqual(2, order_buy.order_amount)
        self.assertEqual(None, order_buy.order_price)   # 市价单
        self.assertEqual(2, order_buy.turnover_amount)
        self.assertEqual(today_close_price, order_buy.turnover_price)
        self.assertEqual(Order.STATUS_SUCCESS, order_buy.status)

        # Position
        posistions = acct.get_position(date)
        self.assertEqual(2, len(posistions))    # 两个头寸，1个现金账户，1个资产账户
        p_cash = acct.get_position_by_id(date, Account.CASH_SEC_ID)
        self.assertIsNotNone(p_cash)
        self.assertEqual(date, p_cash.date)
        self.assertEqual(Account.CASH_SEC_ID, p_cash.security_id)
        self.assertEqual(8.403, p_cash.amount)
        self.assertEqual(1, p_cash.today_price)
        self.assertEqual(8.40, p_cash.get_value())
        # 资产账户
        p_fund = acct.get_position_by_id(date, security_id)
        self.assertIsNotNone(p_fund)
        self.assertEqual(date, p_fund.date)
        self.assertEqual(security_id, p_fund.security_id)
        self.assertEqual(2, p_fund.amount)
        self.assertEqual(today_close_price, p_fund.today_price)
        self.assertEqual(1.60, p_fund.get_value())

        # 当日策略result
        result = strategy.result
        self.assertIsNotNone(result)
        result_table = strategy.result.get_return_table()
        self.assertEqual(10, result_table.loc[date, '总资产'])
        self.assertEqual(0, result_table.loc[date, '当期收益率'])
        self.assertEqual(0, result_table.loc[date, '累计收益率'])
        self.assertEqual(1, result_table.loc[date, '交易次数'])

    def check_20190104(self, strategy):
        # 检查2019-01-04情况
        # 01-04 买入100份基金，失败
        date = '2019-01-04'
        security_id = '005918'
        today_close_price = 0.8163

        # Acct
        acct = strategy.get_context().get_account('基金定投账户')
        self.assertIsNotNone(acct)

        # Order
        orders = acct.get_orders(date)
        self.assertEqual(1, len(orders))
        order_buy = orders[0]   # 失败单
        self.assertIsNotNone(order_buy)
        self.assertEqual(date, order_buy.date)
        self.assertEqual(security_id, order_buy.security_id)
        self.assertEqual(Order.DIRECTION_BUY, order_buy.direction)
        self.assertEqual(100, order_buy.order_amount)
        self.assertEqual(None, order_buy.order_price)
        self.assertEqual(0, order_buy.turnover_amount)
        self.assertEqual(None, order_buy.turnover_price)   # 市价单且未成功，所以没有价格
        self.assertEqual(Order.STATUS_FAILED, order_buy.status)
        self.assertEqual('现金账户余额不足', order_buy.failed_messge)

        # Position
        position = acct.get_position(date)
        self.assertEqual(2, len(position))    # 两个头寸，1个现金账户，1个资产账户
        p_cash = acct.get_position_by_id(date, Account.CASH_SEC_ID)
        self.assertIsNotNone(p_cash)
        self.assertEqual(date, p_cash.date)
        self.assertEqual(Account.CASH_SEC_ID, p_cash.security_id)
        self.assertEqual(8.403, p_cash.amount)
        self.assertEqual(1, p_cash.today_price)
        self.assertEqual(8.40, p_cash.get_value())
        # 资产账户
        p_fund = acct.get_position_by_id(date, security_id)
        self.assertIsNotNone(p_fund)
        self.assertEqual(date, p_fund.date)
        self.assertEqual(security_id, p_fund.security_id)
        self.assertEqual(2, p_fund.amount)
        self.assertEqual(today_close_price, p_fund.today_price)
        self.assertEqual(1.63, p_fund.get_value())

        # 当日策略result
        result = strategy.result
        self.assertIsNotNone(result)
        result_table = strategy.result.get_return_table()
        self.assertEqual(10.03, result_table.loc[date, '总资产'])
        self.assertEqual(0.3, result_table.loc[date, '当期收益率'])
        self.assertEqual(0.3, result_table.loc[date, '累计收益率'])
        self.assertEqual(0, result_table.loc[date, '交易次数'])

    def check_20190107(self, strategy):
        # 检查2019-01-07情况
        # 01-07 卖出10份基金，失败
        date = '2019-01-07'
        security_id = '005918'
        today_close_price = 0.8209

        # Acct
        acct = strategy.get_context().get_account('基金定投账户')
        self.assertIsNotNone(acct)

        # Order
        orders = acct.get_orders(date)
        self.assertEqual(1, len(orders))
        order_buy = orders[0]   # 失败单
        self.assertIsNotNone(order_buy)
        self.assertEqual(date, order_buy.date)
        self.assertEqual(security_id, order_buy.security_id)
        self.assertEqual(Order.DIRECTION_SELL, order_buy.direction)
        self.assertEqual(-10, order_buy.order_amount)
        self.assertEqual(None, order_buy.order_price)
        self.assertEqual(0, order_buy.turnover_amount)
        self.assertEqual(None, order_buy.turnover_price)   # 市价单且未成功，所以没有价格
        self.assertEqual(Order.STATUS_FAILED, order_buy.status)
        self.assertEqual('持有份数不足', order_buy.failed_messge)

        # Position
        position = acct.get_position(date)
        self.assertEqual(2, len(position))    # 两个头寸，1个现金账户，1个资产账户
        p_cash = acct.get_position_by_id(date, Account.CASH_SEC_ID)
        self.assertIsNotNone(p_cash)
        self.assertEqual(date, p_cash.date)
        self.assertEqual(Account.CASH_SEC_ID, p_cash.security_id)
        self.assertEqual(8.403, p_cash.amount)
        self.assertEqual(1, p_cash.today_price)
        self.assertEqual(8.40, p_cash.get_value())
        # 资产账户
        p_fund = acct.get_position_by_id(date, security_id)
        self.assertIsNotNone(p_fund)
        self.assertEqual(date, p_fund.date)
        self.assertEqual(security_id, p_fund.security_id)
        self.assertEqual(2, p_fund.amount)
        self.assertEqual(today_close_price, p_fund.today_price)
        self.assertEqual(1.64, p_fund.get_value())

        # 当日策略result
        result = strategy.result
        self.assertIsNotNone(result)
        result_table = strategy.result.get_return_table()
        self.assertEqual(10.04, result_table.loc[date, '总资产'])
        self.assertEqual(0.1, result_table.loc[date, '当期收益率'])
        self.assertEqual(0.4, result_table.loc[date, '累计收益率'])
        self.assertEqual(0, result_table.loc[date, '交易次数'])

    def check_20190108(self, strategy):
        # 检查2019-01-08情况
        # 01-08 卖出1份基金，成功
        date = '2019-01-08'
        security_id = '005918'
        today_close_price = 0.8192

        # Acct
        acct = strategy.get_context().get_account('基金定投账户')
        self.assertIsNotNone(acct)

        # Order
        orders = acct.get_orders(date)
        self.assertEqual(1, len(orders))
        order_buy = orders[0]   # 成功单
        self.assertIsNotNone(order_buy)
        self.assertEqual(date, order_buy.date)
        self.assertEqual(security_id, order_buy.security_id)
        self.assertEqual(Order.DIRECTION_SELL, order_buy.direction)
        self.assertEqual(-1, order_buy.order_amount)
        self.assertEqual(None, order_buy.order_price)
        self.assertEqual(-1, order_buy.turnover_amount)
        self.assertEqual(today_close_price, order_buy.turnover_price)
        self.assertEqual(Order.STATUS_SUCCESS, order_buy.status)
        self.assertEqual('', order_buy.failed_messge)

        # Position
        position = acct.get_position(date)
        self.assertEqual(2, len(position))    # 两个头寸，1个现金账户，1个资产账户
        p_cash = acct.get_position_by_id(date, Account.CASH_SEC_ID)
        self.assertIsNotNone(p_cash)
        self.assertEqual(date, p_cash.date)
        self.assertEqual(Account.CASH_SEC_ID, p_cash.security_id)
        self.assertEqual(9.2222, p_cash.amount)
        self.assertEqual(1, p_cash.today_price)
        self.assertEqual(9.22, p_cash.get_value())
        # 资产账户
        p_fund = acct.get_position_by_id(date, security_id)
        self.assertIsNotNone(p_fund)
        self.assertEqual(date, p_fund.date)
        self.assertEqual(security_id, p_fund.security_id)
        self.assertEqual(1, p_fund.amount)
        self.assertEqual(today_close_price, p_fund.today_price)
        self.assertEqual(0.82, p_fund.get_value())

        # 当日策略result
        result = strategy.result
        self.assertIsNotNone(result)
        result_table = strategy.result.get_return_table()
        self.assertEqual(10.04, result_table.loc[date, '总资产'])
        self.assertEqual(0, result_table.loc[date, '当期收益率'])
        self.assertEqual(0.4, result_table.loc[date, '累计收益率'])
        self.assertEqual(1, result_table.loc[date, '交易次数'])

    def check_result(self, strategy):
        # 检查策略总结果

        # 策略result
        result = strategy.result
        self.assertIsNotNone(result)
        self.assertEquals(0.4, result.return_rate)
        self.assertEquals(10.04, result.value)
        self.assertEquals(10, result.total_capital_input)
        self.assertEquals(2, result.total_number_of_transactions)

    def check_exp_to_html(self, strategy):
        # 检查HTML文件导出的情况

        # html文件
        html_file_path = strategy.settings['html-exporter.path'] + strategy.settings['html-exporter.file_name']
        self.assertTrue(os.path.exists(html_file_path))

        # 图片文件夹
        pic_dir_path = html_file_path + ".assets"
        self.assertTrue(os.path.exists(pic_dir_path))
        # 收益图
        plot_pic_path = pic_dir_path + r'/fund_return_ratio.jpg'
        self.assertTrue(os.path.exists(plot_pic_path))


if __name__ == "__main__":
    # # 准备测试数据
    # data_api.FUND_DATA_DIR = r'test/equan_test/fund/fund_data/'
    # shutil.copy2(r'test/equan_test/fund/005918_backtesting_1.csv', r'test/equan_test/fund/fund_data/005918.csv')
    # # os.remove(r'test/equan_test/fund/fund_data/005918.csv')

    start_date = '2019-01-01'
    end_date = '2019-01-08'
    strategy = MyTestStrategy()
    strategy.start_date = start_date
    strategy.end_date = end_date
    strategy.set_unverise(FundUnverise(['005918']))    # 定义资产池
    # 策略运行
    strategy.run()

    # # 显示最终的acct收益率表
    # acct = strategy.get_context().get_account('基金定投账户')
    # print(acct.get_daily_return().tail())
    # # print(acct.get_daily_return().info())

    # # 策略的收益率明细：
    # print(strategy.result.get_return_table().tail())

    # 检查初始化的数据准备
    print(strategy.get_context().data['005918'])
