import akshare as ak



if __name__ == "__main__":
    df = ak.fund_em_daily()
    df.to_csv(r'c:/temp/fund_nav_005918_OF.csv', index=False)
    pass
