#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   akshare_demo.py
@Time    :   2020/03/25 13:27:22
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   AkShare试验程序
'''
import akshare as ak
import tushare as ts
import pandas as pd
from pandas.util.testing import assert_frame_equal

TUSHARE_TOKEN = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'

TEMP_DIR = r'data_file/temp/'


def get_astock_daily_byak(symbol, start_date, end_date):
    # 从akshare上下载符合条件的df
    # 存入临时文件目录
    df = ak.stock_zh_a_daily(symbol='sh600016')
    # 日期过滤：
    # df = df[(df.index >= start_date) & (df.index <= end_date)]
    df = df[(df.index >= start_date)]
    df = df[(df.index <= end_date)]
    # print(df.head())
    # print(df.shape[0])
    df.to_csv(TEMP_DIR + r'ak_{symbol}.csv'.format(symbol=symbol))


def get_astock_daily_bytushare(symbol, start_date, end_date):
    ts.set_token(TUSHARE_TOKEN)
    ts_api = ts.pro_api()
    fields = ['trade_date', 'open', 'high', 'low', 'close', 'amount']
    df = ts_api.daily(ts_code=symbol, start_date=start_date, end_date=end_date, fields=fields)
    df.sort_values(by=['trade_date'], ascending=True, inplace=True)
    df.rename(columns={"trade_date": "date"}, inplace=True)
    # 修改日期格式
    df['date'] = df['date'].apply(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:8])
    # print(df.head())
    # print(df.shape[0])
    df.to_csv(TEMP_DIR + r'ts_{symbol}.csv'.format(symbol=symbol.replace('.', '_')), index=False)


# 验证tushare和akshare的A股日线数据
# 2019年一年数据，民生银行
def check_a_stock_daily():
    df_ak = pd.read_csv(TEMP_DIR+'ak_sh600016.csv', index_col=['date'], usecols=['date', 'open', 'high', 'low', 'close'])
    print(df_ak.head())
    print(df_ak.shape[0])

    df_ts = pd.read_csv(TEMP_DIR+'ts_600016_SH.csv', index_col=['date'], usecols=['date', 'open', 'high', 'low', 'close'])
    print(df_ts.head())
    print(df_ts.shape[0])

    # 核对，如果一致则不会抛出异常
    assert_frame_equal(df_ak, df_ts, check_dtype=False, check_like=True)


if __name__ == "__main__":
    print('Hi, Ak')

    check_a_stock_daily()
    # get_astock_daily_byak(symbol='sh600016', start_date='2019-01-01', end_date='2019-12-31')
    # get_astock_daily_bytushare(symbol='600016.SH', start_date='20190101', end_date='20191231')
