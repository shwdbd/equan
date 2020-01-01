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
import equan.backtest.biz_tools as bt
from equan.backtest.tl import log


class StrategyRunner:
    """
    策略回测执行类
    """

    @staticmethod
    def back_test_run(case_obj):


        # 运行策略实例

        if not case_obj or not issubclass(type(case_obj), api.BaseStrategy):
            log.error('策略实例为空或不是基策略的实例！')
            return

        log.info('[{0}] 开始运行策略 '.format(case_obj.name))
        # 初始化context
        context = api.Context(case_obj)
        case_obj.set_context(context)

        # 策略初始化
        log.debug('[{0}] 调用initialize函数'.format(case_obj.name))
        case_obj.initialize(context)
        # 根据参数，获得所有的交易日进行循环
        for day in bt.Trade_Cal.date_range(start=case_obj.start, end=case_obj.end):
            log.debug('[{0}]{1}策略代码执行 ... '.format(case_obj.name, day))

            # 按日初始化context对象（调整日期，调整可访问的数据）
            context.set_date(day)

            # 策略逻辑处理
            case_obj.handle_data(context)
            # 订单撮合
            context.make_deal()

            # 统计汇总
            context.finish_tick()
            # 发送交易信号微信等
        # 所有日期策略执行结束后，统计输出策略结果

        log.info('[{0}] 策略运行结束 '.format(case_obj.name))
