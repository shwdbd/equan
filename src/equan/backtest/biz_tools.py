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
from equan.backtest.tl import tushare, log
from datetime import datetime, timedelta, date
import time


# 日期格式
DATETIME_FORMAT = "%Y%m%d %H%M%S"
DATE_FORMAT = "%Y%m%d"


# 股票代码和 tushare 股票代码相互翻译
class TushareTsCodeTranslator:

    @staticmethod
    def to_tscode(stock_code):
        # TODO 待实现
        pass

    @staticmethod
    def to_stockcode(tscode):
        # TODO 待实现
        pass


class DTUtils:

    DATETIME_FORMAT = "%Y%m%d %H%M%S"
    DATE_FORMAT = "%Y%m%d"

    @staticmethod
    def next_date(date_str, next=1):
        """
        返回某日前后的日期
        
        Arguments:
            date_str {[type]} -- [description]
        
        Keyword Arguments:
            next {int} -- [description] (default: {1})
        
        Returns:
            [type] -- [description]
        """
        # TODO 待测试
        t1 = datetime.strptime(date_str, DTUtils.DATE_FORMAT)
        t2 = t1 + timedelta(days=next)
        return t2.strftime(DTUtils.DATE_FORMAT)


class Trade_Cal:
    """
    tushare的日历数据缓存在本地，本类的函数都从缓存文件中读取

    """

    @staticmethod
    def date_range(start=None, end=None, periods=None):
        """
        返回起始日期范围内的所有交易日

        Arguments:
            start {str} -- 日期左边界
            end str -- 日期右边界
        Keyword Arguments:
            periods {[type]} -- [description] (default: {None})

        Returns:
            [list of str] -- 日期列表
        """
        # TODO 待测试，periods参数，需要测试 网络连接不上的异常
        try:
            if start and end:
                # 限定起止日
                df = tushare.trade_cal(
                    start_date=start, end_date=end, is_open='1')
                return df['cal_date'].tolist()
            elif start and end is None and periods:
                # 从start起往后数periods个数字
                start_date = start
                end_date = DTUtils.next_date(start, periods*2)
                df = tushare.trade_cal(start_date=start_date,
                                       end_date=end_date, is_open='1')
                return df['cal_date'].head(periods).tolist()

            elif end and start is None and periods:
                # 从end往前数5个日期
                start_date = DTUtils.next_date(end, -1*periods*2)
                end_date = end
                df = tushare.trade_cal(start_date=start_date,
                                       end_date=end_date, is_open='1')
                return df['cal_date'].tail(periods).tolist()
            else:
                return []
        except Exception:
            log.error('日历tushare连接失败!')
            return []

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
#     pdate = Trade_Cal.date_range(start='20191101', periods=5)
#     print(pdate)
#     pdate = Trade_Cal.date_range(end='20191101', periods=5)
#     print(pdate)

#     # print( DTUtils.next_date('20191101', next=-5) )
 