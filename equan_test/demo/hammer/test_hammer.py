#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_hammer.py
@Time    :   2019/11/18 17:34:35
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   锤子线策略 单元测试
'''
import unittest


class Test_SetHammerFlag(unittest.TestCase):
    """
    单元测试：找到锤子线日期

    
    
    """

    def test_find_hammer(self):
        """
        DAY1: YES, 锤子形
        DAY2: NO, 上影线=Bar=下影线
        DAY3: NO, Bar过长
        DAY4：NO, 上影线过长
        DAY5: YES，十字星
        """


# here put the import lib
