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
    config_file_path = r'src\equan\fund\log.cfg'
    logging.config.fileConfig(config_file_path)
    return logging.getLogger('funding')


log = get_logger()
# =============================================

if __name__ == "__main__":
    log.info('fda 中文')
