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

# TODO 要加入logger工具


class SMATestFrame(sma.EquityTradingStrategyFrame):

    # 选股参数
    SEEK_EQUITY_SETTINGS = {
        'seek.model': 'MATRIX',   # 选股方式，PEPB_MIN | MATRIX
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
        print('股票池数据获取完成！')

        # 进行选股
        if self.SEEK_EQUITY_SETTINGS['seek.model'] == 'PEPB_MIN':
            # 烟蒂法：
            df['烟蒂因子'] = df['PB'] * df['PE']
            df.sort_values(by=['行业', '烟蒂因子'], ascending=[
                           True, False], inplace=True)
            df.drop(index=df[df['烟蒂因子'].isnull()].index, inplace=True)
            df_stock = df.groupby(by='行业').head(3).sort_values(by=['行业'])
            stock_list = df_stock.index.tolist()
            print('用烟蒂法共筛选出股票{0}支！'.format(len(stock_list)))
            return stock_list
        elif self.SEEK_EQUITY_SETTINGS['seek.model'] == 'MATRIX':
            # 经验矩阵法
            # 根据市值，判断企业 大中小
            def size_of_company(value_of_market):
                if value_of_market > 50000000000:
                    return '大'
                elif value_of_market > 10000000000 and value_of_market < 50000000000:
                    return '中'
                else:
                    return '小'
            df['企业规模'] = df['总市值'].apply(size_of_company)
            # 根据PE、PB，判断是否可以选择

            def choose_by_pepb(df):
                size = df['总市值']
                pb = df['PB']
                pe = df['PE']

                if size == '大':
                    if (pb < 0.7 and pe < 30) or (pb < 0.8 and pe < 6):
                        return '1'
                elif size == '
                if (pb < 0.8 and pe < 50) or (pb < 1 and pe < 10):
                        return '1'
                elif size == '小':
                    if (pb < 0.9 and pe < 50) or (pb < 1 and pe < 20):
                        return '1'
                else:
                    return '0'

            df['是否选取'] = df.apply(choose_by_pepb, axis=1)
            df_stock = df[df['是否选取'] == '1']
            stock_list = df_stock.index.tolist()
            print('用经验矩阵法共筛选出股票{0}支！'.format(len(stock_list)))
            return stock_list
        else:
            print('未知的筛选方法，处理终止！')
            return []

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
        if count_of_stock != df_index.shape[0]:
            print('【警告】股票指标数据未全部取得，应该得到{0}条记录，实际得到{1}条记录!'.format(
                count_of_stock, df_index.shape[0]))
        del(df_index['ts_code'])    # 删除不需要的列
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

    def strategy(stock_list):
        """
        策略实现接口，本函数需要被实现

        返回的DataFrame有字段:
        date, code, position
        其中：
        date, datetime64格式日期
        code, 6位数字股票代码
        position，仓位标志, 1买入,-1卖出,0平仓

        # SMA的策略：
        1. 计算20, 60日的移动平均线；
        2. 



        Arguments:
            stock_list {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        



        return None



if __name__ == "__main__":
    f = SMATestFrame()
    stocks = f.seek_equity()
    print(stocks)
