#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   backtest_api.py
@Time    :   2019/11/25 10:09:13
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   回测API
'''

# here put the import lib


class StrategyCase:
    """
    策略的基类，每个策略都继承于这个类
    """

    # 全局变量：
    start = ''                       # 回测起始时间，yyyyMMdd格式
    end = ''                         # 回测结束时间，yyyyMMdd格式
    universe = None					 # 资产池
    benchmark = ''					 # str，事先算好的benchmark收益率数据
    freq = 'd'					     # 策略执行频率，目前只支持d日频率回测
    refresh_rate = 1				 # 执行handle_data的时间间隔，目前只支持int日期，不支持weekly、Monthly的写法

    accounts = {}					 # 账户的字典
    # 按账户名进行存放，如 'my_account' : Account(fdsafdsa)

    def initialize(context):
        """
        初始化策略运行环境(本函数必须被策略子类实现)

        Arguments:
            context {[type]} -- [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def handle_data(context):
        """
        核心策略逻辑在此处实现

        Raises:
            NotImplementedError: [description]
        """

        raise NotImplementedError


class Context:
    """
    策略运行环境类
    """

    _data = {}   # SAT模式的数据集合

    _accounts = None
    _universe = None

    def now(self):
        """
        获取策略运行时的当前时刻，如2017-01-04 09:30:00

        Returns:
            [datetime] -- [description]
        """
        # TODO 待实现
        return ''

    def current_date(self):
        """
        获取策略运行时的当前日期，如2017-01-04 09:30:00

        Returns:
            [datetime] -- [description]
        """
        # TODO 待实现
        return ''

    def previous_date(self):
        """
        获取当前回测日期的前一交易日，如2017-01-04 09:30:00

        Returns:
            [datetime] -- [description]
        """
        # TODO 待实现
        return ''

    def get_account(self, account_name):
        """
        取得账户引用

        Returns:
            [type] -- [description]
        """
        return self._accounts[account_name]

    def get_accounts(self):
        """
        取得账户引用

        Returns:
            [type] -- [description]
        """
        return self._accounts

    def get_universe(self):
        """
        取得资产池

        Returns:
            [type] -- [description]
        """
        return self._universe

    def get_history(symbol, attribute, time_range, freq='1d', style='sat', rtype='frame'):
        """获取历史数据

        - 只返回 context.previous_date 之前日期的数据（含previous_date）
        - attribute 返回的字段可以有：open, close
        - style类似优矿，有三种模式可以返回选择


        Arguments:
            symbol {[type]} -- [description]
            attribute {[type]} -- [description]
            time_range {int} -- 返回之前N天的数据

        Keyword Arguments:
            freq {str} -- [description] (default: {'1d'})
            style {str} -- [description] (default: {'sat'})
            rtype {str} -- [description] (default: {'frame'})
        """
        # TODO 待实现
        pass


class Account:
    """
    账户类
    """

    account_name = ''       # 账户名
    account_type = 'stock'  # 账户类型
    capital_base = 0        # 初始资金
    _cash_account_balance = 0   # 现金账户余额
    # 暂不支持账户初始持仓的情况，默认持仓为空
    _position = {}  # 每日的所有仓位 {'20190101':Position对象, ...}
    _orders = {}    # 每日的所有订单

    def __init__(self, name, capital_base):
        self.account_name = name
        self.capital_base = capital_base
        self._cash_account_balance = self.capital_base  # 现金账户余额初始化

    def order(self, symbol, amount, order_type):
        """
        下单

        order_type = 'open/close' 按当前开盘价或收盘价交易
        amount 交易手术，必须是100的整数或者0
        """
        # 1. 生成一个Order对象
        # 2. 默认下单全部成交，然后更新cash信息

        # TODO 待实现
        pass

    def order_pct(symbol, pct):
        """
        根据当前账户总资产，进行策略订单委托下单指定百分比的股票仓位。

        Arguments:
            symbol {[type]} -- [description]
            pct {[type]} -- [description]
        """
        # TODO 待实现
        pass

    # 清除所有的持仓
    def close_all_positions(self):
        # TODO 待实现
        pass


class Position:
    """
    仓位信息
    """
    symbol = ''     # 资产编号
    trade_date = ''     # 交易日期

    profit = 0.0          # 持仓盈亏浮动 = value - cost
    cost = 0.0            # 开仓成本
    value = 0.0           # 持仓市值
    amount = 0      # 持仓数量


class Order:
    """
    订单类



    """

    # 订单状态：
    STATE_OPEN = 0  # 待成交
    STATE_FILLED = 100  # 全部成交
    STATE_CANCELED = -1  # 撤销
    order_id = ''       # 订单编号
    symbol = ''         # 资产编码
    order_time = None   # datetime，下单时间
    order_amount = 0    # 委托数量
    order_price = 0.00  # 委托价格
    state = Order.STATE_OPEN    # 订单状态
    direction = 0       # 买卖方向
    offset_flag = ''    # 开平仓标识， open为开仓，close为关仓

    state_message = ''  # 订单状态描述，如拒单原因


class OrderDealer:
    """
    订单撮合
    """

    def deal_order(account):
        # TODO 待实现
        pass
