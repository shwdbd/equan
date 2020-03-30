"""
基金回测框架

v 0.1 第一个可用的版本
v 0.2
- new：回测结果按HTML输出
- new：回测输出，可由客户端提供个性的输出函数
- new：回测输出，回值收益曲线
- new：新增equan.fund的版本号
- 将原版equan.fund.data_api功能迁移到equan.fdata下
- fix: 修复v0.1.1中收益率计算错误
- fix: 修复v0.1.1中资产卖出，反而资产份数增加问题
- fix: 修复基金按当日牌价成交的错误（v0.1.1中是按前一交易日价格成交）ok
- new: 添加客户端可试用函数：after_dayend和end
- new: [文档]添加回测框架流程图、框架主要类结构图
- new: 统计策略执行时间
- new: fdata使用独立的日志

"""

__version__ = "0.2"
__author__ = "Junjie Wang"
