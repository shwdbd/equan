#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ttjjw_ant.py
@Time    :   2020/03/07 10:46:00
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   天天基金网 基金数据爬虫

2020-04-06 发现天天基金网数据格式变化，原有爬虫失效，改为采用tushare来下载原有格式的数据

原有数据文件地址：\\date_file\\ttjj\\005918.csv
内部格式为：
FSRQ,DWJZ,JZZZL,SGZT,SHZT
2018-04-24,1.0000,,开放申购,开放赎回

真正data_api用到的字段包括：FSRQ、DWJZ

'''
import tushare as ts

TOKEN = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'


# 基金数据文件存放地址
fund_data_file_dir = r'data_file/ttjj/'


def download_fund_nv_daily(fund_symbol):
    """下载基金净值数据到本地文件（全部日期的净值数据）

    下载后替换原有文件

    Arguments:
        fund_symbol {str} -- 00000.OF tushare格式的场外基金代码

    Returns:
        str -- 生成文件的路径
    """
    ts.set_token(TOKEN)
    pro = ts.pro_api()
    # df = pro.fund_nav(ts_code='005918.OF', fields=['ts_code', 'end_date', 'unit_nav'])
    df = pro.fund_nav(ts_code='005918.OF')
    df.drop_duplicates(subset=['end_date'], keep='last', inplace=True)    # 去重复
    # print(df[df['end_date'] == '20191231'])

    # df修改为老规则的样式
    df['JZZZL'] = ''
    df['SGZT'] = '开放申购'
    df['SHZT'] = '开放赎回'
    df.rename(columns={'end_date': 'FSRQ', 'unit_nav': 'DWJZ'}, inplace=True)
    df['FSRQ'] = df['FSRQ'].apply(lambda x: x[0:4] + '-' + x[4: 6] + '-' + x[6: 8])  # 日期格式修改
    df.sort_values(by='FSRQ', ascending=True, inplace=True)
    # print(df.head())

    csv_path = fund_data_file_dir + fund_symbol[: fund_symbol.find('.')] + '.csv'
    fields = ['FSRQ', 'DWJZ', 'JZZZL', 'SGZT', 'SHZT']
    df[fields].to_csv(csv_path, index=False)

    print('下载{0}净值数据{1}条记录 ==> {2}'.format(fund_symbol, df.shape[0], csv_path))

    return csv_path


if __name__ == "__main__":
    fund_symbol = '005918.OF'
    # 360008， 005918
    path = download_fund_nv_daily(fund_symbol)
    print('result path is {0}'.format(path))
