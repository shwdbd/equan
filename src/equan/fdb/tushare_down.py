import pandas as pd
from equan.backtest.tl import log, tushare
import os
import time


ROOT_DIR = 'c:\\temp\\tushare\\'


if __name__ == "__main__":
    df = tushare.stock_basic()
    total = df.shape[0]
    print(df.shape[0])
    # df.to_csv(ROOT_DIR+'stock_basic.csv', index=False)

    stockid_list = list(df['ts_code'])
    for idx, stock_id in enumerate(stockid_list):
        file = ROOT_DIR + stock_id + ".csv"
        if os.path.exists(file)==False:
            # 下载:
            while os.path.exists(file)==False:
                try:
                    df = tushare.daily(ts_code=stock_id)
                    df.to_csv(file, index=False)
                    print('{0}/{1} downloaled {2}'.format(idx, total, file))
                except Exception as err:
                    print('下载异常, {0}' + str(err))
                    time.sleep(20)
                    print('暂停结束 ... ')
            
    
