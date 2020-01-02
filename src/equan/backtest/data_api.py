#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_api.py
@Time    :   2019/11/26 09:55:32
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据访问接口

1. TODO 取得某股票某时点的价格

'''
from equan.backtest.tl import log, tushare


def stock_price(symbol, trade_date, price_type='open'):
    """
    查询股票价格

    如出现网络中断等问题，记录error日志，返回None

    Arguments:
        symbol {str|list} -- tushare格式的股票代码，如 000001.SZ
                             可使用list查询多个股票
        trade_date {yyyyMMdd} -- 交易日期

    Keyword Arguments:
        price_type {str} -- 价格种类 (default: {'open'})，可以取值范围：open|high|low|close

    Returns:
        [price:float] -- 价格
    """
    try:
        legal_price_type = ['open', 'high', 'low', 'close']
        if price_type not in legal_price_type:
            log.error('无效的价格类型{0}'.format(price_type))
            return None

        # 调用tushare查询
        if isinstance(symbol, str):
            price_df = tushare.daily(ts_code=symbol, trade_date=trade_date)
            if price_df is None or price_df.empty:
                log.error('无效的股票代码{0}或无效的数据日期{1}'.format(symbol, trade_date))
                return None
            price = price_df[price_type][0]
            return price
        elif isinstance(symbol, list):
            result_dict = {}
            for stock_id in symbol:
                df = tushare.daily(ts_code=stock_id, trade_date=trade_date)
                if df is None or df.empty:
                    log.error('无效的股票代码{0}或无效的数据日期{1}'.format(
                        stock_id, trade_date))
                    return None
                result_dict[stock_id] = df[price_type][0]
            return result_dict
        else:
            return None

    except Exception as err:
        log.error('查询股票价格错误 {0}'.format(str(err)))
        return None


if __name__ == "__main__":
    print(stock_price('600016.SH', '20191104', 'open'))
    print(stock_price('600016.SH', '20191105', 'open'))
    