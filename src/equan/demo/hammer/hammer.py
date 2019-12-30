#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   hammer.py
@Time    :   2019/11/18 13:32:05
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   锤子线策略实现
'''
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
# matplotlib.sytle.use('ggplot')

token = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'


def get_pro_api():
    """
    取得pro 的 python api接口
    :return: 接口对象
    """
    ts.set_token(token)
    return ts.pro_api()


class HammerStrategy:
    """
    锤子线 策略回测
    """

    # 参数
    settings = {
        'STOCK_CODES': ['600016.SH'],     # 待回测的股票代码
        'START_DATE': '20120101',     # 回测起始日期
        'END_DATE': '20170101',
        'HAMMER.ENTITY_TO_PRICE': 0.03,   # 实体/股价 的上限
        'HAMMER.HEADER_TO_TAIL': 0.5,   # 上影线长度/下影线长度
        'HAMMER.TAIL_TO_ENTITY': 2,   # 下影线长度/实体
        'MA.windows': 10,   # 观察窗口
        'STOPLOSE_TRIGGER': 1,  # 表示当价格偏离均线满足几倍标注按察时止损
    }

    def get_data(self):
        """
        取得数据包

        df: index|date,open,close,high,low,ma,std;order by date
        其中：
        ma 是close价格的MA.windows的移动平均值
        std 是标准差
        """
        fields = ['trade_date', 'open', 'high', 'low', 'close']
        df = get_pro_api().daily(
            ts_code=self.settings['STOCK_CODES'][0], start_date=self.settings['START_DATE'],
            end_date=self.settings['END_DATE'], fields=fields)
        # 排序
        df.sort_values(by=['trade_date'], ascending=True, inplace=True)
        # 重置index
        df.reset_index(inplace=True)

        # 计算ma, std
        df['ma'] = df['close'].rolling(self.settings['MA.windows']).mean()
        df['std'] = df['close'].rolling(self.settings['MA.windows']).std()
        df['yes_ma'] = df['ma'].shift(1)
        df['yes_std'] = df['std'].shift(1)

        # 计算价格变动
        df['pct_change'] = df['close'].pct_change()

        return df

    def find_hammer(self, data):
        """
        识别 锤子线 标志

        在 data 中新增一列：hammer,1表示当日是锤子线，0表示不是
        """
        # 计算K Bar的各部分长度
        data['k_body'] = abs(data['open']-data['close'])
        data['k_head'] = data['high'] - \
            data[['open', 'close']].max(axis='columns')
        data['k_tail'] = data[['open', 'close']].min(
            axis='columns') - data['low']

        # 判断是否是锤子线：
        data['k_body_cond'] = np.where(
            data['k_body']/data['open'] < self.settings['HAMMER.ENTITY_TO_PRICE'], True, False)
        data['k_head_cond'] = np.where(
            data['k_tail'] == 0, False, data['k_head']/data['k_tail'] < self.settings['HAMMER.HEADER_TO_TAIL'])
        data['k_tail_cond'] = np.where(
            data['k_body'] == 0, True, data['k_tail']/data['k_body'] > self.settings['HAMMER.TAIL_TO_ENTITY'])
        data['hammer'] = data[['k_body_cond', 'k_head_cond',
                               'k_tail_cond']].all(axis='columns')

        return data

    def get_return(self):
        """
        汇总计算收益
        """
        pass

    def back_test(self):
        """
        交易回测

        1. 识别每天的锤子形态
        2. 大循环 计算每日开仓关仓
        3. 汇总统计收益

        """

        print('开始 锤子线 回测 ... ')

        # 加载数据
        data = self.get_data()
        print('共获得{0}天的数据'.format(len(data)))

        # 识别锤子线形态
        data = self.find_hammer(data)
        print('锤子线识别完成！')

        # 大循环执行策略
        data = self.run_strategy(data)

        return data

    def run_strategy(self, data):
        """
        执行策略
        """
        flag = 0    # 持仓记录， 1代码有仓位，0表示空仓；
        # 策略大循环
        print('策略大循环开始，共{0}个交易日'.format(len(data)))
        WINDOWS = self.settings['MA.windows']

        for day in range(2*WINDOWS, len(data)):
            if flag == 0:
                # 空仓，判断是否有买入机会
                # 持续下跌 且 昨日出现锤子形，就买入开仓
                if data.loc[day-WINDOWS, 'yes_ma'] > data.loc[day, 'yes_ma']:   # 持续下跌
                    if data.loc[day-1, 'hammer']:   # 昨日出现 锤子线
                        # 买入操作，以开盘价买入
                        flag = 1
                        # 仓位操作标识，B为买入，S为卖出
                        data.loc[day, 'position'] = 'B'
                        # data.loc[day, 'long_price'] = data.loc[day, 'open']
                        long_open_price = data.loc[day, 'open']     # 记录买入价格
                        # 记录买入昨日的价格的std
                        long_open_delta = data.loc[day, 'yes_std']
                        # 收益操作：
                        data.loc[day, 'return'] = (
                            data.loc[day, 'close']/data.loc[day, 'open']) - 1
                else:
                    # 如果持续空仓，则无收益
                    data.loc[day, 'return'] = 0
            else:
                # 有仓位，判断是否止损机会
                # 止损价 是 固定止损价 和 浮动止损价 中取大值
                stoplose_fix = long_open_price - long_open_delta    # 固定止损价
                stoplose_floating = data.loc[day, 'yes_ma'] - \
                    self.settings['STOPLOSE_TRIGGER'] * \
                    data.loc[day, 'yes_std']
                stoplose_price = max(stoplose_fix, stoplose_floating)

                if data.loc[day, 'low'] < stoplose_price:
                    # 卖出操作：
                    data.loc[day, 'position'] = 'S'
                    # 收益操作：
                    data.loc[day, 'return'] = min(
                        data.loc[day, 'open'], stoplose_price) / data.loc[day-1, 'close'] - 1      # 按开盘价和止损价中低的价格卖出，计算收益
                else:
                    # 不满足止损条件，继续持仓
                    data.loc[day, 'return'] = data.loc[day,
                                                       'close'] / data.loc[day-1, 'close'] - 1

        # 计算策略收益
        data['return'].fillna(0, inplace=True)    # 如果没有任何操作，则让这些天的收益率=0
        data['strategy_return'] = (data['return']+1).cumprod()
        data['stock_return'] = (data['pct_change']+1).cumprod()

        return data

    def draw_return(self, data):
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(data.stock_return)
        ax.plot(data.strategy_return)
        plt.title(self.settings['STOCK_CODES'][0])
        plt.legend()
        plt.show()


if __name__ == "__main__":
    sty = HammerStrategy()
    data = sty.back_test()
    print(data.head(40))
    sty.draw_return(data)
