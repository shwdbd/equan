#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tushare_data.py
@Time    :   2019/10/29 22:15:31
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Tushare数据获取函数集
'''

# here put the import lib

MODE = 'tushare'    # 数据模式 tushare|local|test
FILE_DIR = r'equan/demo/SMA/tushare_data/'  # 文件存放路径


def get_data_file_dir():
    """
    取得数据文件存放路径
    """
    if MODE == 'local':
        FILE_DIR = r'equan/demo/SMA/tushare_data/'
    elif MODE == 'test':
        FILE_DIR = r'equan_test/demo/SMA/tushare_data/'
    else:
        return None


def get_hs300():
    """[summary]
    
    Returns:
        [type] -- [description]
    """

    return df
