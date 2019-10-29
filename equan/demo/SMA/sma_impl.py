#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sma_impl.py
@Time    :   2019/10/25 16:53:30
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   SMA回测 实现工具函数
'''
import pandas as pd
import tushare as ts
import equan.demo.SMA.sma as sma


class SMATestFrame(sma.EquityTradingStrategyFrame):

    def seek_equity(self):
        """
        选股函数

        烟蒂法选股
        
        Returns:
            [type] -- [description]
        """
        print('选股函数')
        return ['xxxx']

