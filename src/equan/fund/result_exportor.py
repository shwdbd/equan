#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   result_exportor.py
@Time    :   2020/03/27 12:04:32
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基金回测结果输出组件
'''
from jinja2 import PackageLoader, Environment
import pandas as pd
import os
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']


def export_to_console(result, tester):
    """回测结果输出到控制台

    Arguments:
        result {equan.fund.fund_backtesting_impl.StrategyResult} -- 回测结果
        tester {equan.fund.fund_backtesting.FundBackTester} -- 回测对象
    """

    # 回测结果输出到控制台
    tester.fm_log('='*20)
    tester.fm_log('策略总收益 ：{0} %'.format(result.return_rate))
    tester.fm_log('交易次数 ：{0} '.format(round(result.total_number_of_transactions)))
    tester.fm_log('期初投入资金 ：{0}'.format(result.total_capital_input))
    tester.fm_log('期末收益资金 ：{0}'.format(result.value))
    # tester.fm_log('每日收益表 : ')
    # for acct in tester.get_context().get_accounts():
    #     tester.fm_log('账户 {0} ：'.format(acct.name))
    #     tester.fm_log('{0}'.format(acct.get_daily_return()))
    tester.fm_log('='*20)


def export_to_html(result, tester):
    """回测结果输出到HTML文件

    Arguments:
        result {equan.fund.fund_backtesting_impl.StrategyResult} -- 回测结果
        tester {equan.fund.fund_backtesting.FundBackTester} -- 回测对象
    """
    # 结果输出到HTML文件

    # 导出的HTML路径
    html_file_path = tester.settings['html-exporter.path'] + tester.settings['html-exporter.file_name']

    # 生成收益率曲线图片
    df_return_rate = result.get_return_table()
    # draw:
    plt.figure(figsize=(12, 6))
    plt.title('当期收益率')
    plt.plot(df_return_rate.index, df_return_rate['当期收益率'])
    pic_dir_path = html_file_path + r'.assets'
    if not os.path.exists(pic_dir_path):
        os.mkdir(pic_dir_path)
    plt.savefig(pic_dir_path + '/fund_return_ratio.jpg')   # 保存成文件
    # plt.show()
    # print(df_return_rate)


    # 配置路径：my_package包，templates目录下，找到模板
    my_package = 'equan.fund'
    env = Environment(loader=PackageLoader(my_package, 'templates'))
    template = env.get_template('strategy_result.html')   # 取得模板
    # 准备数据
    result.total_number_of_transactions = round(result.total_number_of_transactions)
    html_context = template.render(result=result, html_file_name=tester.settings['html-exporter.file_name'])
    with open(html_file_path, mode='w', encoding='utf-8') as f:
        f.write(html_context)

    # TODO 生成收益率详细表格
    # print( result.get_return_table().to_html() )

