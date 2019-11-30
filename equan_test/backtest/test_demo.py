#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_demo.py
@Time    :   2019/11/30 13:49:40
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :    
'''
import unittest
from equan.backtest.tl import log


class Person:
    age = 10

    def __init__(self):
        # self.age = 77
        log.info('person init')


class Test_Demo(unittest.TestCase):

    person = None

    def setUp(self):
        self.person = Person
        self.person.age = 100
        log.info('setup person age:' + str(self.person.age))

    def tearDown(self):
        self.person = None
        log.info('tear down ' + str(self.person))

    def test_f1(self):
        self.person = Person
        self.person.age = 1
        log.info('f1 person age:' + str(self.person.age))

    def test_f1(self):
        self.person = Person
        self.person.age = 1
        log.info('f1 person age:' + str(self.person.age))

    def test_f2(self):
        self.person = Person()
        # self.person.age = 2
        log.info('f2 person age:' + str(self.person.age))
