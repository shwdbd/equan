
import pandas as pd


data = {
    'date' : ['20190101', '20190101', '20190102', '20190102', '20190103'],
    'symbol' : ['600016', 'CASH', '600016', 'CASH', 'CASH'],
    'balance' : [5, 5, 4, 6, 10],
}
df = pd.DataFrame(data)

print(df)

df.set_index(['date', 'symbol'], inplace=True)

print(df)

print('切片:')
print(df.loc[ ('20190102', slice(None)) , :] )  # ? slice函数

print('转 dict :')
data_dict = {}
for d in df.index.levels[0]:
    # data_dict[d] = df.loc[ (d, slice(None)) , :]
    sub_df = df.loc[ (d, slice(None)) , :].reset_index(level='date', drop=True)
    # print( df.loc[ (d, slice(None)) , :].reset_index(level='date', drop=True) )
    data_dict[d] = sub_df

print(data_dict)
