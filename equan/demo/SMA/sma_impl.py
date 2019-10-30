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
import os


class SMATestFrame(sma.EquityTradingStrategyFrame):



    # 选股参数
    SEEK_EQUITY_SETTINGS = {
        'seek.model': 'PEPB_MIN',   # 选股方式，PEPB_MIN | MATRIX
        'stock_pool': 'hs300',   # 股票池，默认为hs300沪深300
        'benchmark.trade_date': '20191030',   # PE、PB计算的交易日期
        'topN': 3,   # 按行业取前N个股票
    }



    def seek_equity(self):
        """
        选股函数

        烟蒂法选股

        1. 获得待选股票池 df_stock_pool(股票代码, 股票名称)（默认是hs300）
        2. 根据df_stock_pool收集现需要的字段df(股票代码, 股票名称，行业，PE、PB、市值)
        3. 不同模式，实现不同的选股

        Returns:
            [type] -- [description]
        """
        print('选股模块启动')

        # 获得待选股票池
        if self.SEEK_EQUITY_SETTINGS['stock_pool'] == 'hs300':
            df_stock_pool = self.get_hs300(fields=['code', 'name'])
        else:
            df_stock_pool = self.get_hs300(fields=['code', 'name'])
        print('获得待选股票池({1})一共{0}个股票'.format(
            df_stock_pool.shape[0], self.SEEK_EQUITY_SETTINGS['stock_pool']))
        # df_stock_pool['code'].astype('str', copy=False)
        df_stock_pool = df_stock_pool.astype({'code':'str'})
        # print(df_stock_pool.shape[0])
        # print(df_stock_pool[ df_stock_pool['code'] == '402' ])
        # print(df_stock_pool.info())

        # 根据df_stock_pool收集现需要的字段df(股票代码, 股票名称，行业，PE、PB、市值)
        # # 基本信息，行业
        df_basic = self.ts().stock_basic()
        # print(df_basic.shape[0])
        # print(df_basic.info())
        # df_basic['symbol'].isin(df_stock_pool.code).to_csv('xxx.csv')
        df_basic = df_basic[df_basic['symbol'].isin(df_stock_pool.code)]
        # df_basic = df_basic.loc[:, ['symbol', 'industry']]
        # df_basic.rename(columns={'symbol': 'code'}, inplace=True)
        print(df_basic[ df_basic.symbol == '600000' ].head())
        # print(df_stock_pool.code.head())
        # print(df_basic.head())
        print(df_basic.shape[0])
        # df_basic.to_csv('xxx.csv')



        # if self.SEEK_EQUITY_SETTINGS['seek.model'] == 'PEPB_MIN':
        #     df["PE_m_PB"] = df["pe"] * df['pb']
        # elif self.SEEK_EQUITY_SETTINGS['seek.model'] == 'MATRIX':
        #     return _seek_equity_by_pepb()

        return df_stock_pool["code"].tolist()
        # return []




if __name__ == "__main__":
    f = SMATestFrame()
    f.seek_equity()

    # print(ts.get_hs300s().info())
    # print(f.get_hs300().info())
