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
import numpy as np
import tushare as ts
import equan.demo.SMA.sma as sma
import equan.demo.SMA.data_picker as data_picker
import os
from functools import reduce


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
            df_stock_pool = data_picker.get_hs300s(fields=['code', 'name'])
        else:
            df_stock_pool = data_picker.get_hs300s(fields=['code', 'name'])
        print('获得待选股票池({1})一共{0}个股票'.format(
            df_stock_pool.shape[0], self.SEEK_EQUITY_SETTINGS['stock_pool']))
        
        # 获得其他数据
        df = self.get_data(df_stock_pool)
        if df_stock_pool.shape[0] != df.shape[0]:
            raise Exception('获取数据有问题，应该得到{0}条记录，实际得到{1}条记录!'.format(
                df_stock_pool.shape[0], df.shape[0]))
        # print(df.head())

        # TODO 进行选股




        return df_stock_pool["code"].tolist()
        # return []

    def get_data(self, df_stock_pool):
        """
        根据 股票池范围，从tushare上取得所有的数据，拼接成大的DataFrame

        Index: 股票代码
        Columns：
        股票名称, 行业, 价格, PE, PB, 总市值

        数据处理要求:
        1. 记录数同 参数 一致，否则抛出异常
        2. 价格类四舍五入到2位小数
        3. index是股票代码

        Arguments:
            df_stock_pool {DataFrame} -- 股票代码, code, name
        """
        count_of_stock = df_stock_pool.shape[0]

        # 基础信息
        df_basic = data_picker.get_stock_basic()
        df_basic = df_basic[df_basic['symbol'].isin(df_stock_pool.code)]
        if count_of_stock != df_basic.shape[0]:
            raise Exception('股票基础数据未全部取得，应该得到{0}条记录，实际得到{1}条记录!'.format(
                count_of_stock, df_basic.shape[0]))
        df_basic = df_basic.loc[:, ['symbol', 'industry']]  # 取 股票代码,行业 两个字段
        df_basic.rename(columns={'symbol': 'code',
                                 'industry': '行业'}, inplace=True)

        # 指标信息
        df_index = data_picker.get_daily_basic_by_date(
                trade_date=self.SEEK_EQUITY_SETTINGS['benchmark.trade_date']).loc[:, [
                'ts_code', 'close', 'pe', 'pb', 'total_mv']]
        df_index['code'] = df_index['ts_code'].apply(
            lambda x: x[: x.index('.')])  # 整理ts_code的后缀
        df_index = df_index[df_index['code'].isin(df_stock_pool.code)]  
        # TODO 数据有缺失
        # if count_of_stock != df_index.shape[0]:
        #     raise Exception('股票指标数据未全部取得，应该得到{0}条记录，实际得到{1}条记录!'.format(
        #         count_of_stock, df_index.shape[0]))
        del(df_index['ts_code'])
        df_index.rename(columns={'code': 'code', 'close': '价格',
                                 'pe': 'PE', 'pb': 'PB', 'total_mv': '总市值'}, inplace=True)

        # 合并成总的df
        df = reduce(lambda x, y: x.merge(y, how='left', on='code'),
                    [df_stock_pool, df_basic, df_index])
        # 改列名
        df.rename(columns={'code': '股票代码', 'name': '股票名称'}, inplace=True)
        # 价格四舍五入
        df['价格'] = np.round(df['价格'], 2)
        # 设置index
        df.set_index(['股票代码'], inplace=True)

        return df


if __name__ == "__main__":
    f = SMATestFrame()
    f.seek_equity()
    
