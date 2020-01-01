#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   backtest_api.py
@Time    :   2019/11/25 10:09:13
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   回测API

主要类说明:
1. StrategyCase             策略基类
2. Context                  策略执行环境
3. Account, StockAccount    账户类，股票账户子类
4. Position                 头寸类
5. Order                    订单类
6. OrderState               订单状态
7. Universe, StockUniverse  资产池，股票资产池
8. DynamicStockIndexUniverse    动态股票资产池

'''
import equan.backtest.biz_tools as bt
from equan.backtest.tl import log, tushare


class BaseStrategy:
    """
    策略的基类，每个策略都继承于这个类
    """

    # 全局变量：
    name = '无名策略'                 # 策略名称
    start = ''                       # 回测起始时间，yyyyMMdd格式
    end = ''                         # 回测结束时间，yyyyMMdd格式
    universe = None					 # 资产池
    benchmark = 'HS300'			     # str，事先算好的benchmark收益率数据
    freq = 'd'					     # 策略执行频率，目前只支持d日频率回测
    refresh_rate = 1				 # 执行handle_data的时间间隔，目前只支持int日期，不支持weekly、Monthly的写法
    max_history_window = 100         # 回溯数据窗口（单位：天），默认100天

    _context = None                  # 运行环境

    accounts = {}					 # 账户的字典集合
    # 按账户名进行存放，如 'my_account' : Account(fdsafdsa)

    def initialize(self, context):
        """初始化策略运行环境(本函数必须被策略子类实现)

        Arguments:
            context {Context} -- 运行时环境

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

    def get_context(self):
        """返回运行环境

        Returns:
            [type] -- [description]
        """
        return self._context

    def set_context(self, the_context):
        """设置运行环境

        Arguments:
            the_context {[type]} -- [description]
        """
        self._context = the_context


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

    _strategy = None        # 对于策略对象的引用

    def __init__(self, strategy_obj):
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
        self._strategy = strategy_obj

        # 资产池,根据日期，计算当日的资产列表
        self._universe = strategy_obj.universe

        # 账户配置：
        self._accounts = strategy_obj.accounts
        for acct in self.get_accounts():
            acct.set_context(self)

        # 日期初始化：
        self.now = ""
        self.today = ""
        self.previous_date = ""

    def get_strategy(self):
        """
        返回策略对象
        """
        return self._strategy

    def set_date(self, day_str):
        """
        设置环境日期

        Arguments:
            trade_datetime {[type]} -- yyyyMMdd格式日期字符串
        """
        # 初始化当天的日期
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

    def get_universe(self, date=None):
        """
        取得资产池

        Returns:
            [type] -- [description]
        """
        if date is None:
            date = self.today
        return self._universe.get_symbols(date)

    def make_deal(self):
        """
        撮合今天交易
        """
        # 1. 找出所有账户、所有OPEN状态的Order
        # 2. 进行购买/卖出操作（操作Poistion和Cash）
        # 3. 设置Order的状态
        # rule1： 如果现金不足，则全单失败！
        # END

        log.debug('[{0}]开始{1}的交易撮合'.format(
            self.get_strategy().name, self.today))
        for acct in self.get_accounts():
            log.debug('[{0}]撮合账户{1}:'.format(
                self.get_strategy().name, acct.name))
            open_orders = acct.get_orders(state=OrderState.OPEN)
            for order in open_orders:
                # 按账户进行撮合
                # 交易金额
                order_capital = order.order_price * order.order_amount
                # log.debug('成交金额 = {0}, 成交价格={1}'.format(
                #     order_capital, order.order_price))
                # 做多时检查现金账户余额是否足够：
                if order.direction == Order.ORDER_LONG and acct.get_cash() < order_capital:
                    log.debug('现金不足，订单撤销！')
                    order.state_message = '现金不足({0}<{1})，订单撤销！'.format(
                        acct.get_cash(), order_capital)
                    order.state = OrderState.CANCELED  # 更新order的状态
                elif order.direction == Order.ORDER_SHORT and (acct.get_position(order.symbol).available_amount < order.order_amount):
                    # 做空时，仓中股票数量不足的情况
                    log.debug('账户中股票不足可卖出数量，订单撤销！')
                    order.state_message = '持有股票数量不足({0}<{1})，订单撤销！'.format(
                        acct.get_position(order.symbol).available_amount, order.order_amount)
                    order.state = OrderState.CANCELED  # 更新order的状态
                else:
                    # 交易成功
                    log.debug('订单{0} 买卖 {1} {2}份'.format(
                        order.order_id, order.symbol, order.order_amount))

                    # TODO 此处要实现 事务处理
                    # 现金账户扣减
                    acct.update_cash(-1 * (order.direction * order_capital))
                    # 得到Position账户
                    position = acct.get_position(order.symbol)
                    if not position:
                        position = Position(symbol=order.symbol)
                        acct.get_positions()[order.symbol] = position

                    position = acct.get_positions()[order.symbol]
                    position.change(
                        direct=order.direction, the_amount=order.order_amount, the_price=order.order_price)

                    # 交易成功,更新order的filled_amount
                    order.filled_amount = order.order_amount    # 订单成交数量
                    order.state = OrderState.FILLED

    def finish_tick(self):
        """
        回测周期结束处理

        - 头寸转历史
        - 策略效果计算
        
        """


class Account:
    """
    账户类
    """

    ATYPE_STOCK = 'STOCK'           # 账户类型：股票

    name = ''                       # 账户名
    account_type = ''               # 账户类型
    capital_base = 0                # 初始资金
    _cash = 0                       # 现金账户余额
    # 暂不支持账户初始持仓的情况，默认持仓为空
    _positions = {}                 # 每个资产的持仓情况 {'600016':Position对象, ...}
    _orders = []                    # 每日的所有订单，Order对象列表
    _context = None                 # 对环境的引用
    _total_value = 0.0              # 总价值

    def __init__(self, name, capital_base):
        self.name = name
        self.capital_base = capital_base
        self._cash = self.capital_base  # 现金账户余额初始化
        self._positions = {}
        self._orders = []
        self._context = None
        self._total_value = 0.0

    def get_value(self):
        """
        返回账户总市价
        """
        total_value = 0
        for symbol, position in self.get_positions().items():
            total_value += position.value

        return self.get_cash() + total_value

    def set_context(self, context):
        self._context = context

    def get_context(self):
        return self._context

    def get_cash(self):
        """
        返回当前现金账户余额
        """
        return self._cash

    def update_cash(self, volume):
        self._cash = self._cash + volume

    def get_positions(self):
        """
        取得所有的持仓头寸

        Returns:
            [type] -- [description]
        """
        return self._positions

    def get_position(self, symbol_id):
        """
        按资产编号返回某日头寸

        Returns:
            [type] -- [description]
        """

        if symbol_id not in self._positions.keys():
            position = Position(symbol=symbol_id)
            self.get_positions()[symbol_id] = position
        return self._positions[symbol_id]

    def get_orders(self, state=None):
        """
        返回账户所有订单，返回list

        默认返回所有状态的order
        """
        if state is None:
            return self._orders
        else:
            order_list = []
            for o in self._orders:
                if o.state == state:
                    order_list.append(o)
            return order_list

    def get_order(self, order_id=None):
        """根据订单号返回订单对象

        Arguments:
            order_id {str} -- 订单号
        """
        for o in self._orders:
            if o.order_id == order_id:
                return o

    def order(self, symbol, amount, order_type):
        """
        下单动作
        - 仅下单，不完成交易
        - 目前仅支持市价单（即按市场价成交）


        order_type = '1/-1' 交易方向，即买卖
        amount 交易手术，必须是100的整数或者0

        Arguments:
            symbol {str} -- 资产编号，必须在回测资产池范围内
            amount {int} -- 交易数量
            order_type {int} -- 交易方向，多头或空头

        Returns:
            [Order对象] -- 下单成功返回对象，否则抛出不同的异常
        """
        raise NotImplementedError

    def order_pct(self, symbol, pct):
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
    """
    account_type = Account.ATYPE_STOCK

    def __init__(self, name, capital_base):
        super().__init__(name, capital_base)
        self.account_type = Account.ATYPE_STOCK

    def order(self, symbol, amount, order_type):
        """[summary]
        股票下单

        - 必须按"手"为单位下单

        Arguments:
            symbol {[type]} -- [description]
            amount {[type]} -- [description]
            order_type {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        log.debug('股票账户{0}下单'.format(self.name))

        order = Order(symbol, self)
        try:
            if amount != 0 and amount % 100 != 0:
                # 检查amount是否是100的倍数或是0，否则订单状态就是 REJECTED
                order.state = OrderState.REJECTED
                order.state_message = '股票单交易数量必须以100为单位(amount={0})'.format(
                    amount)
            elif symbol not in self.get_context().get_universe():
                # 检查symbol是否在资产池中，不在则状态为  REJECTED
                order.state = OrderState.REJECTED
                order.state_message = '股票{0}不在可交易的资产池中，不能下单'.format(symbol)
            else:
                # 正常下单:
                order.order_amount = amount
                order.direction = order_type
                if order.direction:
                    order.offset_flag = 'open'
                else:
                    order.offset_flag = 'close'

                # 按当日open价格计算委托价格
                # TODO 考虑数据取不到的情况
                # TODO 取数据要简化
                open_price = float(tushare.daily(
                    ts_code='600016.SH', trade_date=self.get_context().today)['open'])
                order.order_price = open_price

                # TODO ？怎么判断，开平仓标识
                order.state = OrderState.OPEN

        except Exception as sys_e:
            order.state = OrderState.ERROR
            order.state_message = '系统异常:' + str(sys_e)
        finally:
            self._orders.append(order)
            return order

        return order


class Position:
    """
    资产持仓情况

    amount (price) value_change   |cost     value   profit
    100    1       100             1*100    100     0
    100    2       200             300      400     400-300=100


    """
    symbol = ''             # 资产编号
    amount = 0              # 当前持仓数量
    available_amount = 0    # 可卖出持仓数量
    cost = 0.0              # 平均开仓成本
    value = 0.0             # 当前持仓市值（随市场价格变动）
    profit = 0.0            # 累计持仓盈亏浮动 = (value - cost)

    def __init__(self, symbol):
        self.symbol = symbol
        self.amount = 0              # 持仓数量
        self.available_amount = 0    # 可卖出持仓数量
        self.profit = 0.0            # 累计持仓盈亏浮动
        self.cost = 0.0              # 平均开仓成本
        self.value = 0.0             # 持仓市值（随市场价格变动）
        self.change(1, 0, 0)

    def change(self, direct, the_amount, the_price):
        """
        仓位变动

        仓位变动后，有几个属性会随之改变：
        1. amount、available_amount 和 value
        2. profit = value / amount

        Arguments:
            direct {int} -- 仓位变动方向，1多头，-1空头
            the_amount {int} -- 此次买卖的头寸数量
            the_cost {float} -- 此次买卖头寸价格，买入卖出的价格

        amount (price) value_change   |cost     value   profit
        100    1       100             1*100    100     0
        100    2       200             300      400     400-300=100
        -100   1                       200      100     -100
        """
        self.amount = self.amount + direct * the_amount
        self.available_amount = self.amount
        self.value = self.amount * the_price    # 市场价

        # 平均成本：
        self.cost = self.cost + direct * (the_amount*the_price) # TODO 计算错误，应是每单位的买入价格
        # 收益
        self.profit = self.value - self.cost

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
        str_arr = ', '.join(
            ['%s=\'%s\'' % item for item in self.__dict__.items()])
        return "Order({0})".format(str_arr)


class Universe:
    """
    资产池基类
    """

    _symbol_ids = []  # 资产编号集合

    def get_symbols(self, date):
        """
        取得某个时刻的资产id列表(本函数需要实现)

        Arguments:
            date {[type]} -- [description]
        """
        raise NotImplementedError


class StockUniverse(Universe):
    """
    静态股票资产池
    """

    def __init__(self, stock_list):
        self._symbol_ids = stock_list

    def get_symbols(self, date):
        """[summary]

        Arguments:
            date {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        # FIXME 需要剔除当天停牌的股票（下一个版本考虑）
        return self._symbol_ids


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
