import pandas as pd
import numpy as np


def find_cross_point():
    # 模拟 1000 天价格，然后绘制sma20， sma60
    # 输出所有的 gold-cross / dead-cross 的日期
    # 通过绘图来验证
    # df: date; sma20, sma60, position

    sampl_num = 1000
    sampl_max = 50.0
    sampl_min = 1.0
    sampl_sr = np.random.uniform(low=sampl_min, high=sampl_max, size=(sampl_num,))
    df = pd.DataFrame(sampl_sr)
    df.index = pd.date_range(start='1/1/2018', periods=sampl_num) 
    print(df)
    # TODO 绘制price价格
    # TODO 计算sma20, sma60
    # TODO 判断上穿、下穿标识
    #  绘图验证




def demo1():
    df = pd.DataFrame(columns=['A', 'B'])
    df['A'] = df.A.apply(str)
    print(df['A'].dtype)

    print(type(df.dtypes.tolist()))
    print(type(df.dtypes.tolist()[0]))


if __name__ == "__main__":
    find_cross_point()
