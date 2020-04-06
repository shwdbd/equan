
import tushare as ts

TOKEN = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'




if __name__ == "__main__":
    ts.set_token(TOKEN)

    pro = ts.pro_api()

    # df = pro.fund_basic(market='O')
    # df.to_csv(r'c:/temp/fund_basic_o.csv', index=False)
    # 005918
    # 005918.OF 场外
    # 场内 000000.SH or 00000.SZ

    # df = pro.fund_daily(ts_code='005918', start_date='20180101', end_date='20200406')
    # df = pro.fund_daily(trade_date='20200403')
    # df.to_csv(r'c:/temp/fund_daily_005918_OF.csv', index=False)

    df = pro.fund_nav(ts_code='005918.OF')
    df.to_csv(r'c:/temp/fund_nav_005918_OF.csv', index=False)
