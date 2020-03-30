#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_backtesting_2_html.py
@Time    :   2020/03/27 11:38:24
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基金回测框架，测试结果HTML输出

'''
from equan.fund.fund_backtesting import FundBackTester
from equan.fund.fund_backtesting_impl import Account, FundUnverise
import equan.fund.tl as tl
import datetime

log = tl.get_logger()


class MyTestStrategy(FundBackTester):
    """测试用策略
    周一，买入1手
    周五，卖出1手
    """

    def __init__(self):
        super().__init__()

        # 初始化账户
        fund_acct = Account('基金账户', initial_capital=10)
        self.get_context().add_account('基金账户', fund_acct)

        # # 资产池
        # self.set_unverise(FundUnverise(['005918']))    # 定义资产池

    def initialize(self):
        """
        1. 在account的数据中，增加一列星期几的字段
        2. 将data复制到self.initialize_data变量中，使得可以单元测试到
        """
        # 星期数据的计算
        df = self.get_context().data['005918']
        df['星期'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').weekday()+1)
        pass

    def date_handle(self, context):
        # 每日执行
        # 查看每日的数据
        today = context.today
        df = self.get_context().data['005918']
        acct = context.get_account('基金账户')
        week = df.loc[context.today, '星期']
        print(today + ' : ' + str(week))
        if week == 1:   # 周一
            # 下单买入
            order_price = df.loc[today, 'price']   # 按当日价格买入
            acct.order(date=today, securiy_id='005918', amount=1, price=order_price)
            print('{0} 买入 {1} 份 {2}'.format(today, 1, order_price))
        elif week == 5:     # 周五
            # 下单卖出
            order_price = df.loc[today, 'price']   # 按当日价格买入
            acct.order(date=today, securiy_id='005918', amount=-1, price=order_price)
            print('{0} 卖出 {1} 份 {2}'.format(today, 1, order_price))


if __name__ == "__main__":
    # 开始回测：
    start_date = '2019-01-01'
    end_date = '2019-01-08'
    strategy = MyTestStrategy()
    strategy.start_date = start_date
    strategy.end_date = end_date
    strategy.set_unverise(FundUnverise(['005918']))    # 定义资产池
    # 修改输出参数:
    strategy.settings['html-exporter.file_name'] = 'my_str.html'
    # 策略运行
    strategy.run()
