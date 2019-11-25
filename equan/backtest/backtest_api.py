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
import datetime
import equan.backtest.biz_tools as bt
from equan.backtest.tl import log


class StrategyCase:
    """
    策略的基类，每个策略都继承于这个类
    """

    # 全局变量：
    start = ''                       # 回测起始时间，yyyyMMdd格式
    end = ''                         # 回测结束时间，yyyyMMdd格式
    name = ''                        # 策略名称
    universe = None					 # 资产池
    benchmark = ''					 # str，事先算好的benchmark收益率数据
    freq = 'd'					     # 策略执行频率，目前只支持d日频率回测
    refresh_rate = 1				 # 执行handle_data的时间间隔，目前只支持int日期，不支持weekly、Monthly的写法

    accounts = {}					 # 账户的字典
    # 按账户名进行存放，如 'my_account' : Account(fdsafdsa)

    def initialize(self, context):
        """
        初始化策略运行环境(本函数必须被策略子类实现)

        Arguments:
            context {[type]} -- [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def handle_data(self, context):
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

    _accounts = {}
    _universe = None

    # 时间：
    now = None              # 当前时间, datetime格式
    today = None            # 当前日期, datetime格式
    previous_date = None    # 前一交易日, datetime格式

    def __init__(self, trade_datetime, accounts, universe):
        """
        初始化策略运行环境

        1. 账户dict引用
        2. 日期初始化
        3. 资产池按日初始化
        4. 账户的当日Position初始化

        Arguments:
            trade_datetime {[type]} -- [description]
            accounts {[type]} -- [description]
        """
        log.debug('初始化{0}的Context'.format(trade_datetime))
        # 初始化当天的日期
        self.now = datetime.datetime.strptime(
            trade_datetime+" 000000", bt.DATETIME_FORMAT)
        self.today = datetime.datetime.strptime(
            trade_datetime, bt.DATETIME_FORMAT.split(' ')[0])
        self.previous_date = datetime.datetime.strptime(
            bt.Trade_Cal.previous_date(trade_datetime), bt.DATETIME_FORMAT.split(' ')[0])

        # 资产池,根据日期，计算当日的资产列表
        self._universe = universe

        # 账户配置：

        # 头寸配置

        # TODO

    def get_account(self, account_name):
        """
        取得账户引用

        Returns:
            [type] -- [description]
        """

        try:
            return self._accounts[account_name]
        except Exception:
            return None

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

    ATYPE_Stock = 'STOCK'   # 账户类型：股票

    name = ''       # 账户名
    account_type = ''       # 账户类型
    capital_base = 0        # 初始资金
    _cash_account_balance = 0   # 现金账户余额
    # 暂不支持账户初始持仓的情况，默认持仓为空
    _position = {}  # 每日的所有仓位 {'20190101':Position对象, ...}
    _orders = {}    # 每日的所有订单

    def __init__(self, name, capital_base):
        self.name = name
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
        print('order in account')

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


class StockAccount(Account):
    """
    股票账户

    Arguments:
        Account {[type]} -- [description]
    """
    account_type = Account.ATYPE_Stock

    def __init__(self, name, capital_base):
        super().__init__(name, capital_base)

    def order(self, symbol, amount, order_type='close'):

        print('order in stock account')


class Position:
    """
    仓位信息

    Position(symbol: 601318.XSHG, amount: 100, cost: 34.649, profit: 33.3, value: 3498.2)

    """
    symbol = ''     # 资产编号
    trade_date = ''     # 交易日期

    profit = 0.0          # 持仓盈亏浮动 = (value - cost)*amount
    cost = 0.0            # 开仓成本
    value = 0.0           # 持仓市值
    amount = 0      # 持仓数量


class Order:
    """
    订单类

    买单：现金position --> 股票position
    卖单：股票position --> 现金position

    Order(order_id: 2017-01-03-0000001, order_time: 2017-01-03 09:30
    , symbol: 600000.XSHG, direction: 1, order_amount: 100
    , state: ORDER_SUBMITTED, filled_time: , filled_amount: 0
    , transact_price: 0.0000, slippage: 0.0000, commission: 0.0000)

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
    state = STATE_OPEN    # 订单状态
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


class Universe:
    """
    资产池基类
    """

    symbol_ids = []  # 资产编号集合

    def get_symbols(self, date):
        """
        取得某个时刻的资产id列表(本函数需要实现)

        Arguments:
            date {[type]} -- [description]
        """
        raise NotImplementedError


class StockUniverse(Universe):
    """
    动态股票资产池
    """

    def __init__(self, stock_list):
        self.symbol_ids = stock_list

    def get_symbols(self, date):
        # 静态池，不受到影响
        # FIXME 需要剔除当天停牌的股票
        return self.symbol_ids


class DynamicStockIndexUniverse(Universe):
    """
    动态 股票指数

    目前支持的指数：
    1. HS300    沪深300

    """

    def __init__(self, index_id="HS300", date=None):
        """

        Arguments:
            Universe {[type]} -- [description]
            index_id {[type]} -- [description]
            date     {datetime} -- 日期，指数
        """

        self.symbol_ids = index_id

    def get_symbols(self, date):
        # 静态池，不受到影响
        # FIXME 需要剔除当天停牌的股票
        return self.symbol_ids
