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
import pandas as pd


class StrategyRunner:
    """
    策略回测执行类
    """

    @staticmethod
    def back_test_run(case_obj):
        # 运行策略实例

        print('开始运行策略')

        # 初始化context
        # 加载数据
        # 加载Account、Universe
        context = None

        # 策略初始化
        case_obj.initialize(context)
        for day in pd.date_range(start=case_obj.start, end=case_obj.end):  # 根据参数，获得所有的交易日进行循环
            # FIXME 此处要改为交易日

            # 按日初始化context对象（调整日期，调整可访问的数据）
            context = api.Context()
            context._accounts = case_obj.accounts   # FIXME 此处需要修改
            # TODO 初始化context

            # 策略逻辑处理
            case_obj.handle_data(context)
            # 订单撮合
            api.OrderDealer.deal_order(context.get_accounts())

            # 统计汇总
            # 发送交易信号微信等
        # 所有日期策略执行结束后，统计输出策略结果

    
