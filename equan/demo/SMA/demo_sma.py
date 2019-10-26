#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   demo_sma.py
@Time    :   2019/10/26 19:22:59
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   金程教育的演示代码实现


1. 选股
2. 选择某一股票
3. SMA策略实现
4. 策略评估

1.1 取hs300
1.2 获取hs300的close, pe, pb, 行业
1.3 合并成 data_df
    判断 成长性、高风险
1.4 group找出每个行业 PE*PB 的前三名股票
1.5 获得最终待投资股票池, list of stock code

2.1 选择某股票，如：

3.1 获取该股票7年的价格数据 data_df
3.2 计算SMA_20, SMA_60
3.3 根据 金叉、死叉 原理判断 开仓信号position
3.4 计算每天的return
3.5 计算策略每天的return_sma
3.6 绘制 return ， return_sma 的图形
3.7 计算 收益、风险、回撤、总开仓次数
3.8 计算 shape_ration

附加：
0.1 去除 short 的收益，重新计算收益


'''

# here put the import lib
