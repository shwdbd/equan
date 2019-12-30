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

        log.info('开始运行策略')
        # TODO 检查Case的合法性

        # 初始化context
        # 加载数据
        # 加载Account、Universe
        context = api.Context(case_obj.accounts, case_obj.universe)
        case_obj.set_context(context)

        # 策略初始化
        case_obj.initialize(context)
        # 根据参数，获得所有的交易日进行循环
        for day in bt.Trade_Cal.date_range(start=case_obj.start, end=case_obj.end):
            log.debug('策略按日{0} : '.format(day))

            # 按日初始化context对象（调整日期，调整可访问的数据）
            context.set_date(day)

            # 策略逻辑处理
            case_obj.handle_data(context)
            # 订单撮合
            context.make_deal()

            # 统计汇总
            # 发送交易信号微信等
        # 所有日期策略执行结束后，统计输出策略结果
