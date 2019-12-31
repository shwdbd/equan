#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tl.py
@Time    :   2019/11/25 14:23:24
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   回测项目的通用工具集合

目前提供：
1. 日志
2. tushare数据访问api

'''
import logging.config
import tushare as ts


# =============================================
# tushare接口
token = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'


def get_ts_pro_api():
    """
    取得pro 的 python api接口
    :return: 接口对象
    """
    ts.set_token(token)
    return ts.pro_api()


tushare = get_ts_pro_api()


# =============================================
# 日志
# 使用方式：log.info('xxxx')

def get_logger(config_file_path=None):
    """
    返回一个日志器
    :rtype:
    :param config_file_path: str 配置文件路径
    :return: logger日志器
    """
    # config_file_path = r'C:\python\workspace\equan\config\log.cfg'
    config_file_path = r'config\log.cfg'

    logging.config.fileConfig(config_file_path)
    return logging.getLogger('equan')


log = get_logger()
# =============================================

# if __name__ == "__main__":
#     log.info('fda 中文')
#     df = ts.trade_cal(exchange='SSE', start_date='20180101', end_date='20180131', is_open='1')
#     print(df.head())
