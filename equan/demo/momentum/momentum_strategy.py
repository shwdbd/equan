#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   momentum_strategy.py
@Time    :   2019/11/12 09:46:13
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   动量策略 临摹程序

- get_data                  取得沪深300的数据
- strategy_1day             1天动量策略
- strategy_Nday             N天移动平均动量策略
- strategy_ND               穷举法参数寻优优化后的策略
- strategy_high             高频数据策略
- strategy_estimator        策略评估

'''
import pandas as pd
import tushare as ts
# import numpy as np
# import matplotlib.pyplot as plt

# 回测指数
INDEX_CODE = '000300.SH'
# 回测数据日期范围
START_DATE = '20190101'
END_DATE = '20190110'


token = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'


def get_pro_api():
    """
    取得pro 的 python api接口
    :return: 接口对象
    """
    ts.set_token(token)
    return ts.pro_api()


def get_data():
    """
    取得 策略基础数据 的数据

    df: date|price ;  按date升序排序
    price为收盘价,close

    """
    df = get_pro_api().index_daily(ts_code=INDEX_CODE, start_date=START_DATE,
                                   end_date=END_DATE, fields=['trade_date', 'close'])
    df.rename(columns={'trade_date': 'date', 'close': 'price'}, inplace=True)
    df.sort_values(by='date', ascending=True, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    return df


if __name__ == "__main__":
    data = get_data()
    print(data.head())
    print(data.info())
