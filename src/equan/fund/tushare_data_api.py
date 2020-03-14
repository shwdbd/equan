#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tushare_data_api.py
@Time    :   2020/03/11 21:13:10
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
import tushare as ts


DATA_DIR = r'data/tushare_cache/fund/'


# =============================================
# tushare接口
token = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'


def get_ts_pro_api():
    """
    取得pro 的 python api接口
    :return: 接口对象
    """
    ts.set_token(token)
    return ts.pro_api()


def download_fund_list():
    # 下载股票清单
    tushare = get_ts_pro_api()
    df = tushare.fund_basic(market='O')
    df.to_csv(DATA_DIR+'fund_basic_O.csv', index=False)
    print('下载 基金基础数据完毕 ')


def dw_fund_nv(fund_id):
    # 下载基金净值
    tushare = get_ts_pro_api()
    # df = tushare.fund_nav(ts_code=fund_id)
    df = tushare.fund_daily(ts_code=fund_id)
    df.to_csv(DATA_DIR+'nav_{0}.csv'.format(fund_id), index=False)
    print('下载 基金{0}净值完毕 '.format(fund_id))


if __name__ == "__main__":
    # download_fund_list()

    # 005918.OF
    # dw_fund_nv('005918.OF')
    dw_fund_nv('160807.SZ')
