#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sma.py
@Time    :   2019/10/24 22:08:02
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   移动平均线策略



'''
# import pandas as pd
import tushare as ts
import equan.demo.SMA.sma_impl as impl


# 全局参数
DATA_SOURCE = 'local'   # 数据来源，tushare | local
BASE_DATE = '20191025'  # 基准日期


class EquityTradingStrategyFrame:
    """
    股票交易回测框架
    """

    def seek_equity(self):
        """
        选股函数
        
        Returns:
            list of str -- 股票代码列表
        """
        # TODO 待实现
        return []


if __name__ == "__main__":
    frm = impl.SMATestFrame()
    frm.seek_equity()
