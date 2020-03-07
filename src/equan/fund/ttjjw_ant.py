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
import urllib.request
import urllib.parse

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


def ant_fund():
    fund_symbol = '005918'
    start = '2019-01-01'
    end = '2019-12-31'
    page_size = 20     # 365
    page_no = 1
    url = 'http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18301730369606145108_1583501484436&fundCode=005918&pageIndex={page_no}&pageSize={page_size}&startDate={start}&endDate={end}&_=1583548814846'.format(page_size=page_size, start=start, end=end, page_no=page_no)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Host': 'api.fund.eastmoney.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'http://fundf10.eastmoney.com/jjjz_005918.html',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,fr;q=0.7,ja;q=0.6,zh-TW;q=0.5',
        'Cookie': 'st_pvi=01936466598903; st_sp=2019-07-02%2020%3A04%3A13; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink',
        # 'Cookie': 'qgqp_b_id=a5c790cb8efcc9770a6fc869b3f6317f; em_hq_fls=js; HAList=f-0-000300-%u6CAA%u6DF1300; st_si=31331266555451; st_asi=delete; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND0=null; EMFUND9=03-06 21:31:09@#$%u5929%u5F18%u6CAA%u6DF1300ETF%u8054%u63A5C@%23%24005918; st_pvi=92009671528561; st_sp=2019-09-25%2009%3A09%3A12; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=6; st_psi=20200307103356147-112200304021-1215736316',
    }
    # headers = {

    # }

    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request, timeout=15)
    print('conn ok')
    print(response.code)
    # 输出所有
    if response.code == 200:
        print(response.read().decode('utf-8'))
    # print(response.read().decode('utf-8'))

    # #将内容写入文件中
    # with open('fund.txt', 'w') as fp:
    #     fp.write(response.read().decode('gbk'))
    
    print('Done')
    # 输出所有

if __name__ == "__main__":
    # 转csv文件：
    json_file = r'src\equan\fund\005918 all.json'
    csv_file = r'src\equan\fund\005918.csv'
    r = json_to_csv(json_file, csv_file)

    # # 爬取网页数据
    # ant_fund()
