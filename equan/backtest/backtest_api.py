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
import time
import equan.backtest.biz_tools as bt
from equan.backtest.tl import log, tushare
import pandas as pd


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
    max_history_window = 100         # 回溯数据窗口（单位：天），默认100天

    accounts = {}					 # 账户的字典集合
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
    now = None              # 当前时间, str(yyyyMMdd HHmmSS)格式
    today = None            # 当前日期, str(yyyyMMdd)格式
    previous_date = None    # 前一交易日, str(yyyyMMdd)格式

    def __init__(self, accounts, universe):
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
        log.debug('初始化Context')

        # 资产池,根据日期，计算当日的资产列表
        self._universe = universe

        # 账户配置：
        self._accounts = accounts
        for acct in self.get_accounts():
            acct.set_context(self)

        # 日期初始化：
        self.now = ""
        self.today = ""
        self.previous_date = ""

    def set_date(self, day_str):
        """
        设置环境日期

        Arguments:
            trade_datetime {[type]} -- yyyyMMdd格式日期字符串
        """
        # 初始化当天的日期
        # TODO 待单元测试
        self.now = day_str + " 000000"
        self.today = day_str
        self.previous_date = bt.Trade_Cal.previous_date(day_str)

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
        取得账户引用，返回账户列表（非dict）

        Returns:
            [type] -- [description]
        """
        acct_list = []
        for acct_name in self._accounts:
            acct_list.append(self.get_account(acct_name))
        return acct_list

    def get_universe(self, date):
        """
        取得资产池

        Returns:
            [type] -- [description]
        """
        return self._universe.get_symbols(date)

    def get_history(self, symbol, fields, time_range=1, freq='1d', style='sat', rtype='frame'):
        """获取历史数据

        - 只返回 context.previous_date 之前日期的数据（含previous_date）
        - attribute 返回的字段可以有：open, close
        - style类似优矿，有三种模式可以返回选择

        """
        data = {}
        if style.upper() == 'TAS':
            # DSA模式，key=日期, index是symbol, col是参数
            # TODO 日期转成datetime yyyyMMdd格式
            date_list = pd.date_range(end='20190101', periods=time_range)
            for day in date_list:
                print(type(day))
                data[str(day)] = pd.DataFrame()  # TODO 日期转成datetime格式

            # tushare.daily( ts_code='', trade_date='', fields=attribute)    # 多个要合并

        print(data)

        # TODO 待实现
        pass


class Account:
    """
    账户类
    """

    ATYPE_Stock = 'STOCK'           # 账户类型：股票
    name = ''                       # 账户名
    account_type = ''               # 账户类型
    capital_base = 0                # 初始资金
    _cash = 0                       # 现金账户余额
    # 暂不支持账户初始持仓的情况，默认持仓为空
    _positions = {}                 # 每个资产的持仓情况 {'600016':Position对象, ...}
    _orders = []                    # 每日的所有订单，Order对象列表
    _context = None                 # 对环境的引用

    def __init__(self, name, capital_base):
        self.name = name
        self.capital_base = capital_base
        self._cash = self.capital_base  # 现金账户余额初始化

    def set_context(self, context):
        self._context = context

    def get_context(self):
        return self._context

    def get_cash(self):
        """
        返回当前现金账户余额
        """
        return self._cash

    def get_positions(self):
        """
        取得所有的持仓头寸

        Returns:
            [type] -- [description]
        """
        return self._positions

    def get_position(self, date):
        """
        按日期返回某日头寸

        Returns:
            [type] -- [description]
        """
        return self._positions[date]

    def get_orders(self):
        """
        返回账户所有订单，返回list
        """
        return self._orders

    def order(self, symbol, amount, order_type):
        """
        下单动作
        - 仅下单，不完成交易
        - 目前仅支持市价单（即按市场价成交）


        order_type = 'open/close' 按当前开盘价或收盘价交易
        amount 交易手术，必须是100的整数或者0

        Arguments:
            symbol {str} -- 资产编号，必须在回测资产池范围内
            amount {int} -- 交易数量
            order_type {int} -- 交易方向，多头或空头

        Returns:
            [Order对象] -- 下单成功返回对象，否则抛出不同的异常
        """
        # EFFECTS:
        # 1. 参数检查（检查symbol、order_type有效性、检查amount是否满足手的单位要求）
        # 2. 生成order对象
        # END

        # TODO 待实现
        raise NotImplementedError

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
        """
        卖出所有持仓资产
        """

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

    def order(self, symbol, amount, order_type):
        """[summary]
        
        Arguments:
            symbol {[type]} -- [description]
            amount {[type]} -- [description]
            order_type {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        log.debug('股票账户下单')
        # 参数检查：
        # 1. TODO 检查symbol是否在资产池中

        order = Order(symbol, self)
        try:
            # TODO 检查amount是否是100的倍数或是0，否则订单状态就是 REJECTED
            if amount != 0 and amount % 100 != 0:
                order.state = OrderState.REJECTED
                order.state_message = '股票单 交易数量 必须以100为单位'
            else:
                order.order_amount = amount
                order.direction = order_type
                if order.direction:
                    order.offset_flag = 'open'
                else:
                    order.offset_flag = 'close'

                # 按当日open价格计算委托价格
                # TODO 考虑数据取不到的情况
                # TODO 取数据要简化
                open_price = float(tushare.daily(ts_code='600016.SH', trade_date=self.get_context().today)['open'])
                order.order_price = open_price
                
                # TODO ？怎么判断，开平仓标识
                order.state = OrderState.OPEN

        except Exception as sys_e:
            order.state = OrderState.ERROR
            order.state_message = '系统异常:' + str(sys_e)
        finally:
            return order

        return order


class Position:
    """
    资产持仓情况

    Position(symbol: 601318.XSHG, amount: 100, cost: 34.649, profit: 33.3, value: 3498.2)

{'000425.XSHE': 
  Position(symbol: 000425.XSHE, amount: 200, available_amount: 200, cost: 3.37, profit: 4.0, value: 678.0)}

    """
    symbol = ''             # 资产编号
    trade_date = ''         # 持仓日期

    amount = 0              # 持仓数量
    available_amount = 0    # 可卖出持仓数量
    profit = 0.0            # 累计持仓盈亏浮动 = (value - cost)*amount
    cost = 0.0              # 平均开仓成本
    value = 0.0             # 持仓市值（随市场价格变动）

    def __init__(self, symbol, trade_date=trade_date):
        self.symbol = symbol
        self.trade_date = trade_date
        self.amount = 0              # 持仓数量
        self.available_amount = 0    # 可卖出持仓数量
        self.profit = 0.0            # 累计持仓盈亏浮动 = (value - cost)*amount
        self.cost = 0.0              # 平均开仓成本
        self.value = 0.0             # 持仓市值（随市场价格变动）

    def __str__(self):
        """返回一个对象的描述信息"""
        str_arr = ', '.join(['%s=%s' % item for item in self.__dict__.items()])
        return "Position({0})".format(str_arr)


class OrderState:
    """
    订单状态

    # >0 为成功单; <0为失败单；=0 待成交单
    """
    OPEN = 0          # 待成交
    FILLED = 100      # 全部成交
    CANCELED = -1     # 撤销
    ERROR = -9999     # 系统错误，若模拟异常、线路中断等
    REJECTED = -4     # 订单被交易所拒绝


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
    # 订单类型
    ORDER_LONG = 1          # 订单类型：做多，买入
    ORDER_SHORT = -1        # 订单类型：做空，卖出

    # 属性：
    order_id = ''               # 订单编号(样式：000001)
    symbol = ''                 # 资产编码
    order_time = None           # datetime，下单时间
    order_amount = 0            # 委托数量
    filled_amount = 0           # 成交数量
    order_price = 0.00          # 委托价格
    state = OrderState.OPEN     # 订单状态
    direction = 0               # 买卖方向, 1买,-1卖
    offset_flag = ''            # 开平仓标识， open为开仓，close为关仓
    state_message = ''          # 订单状态描述，如拒单原因
    _account = None             # 隶属账户的引用

    def __init__(self, symbol=symbol, account=None):
        # 生成order_id
        self.order_id = (str(len(account.get_orders())+1)
                         ).zfill(6)               # 订单编号(从1开始，顺序编号)
        self.symbol = symbol                 # 资产编码
        self._account = account

        self.order_time = account.get_context().now          # datetime，下单时间
        self.order_amount = 0            # 委托数量
        self.filled_amount = 0           # 成交数量
        self.order_price = 0.00          # 委托价格
        self.state = OrderState.OPEN     # 订单状态
        self.direction = 0               # 买卖方向
        self.offset_flag = ''            # 开平仓标识， open为开仓，close为关仓
        self.state_message = ''          # 订单状态描述，如拒单原因

    def get_account(self):
        return self._account

    def __str__(self):
        """返回一个对象的描述信息"""
        str_arr = ', '.join(['%s=\'%s\'' % item for item in self.__dict__.items()])
        return "Order({0})".format(str_arr)


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
