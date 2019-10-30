import pandas as pd


if __name__ == "__main__":
    df = pd.DataFrame(columns=['A', 'B'])
    df['A'] = df.A.apply(str)
    print(df['A'].dtype)

    print(type(df.dtypes.tolist()))
    print(type(df.dtypes.tolist()[0]))
