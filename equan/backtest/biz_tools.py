#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   biz_tools.py
@Time    :   2019/11/25 14:50:48
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   业务工具类
'''
from equan.backtest.tl import tushare

# 日期格式
DATETIME_FORMAT = "%Y%m%d %H%M%S"
DATE_FORMAT = "%Y%m%d"


# class DateTimeUtils:

    # def to_date_str(datetime_obj):



class Trade_Cal:
    """
    tushare的日历数据缓存在本地，本类的函数都从缓存文件中读取

    """

    @staticmethod
    def date_range(start, end):
        """
        返回起始日期范围内的所有交易日

        Arguments:
            start {str} -- 日期左边界
            end str -- 日期右边界

        Returns:
            [list of str] -- 日期列表
        """
        df = tushare.trade_cal(start_date=start, end_date=end, is_open='1')
        return df['cal_date'].to_list()

    @staticmethod
    def previous_date(date):
        """
        按日期取得前一个交易日

        Arguments:
            date {[type]} -- [description]

        Returns:
            [str] -- 日期，如果没有则返回None
        """
        df = tushare.trade_cal(
            start_date=date, end_date=date, fields=['pretrade_date'])
        if len(df) > 0:
            return df['pretrade_date'][0]
        else:
            return None


# if __name__ == "__main__":
#     pdate = Trade_Cal.previous_date('99990101')
#     print(pdate)
