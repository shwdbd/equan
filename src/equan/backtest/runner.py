#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   runner.py
@Time    :   2019/11/25 10:07:17
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   回测框架执行接口
'''
import equan.backtest.backtest_api as api
# import equan.backtest.biz_tools as bt
from equan.backtest.tl import log
import equan.backtest.constant as CONSTANT
import pandas as pd


class StrategyRunner:
    """
    策略回测执行类
    """

    @staticmethod
    def back_test_run(case_obj):
        # 运行策略实例

        # 检查策略实现对象的合法性
        if not case_obj or not issubclass(type(case_obj), api.BaseStrategy):
            log.error('策略实例为空或不是基策略的实例！')
            log.error('策略运行终止！')
            return

        log.info('[{0}] 开始运行策略 '.format(case_obj.name))
        # 初始化context
        context = api.Context(case_obj)
        case_obj.set_context(context)

        # 策略初始化
        log.debug('[{0}] 调用initialize函数'.format(case_obj.name))
        case_obj.initialize(context)
        # 根据参数，获得所有的交易日进行循环
        for day in context.get_ticks():
            # 按日初始化context对象（调整日期，调整可访问的数据）
            context.set_date(day)

            # 策略逻辑处理
            log.debug('[{0}]{1}策略代码执行'.format(case_obj.name, day))
            case_obj.handle_data(context)

            # 订单撮合
            StrategyFrame.make_deal(context)

            # 统计汇总
            StrategyFrame.finish_tick(context)

            # 发送交易信号微信等
        # 所有日期策略执行结束后，统计输出策略结果

        log.info('[{0}] 策略运行结束 '.format(case_obj.name))

        # 结果导出
        exp = LogExportor()
        exp.export(context)


class StrategyResult:
    """
    策略结果存放数据

    TODO 对context对象的引用
    TODO 开发add函数
    TODO get_xxx函数
    TODO 建立策略参数的数据结构，包括初始化
    TOOD 建立取 return, acct, position, order的查询函数

    TODO 单元测试：新建数据结构
    TODO 单元测试：add函数调用（包括新增失败、数据覆盖场景）
    TODO 单元测试：查询函数（包括带和不带条件）

    """
    _parameter = None       # 策略参数
    _context = None         # 对context的引用

    _df_return = None       # 策略收益 数据集
    _df_account = None      # 账户 数据集
    _df_position = None     # 头寸 数据集
    _df_order = None        # 订单 数据集

    # 策略收益 数据集结构
    _return_columns = {
        'tick': {'type': 'str', 'label': '日期'},
        'value': {'type': 'float', 'label': '市价'},
        'return': {'type': 'float', 'label': '当期收益率	'},
        'cum_return': {'type': 'float', 'label': '累计收益率'},
        'bm_return': {'type': 'float', 'label': '基准当期收益率'},
        'bm_cum_return': {'type': 'float', 'label': '基准累计收益率'},
    }

    # 账户 数据集结构
    _account_columns = {
        'tick': {'type': 'str', 'label': '日期'},
        'name': {'type': 'str', 'label': '账户名'},
        'value': {'type': 'float', 'label': '市价'},
        'return': {'type': 'float', 'label': '当期收益率'},
        'cum_return': {'type': 'float', 'label': '累计收益率'},
    }

    # 头寸 数据集结构
    _position_columns = {
        'tick': {'type': 'str', 'label': '日期'},
        'acct_name': {'type': 'str', 'label': '账户名'},
        'symbol': {'type': 'str', 'label': '资产名'},
        'amount': {'type': 'int', 'label': '持有数量'},
        'available_amount': {'type': 'int', 'label': '可卖出数量'},
        'value': {'type': 'float', 'label': '市值'},
        'price': {'type': 'float', 'label': '市价'},
    }

    # 订单 数据集结构
    _order_columns = {
        'order_id': {'type': 'str', 'label': '订单编号'},
        'name': {'type': 'str', 'label': '账户名'},
        'symbol': {'type': 'str', 'label': '资产名'},
        'ordr_time': {'type': 'str', 'label': '下单时间'},
        'order_amount': {'type': 'int', 'label': '委托数量'},
        'filled_amount': {'type': 'int', 'label': '成交数量'},
        'order_price': {'type': 'float', 'label': '委托价格'},
        'filled_price': {'type': 'float', 'label': '成交价格'},
        'state': {'type': 'str', 'label': '状态'},
        'state_label': {'type': 'str', 'label': '状态中文'},
        'state_message': {'type': 'str', 'label': '订单描述'},
        'direction': {'type': 'int', 'label': '订单方向'},
        'offset_flag': {'type': 'str', 'label': '开仓/平仓标识'},
    }

    def __init__(self, context):
        """
        初始化
        """
        self._context = context

        # 初始化策略参数
        self._parameter = {
            'start': context.start,
            'end': context.end,
            'universe': str(context.universe),
            'benchmark': str(context.benchmark),
        }

        # 初始化 策略收益 数据集
        self._df_return = self._init_dataframe(self._df_return, self._return_columns)

        # 初始化 账户 数据集
        self._df_account = self._init_dataframe(self._df_account, self._account_columns)

        # 初始化 头寸 数据集
        self._df_position = self._init_dataframe(self._df_position, self._position_columns)

        # 初始化 订单 数据集
        self._df_order = self._init_dataframe(self._df_order, self._order_columns)

    def _init_dataframe(self, dataframe, define_dict):
        dtypes = {}
        for field in define_dict.keys():
            dtypes[field] = define_dict[field]['type']
        # print(dtypes)
        dataframe = pd.DataFrame(columns=list(define_dict.keys()))
        dataframe = dataframe.astype(dtypes)
        # print(self._df_account.info())
        return dataframe

    def _get_columns_types(self, define_dict):
        dtypes = {}
        for field in define_dict.keys():
            dtypes[field] = define_dict[field]['type']
        return dtypes

    def get_context(self):
        return self._context

    def get_returns(self):
        """返回所有策略收益情况

        Returns:
            [dataframe] -- 数据集
        """
        return self._df_return

    def get_return(self):
        """返回最终日策略收益情况

        Returns:
            [dataframe] -- 数据集，仅一条记录
        """
        return self._df_return.loc[-1: []]

    def add(self, data_type, data_dict):
        """添加数据

        Arguments:
            data_type {[type]} -- [description]
            data_dict {[type]} -- [description]
        """
        # TODO 待实现，实现通用添加数据功能，待数据覆盖更新
        return data_dict


class StrategyResultExportor:
    """
    策略结果导出基类
    """

    def export(self, context):
        """
        策略结果导出
        """
        pass


class LogExportor(StrategyResultExportor):
    """
    日志结果展示
    """

    def export(self, context):
        """
        策略结果导出
        """
        data = context.get_strategy_data()
        log.info('='*30)
        log.info('{0} 策略执行结果:'.format(context.get_strategy().name))
        log.info('-'*30)
        log.info('账户[数量:{0}]:'.format(len(context.get_accounts())))
        log.info('-'*30)
        for acct in context.get_accounts():
            log.info('账户 {0}]:'.format(acct.name))
            log.info(data['accounts'])
            # for p in acct.get_positions():
            #     log.info('-'*15)
            #     log.info()

        df_order = data['orders']
        log.info('Order[数量:{0}]:'.format(df_order.shape[0]))
        log.info(df_order)
        # log.info('-'*30)

        log.info('-'*30)

        log.info('='*30)


class StrategyFrame:

    @staticmethod
    def make_deal(context):
        """
        撮合当日交易
        """
        # 1. 找出所有账户、所有OPEN状态的Order
        # 2. 进行购买/卖出操作（操作Poistion和Cash）
        # 3. 设置Order的状态
        # rule1： 如果现金不足，则全单失败！
        # END

        log.debug('[{0}]开始 {1} 的交易撮合'.format(
            context.get_strategy().name, context.today))
        for acct in context.get_accounts():
            open_orders = acct.get_orders(state=api.OrderState.OPEN)
            if len(open_orders) == 0:
                log.debug('[{0}]撮合账户 {1} ，无订单'.format(
                    context.get_strategy().name, acct.name))
            else:
                log.debug('[{0}]撮合账户 {1} ，{2} 个订单'.format(
                    context.get_strategy().name, acct.name, len(open_orders)))
                for order in open_orders:
                    order_capital = order.order_price * order.order_amount  # 交易金额
                    # print('order_capital = ' + str(order_capital))

                    log.debug('撮合订单 {0}'.format(order))
                    if order.direction == api.Order.ORDER_LONG and acct.get_cash() < order_capital:
                        # 做多时检查现金账户余额是否足够：
                        log.debug('现金不足，订单撤销！')
                        order.state_message = '现金不足({0}<{1})，订单撤销！'.format(
                            acct.get_cash(), order_capital)
                        order.state = api.OrderState.CANCELED  # 更新order的状态
                    elif order.direction == api.Order.ORDER_SHORT and (acct.get_position(order.symbol).available_amount < order.order_amount):
                        # 做空时，仓中股票数量不足的情况
                        log.debug('账户中股票不足可卖出数量，订单撤销！')
                        order.state_message = '持有股票数量不足({0}<{1})，订单撤销！'.format(
                            acct.get_position(order.symbol).available_amount, order.order_amount)
                        order.state = api.OrderState.CANCELED  # 更新order的状态
                    else:
                        # 成功撮合：

                        # 现金账户扣减
                        acct.update_cash(-1 *
                                         (order.direction * order_capital))
                        # 得到Position账户
                        position = acct.get_position(order.symbol)
                        if not position:
                            position = api.Position(
                                symbol=order.symbol, acct=acct)
                            acct.get_positions()[order.symbol] = position
                        position = acct.get_positions()[order.symbol]
                        position.change(
                            direct=order.direction, the_amount=order.order_amount, the_price=order.order_price)

                        # 交易成功,更新order的filled_amount
                        order.filled_amount = order.order_amount    # 订单成交数量
                        order.filled_price = order.order_price
                        order.state = api.OrderState.FILLED

                        # 交易成功
                        if order.direction == CONSTANT.ORDER_DIRECTION_LONG:
                            order_direction_str = '买入'
                        else:
                            order_direction_str = '卖出'
                        log.debug('订单{0} 成功 {1} {2} {3}份！'.format(
                            order.order_id, order_direction_str, order.symbol, order.order_amount))
        log.debug('[{0}]{1} 交易撮合结束 '.format(
            context.get_strategy().name, context.today))

    @staticmethod
    def finish_tick(context):
        """
        回测周期结束处理

        - Order,Position 头寸转历史
        - 策略效果计算
        """
        log.debug('[{0}]{1} 日终数据处理 '.format(
            context.get_strategy().name, context.today))

        for acct in context.get_accounts():
            # 订单存入历史(全部导入，并覆盖历史）
            for order in acct.get_orders():
                record = {
                    'order_id': order.order_id,          # 订单编号
                    'acct_name': acct.name,     # 账户名
                    'symbol': order.symbol,    # 资产名
                    'ordr_time': order.order_time,     # 下单时间
                    'order_amount': order.order_amount,  # 委托数量
                    'filled_amount': order.filled_amount,     # 成交数量
                    'order_price': order.order_price,   # 委托价格
                    'filled_price': order.filled_price,  # 成交价格
                    'state': order.state,     # 状态
                    'state_label': '',   # 状态中文
                    'state_message': order.state_message,     # 订单描述
                    'direction': order.direction,     # 订单方向
                    'offset_flag': order.offset_flag,   # 开平仓标识
                }
                context.get_strategy_data()['orders'] = context.get_strategy_data()[
                    'orders'].append(record, ignore_index=True)
                context.get_strategy_data()['orders'].drop_duplicates(
                    subset=['order_id'], keep='last', inplace=True)
                # print(context.get_strategy_data()['orders'])

            # 头寸保留历史表
            for p_symbol in acct.get_positions().keys():
                p = acct.get_positions()[p_symbol]
                # data = {
                #     'date': context.today,
                #     'account_name': acct.name,
                #     'symbol': p_symbol,
                #     'amount': p.amount,
                #     'unit_price': p.value / p.amount,
                #     'market_price': p.value,
                # }
                # context._df_positions = context._df_positions.append(data, ignore_index=True)
                # TODO 此处要改为往 context.data中添加
        # print(context._df_positions)

        # TODO ! 计算每一个账户的市价，收益率，累计收益率

        # TODO 待实现 position 存入历史

        # TODO 待实现 策略的收益计算
        log.debug('[{0}]{1} 日终数据处理结束 '.format(
            context.get_strategy().name, context.today))
