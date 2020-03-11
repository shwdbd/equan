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

测试案例2:

'''
from equan.fund.fund_backtesting import FundBackTester, Context
from equan.fund.fund_backtesting_impl import Account, FundUnverise, Order
import equan.fund.tl as tl
import unittest
import datetime
import equan.fund.data_api as data_api

log = tl.get_logger()


class MyTestStrategy(FundBackTester):

    def __init__(self):
        super().__init__()

        # 初始化账户
        fund_acct = Account('基金定投账户', initial_capital=10)
        self.get_context().add_account('基金定投账户', fund_acct)

        # 函数调用标识
        self.dates_of_date_handle = []  # 被调用过的日期

    def initialize(self):
        """
        1. 在account的数据中，增加一列星期几的字段
        2. 将data复制到self.initialize_data变量中，使得可以单元测试到
        """
        self.flag_of_initialize_called = True   # 证明函数被调用

        data_df = self.get_context().data['005918']
        data_df['week'] = data_df['date'].apply(lambda x: datetime.datetime.strptime(x, data_api.DATE_FORMAT).weekday()+1)
        self.testdata_init_datadf = data_df.copy()  # 生成检测用数据
        # print(self.testdata_init_datadf['week'])

    def date_handle(self, context):
        # 每日执行

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


class TestMyTestStrategy(unittest.TestCase):
    """测试最简单的回测逻辑
    """

    def test_normal(self):
        start_date = '2019-01-01'
        end_date = '2019-01-31'
        strategy = MyTestStrategy()
        strategy.start_date = start_date
        strategy.end_date = end_date
        strategy.set_unverise(FundUnverise(['005918']))    # 定义资产池
        # 策略运行
        strategy.run()

        # 检查：
        # 资产池：
        self.assertListEqual(['005918'], strategy.get_unverise().get_symbol())
        # context 和 account
        self.assertIsNotNone(strategy.get_context())
        self.assertIsNotNone(strategy.get_context().get_account('基金定投账户'))
        # TODO 检查data的准备，检查时间范围是否包括windows

        # 检查 initialize 是否被调用
        self.assertTrue(strategy.flag_of_initialize_called)

        # 检查 initialize 时候的数据
        # 在 initialize 中，策略新增了一列 星期 的数据
        self.assertEqual(5, strategy.testdata_init_datadf.loc['2019-01-04', 'week'])

        # 检查date_handle被调用情况
        dates = ['2019-01-02', '2019-01-03', '2019-01-04', '2019-01-07', '2019-01-08', '2019-01-09', '2019-01-10', '2019-01-11', '2019-01-14', '2019-01-15', '2019-01-16', '2019-01-17', '2019-01-18', '2019-01-21', '2019-01-22', '2019-01-23', '2019-01-24', '2019-01-25', '2019-01-28', '2019-01-29', '2019-01-30', '2019-01-31']
        self.assertListEqual(dates, strategy.dates_of_date_handle)

        acct = strategy.get_context().get_account('基金定投账户')
        # 检查下单的情况
        # 2019-01-03 当日的order: 下2手单，正常
        order_20190103 = acct.get_orders('2019-01-03')
        self.assertEqual(1, len(order_20190103))
        order_1 = order_20190103[0]
        self.assertIsNotNone(order_1)
        self.assertEqual('2019-01-03', order_1.date)
        self.assertEqual('005918', order_1.security_id)
        self.assertEqual(Order.DIRECTION_BUY, order_1.direction)
        self.assertEqual(2, order_1.order_amount)
        self.assertEqual(0.7997, order_1.order_price)  # 市价单
        self.assertEqual(2, order_1.turnover_amount)
        self.assertEqual(0.7997, order_1.turnover_price)    # 前一日价格成交
        self.assertEqual(Order.STATUS_SUCCESS, order_1.status)  # 该交易应该被交易成功
        # 2019-01-03 当日的position
        positions_20190103 = acct.get_position('2019-01-03')
        self.assertEqual(2, len(positions_20190103))    # 两个头寸，1个现金账户，1个资产账户
        # 现金账户，balance = 10-2*0.7997
        p_cash_20190103 = acct.get_position_by_id('2019-01-03', Account.CASH_SEC_ID)
        self.assertIsNotNone(p_cash_20190103)
        self.assertEqual('2019-01-03', p_cash_20190103.date)
        self.assertEqual(Account.CASH_SEC_ID, p_cash_20190103.security_id)
        self.assertEqual((10-2*0.7997), p_cash_20190103.amount)
        self.assertEqual(1, p_cash_20190103.today_price)
        self.assertEqual((10-2*0.7997), p_cash_20190103.get_value())
        # 资产账户
        p_fund_20190103 = acct.get_position_by_id('2019-01-03', '005918')
        self.assertIsNotNone(p_fund_20190103)
        self.assertEqual('2019-01-03', p_fund_20190103.date)
        self.assertEqual('005918', p_fund_20190103.security_id)
        self.assertEqual(2, p_fund_20190103.amount)
        self.assertEqual(0.7997, p_fund_20190103.today_price)
        self.assertEqual((2*0.7997), p_fund_20190103.get_value())

        # 2019-01-04 当日的order: 买100手单，失败，现金不足
        order_20190104 = acct.get_orders('2019-01-04')
        self.assertEqual(1, len(order_20190104))
        order_20190104 = order_20190104[0]
        self.assertIsNotNone(order_20190104)
        self.assertEqual('2019-01-04', order_20190104.date)
        self.assertEqual('005918', order_20190104.security_id)
        self.assertEqual(Order.DIRECTION_BUY, order_20190104.direction)
        self.assertEqual(100, order_20190104.order_amount)
        self.assertIsNone(order_20190104.order_price)  # 市价单
        self.assertEqual(0, order_20190104.turnover_amount)
        self.assertIsNone(order_20190104.turnover_price)    # 前一日价格成交
        self.assertEqual(Order.STATUS_FAILED, order_20190104.status)  # 交易失败
        self.assertEqual('现金账户余额不足', order_20190104.failed_messge)

        # 2019-01-07 当日的order: 卖10手单，失败，持有份额不足
        order_20190107 = acct.get_orders('2019-01-07')
        self.assertEqual(1, len(order_20190107))
        order_20190107 = order_20190107[0]
        self.assertIsNotNone(order_20190107)
        self.assertEqual('2019-01-07', order_20190107.date)
        self.assertEqual('005918', order_20190107.security_id)
        self.assertEqual(Order.DIRECTION_SELL, order_20190107.direction)
        self.assertEqual(-10, order_20190107.order_amount)
        self.assertIsNone(order_20190107.order_price)  # 市价单
        self.assertEqual(0, order_20190107.turnover_amount)
        self.assertIsNone(order_20190107.turnover_price)    # 前一日价格成交
        self.assertEqual(Order.STATUS_FAILED, order_20190107.status)  # 交易失败
        self.assertEqual('持有份数不足', order_20190107.failed_messge)

        # 2019-01-08 当日的order: 卖1手单，成功
        order_20190108 = acct.get_orders('2019-01-08')
        self.assertEqual(1, len(order_20190108))
        order_20190108 = order_20190108[0]
        self.assertIsNotNone(order_20190108)
        self.assertEqual('2019-01-08', order_20190108.date)
        self.assertEqual('005918', order_20190108.security_id)
        self.assertEqual(Order.DIRECTION_SELL, order_20190108.direction)
        self.assertEqual(-1, order_20190108.order_amount)
        self.assertEqual(0.8209, order_20190108.order_price)  # 市价单
        self.assertEqual(-1, order_20190108.turnover_amount)
        self.assertEqual(0.8209, order_20190108.turnover_price)    # 前一日价格成交
        self.assertEqual(Order.STATUS_SUCCESS, order_20190108.status)  # 交易成功
        self.assertEqual('', order_20190108.failed_messge)

        # 检查总的收益参数
        result = strategy.result
        self.assertIsNotNone(result)
        self.assertEqual(16.84, result.return_rate)
        self.assertEqual(2, result.total_number_of_transactions)
        self.assertEqual(10, result.total_capital_input)
        self.assertEqual(11.68, result.value)


if __name__ == "__main__":
    start_date = '2019-01-01'
    end_date = '2019-01-31'
    strategy = MyTestStrategy()
    strategy.start_date = start_date
    strategy.end_date = end_date
    strategy.set_unverise(FundUnverise(['005918']))    # 定义资产池

    # 运行
    strategy.run()

    # acct = strategy.get_context().get_account('基金定投账户')
    # print(acct.get_daily_return())
    # print(acct.return_ratio)
    # # 检查收益率
