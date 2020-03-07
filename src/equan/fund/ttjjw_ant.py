#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ttjjw_ant.py
@Time    :   2020/03/07 10:46:00
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   天天基金网 基金数据爬虫

+ json_to_csv   将手工取得的json数据，转为csv文件

'''
import os
import json
import pandas as pd

# 字段对照：
# "FSRQ": "2019-03-05", 净值日期
# "DWJZ": "1.0117", 单位净值
# "LJJZ": "1.0117", 累计净值
# "SDATE": null,
# "ACTUALSYI": "",
# "NAVTYPE": "1",
# "JZZZL": "0.55",  日增长率
# "SGZT": "开放申购",   # 申购状态
# "SHZT": "开放赎回",   # 赎回状态
# "FHFCZ": "",  # 分红情况
# "FHFCBZ": "",
# "DTYPE": null,
# "FHSP": ""

# here put the import lib


def json_to_csv(json_file, csv_file):
    """将http爬虫获得的伪json文件，转化成csv格式数据文件

    Arguments:
        json_file {str} -- 伪json文件名
        csv_file {str} -- 目标csv文件文件名

    Returns:
        [boolean] -- 成功与否
    """
    if not os.path.exists(json_file):
        print('文件{0}不存在，转化失败！'.format(json_file))
        return False

    file_context = ""
    with open(json_file, mode='r', encoding='utf-8') as jf:
        for l in jf.readlines():
            file_context += l
    file_context = file_context[file_context.find("(")+1:file_context.rfind(")")]
    # print(file_context)
    data_dict = json.loads(file_context)
    data_list = data_dict['Data']['LSJZList']
    cols = ['FSRQ', 'DWJZ', 'JZZZL', 'SGZT', 'SHZT']
    df = pd.DataFrame(data=data_list, columns=cols)   # 转为dataframe
    # print(df.head())
    df.to_csv(csv_file, index=False)
    print('转换完毕！')

    return True


if __name__ == "__main__":
    # 转csv文件：
    json_file = r'src\equan\fund\005918 2019.json'
    csv_file = r'src\equan\fund\005918 2019.csv'
    r = json_to_csv(json_file, csv_file)
