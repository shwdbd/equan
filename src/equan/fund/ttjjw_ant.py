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
+ ant_fund      从天天基金网上爬取数据，并解析写入csv文件



'''
import os
import json
import pandas as pd
import urllib.request
import urllib.parse
import datetime
import equan.fund.DataAPI_CI as DATA_CI
import equan.fund.tl as tl

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

# 全局参数：
TEMP_FILE_DIR = r'data_file/temp_files/'
# 天天基金网，日线数据地址
TTJJ_URL = 'http://api.fund.eastmoney.com/f10/lsjz?callback=jQuery18301730369606145108_1583501484436&fundCode={fund_id}&pageIndex={page_no}&pageSize={page_size}&startDate={start}&endDate={end}&_=1583548814846'
TTJJ_HEADER = {
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
TTJJ_TIMEOUT = 5   # 超时容忍5秒
TTJJ_RESPONSE_ENCODING = 'utf-8'
TTJJ_PAGE_SIZE = 5


log = tl.get_logger()

def json_to_csv(json_file, csv_file):
    """将http爬虫获得的伪json文件，转化成csv格式数据文件

    Arguments:
        json_file {str} -- 伪json文件名
        csv_file {str} -- 目标csv文件文件名

    Returns:
        [boolean] -- 成功与否
    """
    if not os.path.exists(json_file):
        log.info('文件{0}不存在，转化失败！'.format(json_file))
        return False

    file_context = ""
    with open(json_file, mode='r', encoding='utf-8') as jf:
        for l in jf.readlines():
            file_context += l
    # 解析
    df = _htmlstr_2_df(file_context)
    # log.info(df.head())
    df.to_csv(csv_file, index=False)
    log.info('转换完毕！')

    return True


def _read_http(fund_symbol, start_date, end_date, page_no):
    # 从网页读取，并返回读取到的HTTP Response文本
    # 失败，则返回None
    try:
        url = TTJJ_URL.format(fund_id=fund_symbol, start=start_date, end=end_date, page_no=page_no, page_size=TTJJ_PAGE_SIZE)
        request = urllib.request.Request(url=url, headers=TTJJ_HEADER)
        response = urllib.request.urlopen(request, timeout=TTJJ_TIMEOUT)
        # 输出所有
        if response.code == 200:
            http_str = response.read().decode(TTJJ_RESPONSE_ENCODING)
            # log.info(http_str)
            return http_str
        else:
            log.info('天天基金网拒绝访问')
            return None
    except Exception as err:
        log.info('读取天天基金网数据出错，' + str(err))
        return None


def _htmlstr_2_df(http_str):
    # 将网页返回解析成dataframe
    # 有错误则返回None

    try:
        http_str = http_str[http_str.find("(")+1:http_str.rfind(")")]   # 就取中间json部分
        # log.info(http_str)
        data_dict = json.loads(http_str)
        # log.info(data_dict)
        data_list = data_dict['Data']['LSJZList']
        cols = ['FSRQ', 'DWJZ', 'JZZZL', 'SGZT', 'SHZT']    # df 的列
        df = pd.DataFrame(data=data_list, columns=cols)   # 转为dataframe
        # 总记录数
        total_count = data_dict['TotalCount']
        return df, total_count
    except Exception:
        return None


def ant_fund(fund_symbol, start_date, end_date):
    """从天天基金网爬取数据，返回pandas.dataframe

    Arguments:
        fund_symbol {[type]} -- 基金编号（按天天基金网的格式）
        start_date {[type]} -- 开始日期，yyyy-MM-dd格式（含）
        end_date {[type]} -- 截至日期，yyyy-MM-dd格式（含

    Keyword Arguments:
        temp_file {file path of str} -- 临时文件路径 (default: {None})

    Returns:
        [pandas.dataframe] -- 返回爬取到的数据集
    """
    # 实现逻辑：
    # 1. http申请数据，形成str
    # 2. 将str解析成dataframe
    # 3. 返回dataframe

    # HTTP请求数据：
    http_str = _read_http(fund_symbol, start_date, end_date, page_no=1)

    if not http_str:
        return None
    else:
        # 解析第一页：
        df, count_of_record = _htmlstr_2_df(http_str)
        # log.info('total count = {0}'.format(count_of_record))
        if count_of_record <= TTJJ_PAGE_SIZE:
            return df
        else:
            df_list = []
            df_list.append(df)
            # 计算还需要取的次数
            if count_of_record % TTJJ_PAGE_SIZE == 0:
                page_count = int(count_of_record/TTJJ_PAGE_SIZE) + 1
            else:
                page_count = int((count_of_record+1)/TTJJ_PAGE_SIZE) + 1
            # log.info('page_count index = ' + str(page_count))
            for page_index in range(1, page_count):
                # log.info('page index = ' + str(page_index))
                http_str = _read_http(fund_symbol, start_date, end_date, page_no=page_index+1)
                df, c = _htmlstr_2_df(http_str)
                df_list.append(df)
            # df合并
            df = pd.concat(df_list)
            df.sort_values(by=['FSRQ'], inplace=True)
            df.reset_index(inplace=True, drop=True)
            return df

        # 解析内容：
        df, count = _htmlstr_2_df(http_str)
        log.info('count = ' + str(count))
        if count > TTJJ_PAGE_SIZE:
            page_count = 1
            if count % TTJJ_PAGE_SIZE == 0:
                page_count = int(count/TTJJ_PAGE_SIZE) + 1
            else:
                page_count = int((count+1)/TTJJ_PAGE_SIZE) + 1
            for page_index in range(2, page_count):
                log.info('page index = ' + str(page_index))
        return df


def data_merge(fund_symbol, new_df):
    # 合并，将新的数据，合并到老的数据文件中
    # data_file_path = r'data/ttjj/{0}.csv'.format(fund_symbol)
    data_file_path = DATA_CI.FUND_DATA_DIR + '{0}.csv'.format(fund_symbol)

    try:
        df_old = pd.read_csv(data_file_path)
        df = pd.concat([df_old, new_df])
    except FileNotFoundError:
        # 文件不存在，则新建文件
        df = new_df
    df.drop_duplicates(subset=['FSRQ'], keep='last', inplace=True)
    df.sort_values(by=['FSRQ'], inplace=True)
    df.to_csv(data_file_path, index=False)
    log.info('合并完成！')


def update_daily(fund_symbol, start_date, end_date=None):
    # 爬取数据，更新本地数据文件
    # 逻辑：(按基金逐个爬取)
    # 1. 爬取数据，形成df
    # 2. 更新本地文件
    # OVER

    if not end_date:
        end_date = datetime.datetime.today().strftime(DATA_CI.DATE_FORMAT)

    if type(fund_symbol) is str:
        fund_symbol_list = [fund_symbol]
    elif type(fund_symbol) is list:
        fund_symbol_list = fund_symbol
    else:
        log.info('参数错误, fund_symbol必须是str或list，现在是 {0}'.format(type(fund_symbol)))
        return

    for fund_id in fund_symbol_list:
        df = ant_fund(fund_symbol=fund_id, start_date=start_date, end_date=end_date)
        if df is not None and not df.empty:
            log.info('爬取{0}数据{1}条 ... '.format(fund_id, df.shape[0]))
            data_merge(fund_id, df)
            log.info('更新本地{0}数据文件完成！'.format(fund_id))
        else:
            log.info('{0} 获取数据为空'.format(fund_id))

    log.info('数据全部更新完毕')


if __name__ == "__main__":
    # 爬取后更新本地文件

    # # 爬取网页数据
    # df = ant_fund(fund_symbol='005918', start_date='2020-01-01', end_date='2020-01-31')
    # log.info(df)
    # # log.info(df.shape[0])

    start_date = '2018-01-01'
    end_date = '2020-03-27'
    # fund_symbol = '005918'
    fund_symbol = ['005918', '360008', '160416']
    # 360008， 005918
    update_daily(fund_symbol, start_date, end_date)



