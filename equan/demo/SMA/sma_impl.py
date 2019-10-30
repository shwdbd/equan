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

    DATA_SOURCE = 'local'   # tushare | local

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

        # if self.SEEK_EQUITY_SETTINGS['seek.model'] == 'PEPB_MIN':
        #     return _seek_equity_by_pepb()
        # elif self.SEEK_EQUITY_SETTINGS['seek.model'] == 'MATRIX':
        #     return _seek_equity_by_pepb()

        return ['xxxx']

    def get_hs300(self, fields=None):
        """
        根据tushare获取沪深300股票

        Keyword Arguments:
            fields {list} -- 返回的字段列表 (default: {None})

        Returns:
            pd.DataFrame -- 沪深300股票(结构同tushare)
        """
        # 加入本地缓存功能，找本地文件如没有，则网上下载
        if self.DATA_SOURCE == 'local':
            file_path = r'data/hs300.csv'
            if not os.path.exists(file_path):
                ts.get_hs300s().to_csv(file_path)
            df = pd.read_csv(file_path, index_col=0)
        else:
            df = ts.get_hs300s()

        if fields == None or len(fields) == 0:
            # 所有的字段
            return df
        else:
            # 指定字段
            return df.loc[:, fields]


if __name__ == "__main__":
    f = SMATestFrame()
    f.seek_equity()
