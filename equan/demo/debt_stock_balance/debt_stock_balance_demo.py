#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   debt_stock_balance_demo.py
@Time    :   2019/11/21 08:36:59
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   股债平衡策略 临摹代码
'''


class Account():
    """
    账户类，模拟账户的各种行为
    """

    def __init__(self, stock=0.5, bond=0.5, rebalance_ratio=0.55):
        """
        初始化函数，记录初始账户股票和债券的比例以及账户净值
        初始账户净值为1

        Keyword Arguments:
            stock {float} -- 股票比例 (default: {0.5})
            bond {float} -- 债券比例 (default: {0.5})
            rebalance_ratio {float} -- [description] (default: {0.55})
        """
        self.stock_ratio = stock        # 股票资产比例
        self.bond_ratio = bond          # 债券资产比例
        self.balance_ratio = {'stock': stock,
            'bond': bond}   # 调仓时的目标比例，此处与初始值相同
        self.rebalance_ratio = rebalance_ratio  # 调仓阈值
        self.net_value = 1              # 初始账户净值
        self.rebalance_record = {}      # 记录策略调仓记录，检查时用
        self.balance = {}               # 记录账户策略表现净值，检查时用

    def rebalance(self):
        """
        账户再平衡，将股票和债券比例调整回目标比例
        """
        self.stock_ratio = self.balance_ratio['stock']
        self.bond_ratio = self.balance_ratio['bond']

    def update_ratio(self, daily_series):
        """
        根据每日收益率数据更新股票和债券持仓比例和策略净值

        Arguments:
            daily_series {[type]} -- 两种资产的收益率，pandas series：date|stock股票收益率, bond债券收益率
        """
        # 股票资产的净值
        stock_net = self.stock_ratio * self.net_value * (1 + daily_series['stock'])
        # 债券资产的净值
        bond_net = self.bond_ratio * self.net_value * (1 + daily_series['bond']

        # 更新账户总体净值，股票比例，债券比例
        self.net_value=stock_net + bond_net
        self.stock_ratio=stock_net / self.net_value   # 更新股票仓位比例
        self.bond_ratio=bond_net / self.net_value     # 更新债券仓位比例
        # 记录账户净值
        self.balance[daily_series.name]=self.net_value

    def check_rebalance(self):
        """
        检查账户是否需要再平衡

        return:boolean 任何一种资产超过 rebalance_retio 返回 True
        """
        return (self.stock_ratio>=self.rebalance_ratio) or self.bond_ratio>=self.rebalance_ratio()


    def data_in (self, daily_series):
        """
        处理每天进来的新数据
        根据u当日涨跌数据计算账户变动
        此方法设计作为参数传递给pandas.apply()函数
        
        Arguments:
            daily_series series -- 单日股票和债券收益率，index为['stock', 'bond']
        return 返回与 daily_series结构相同的series，分别是stock和bond比例更新后的结果
        """
        # 更新股债资产持仓比例和账户净值，记录账户净值
        self.update_ratio(daily_series)
        # 检查是否rebalance
        if self.check_rebalance():
            # 记录调仓日期和调仓前的股票债券比例
            self.rebalance_recor[daily_series.name] = {'stock':self.stock_ratio, 'bond':self.bond_ratio}
            # 调仓到目标比例
            self.rebalance()
        else:
            pass

        return pd.series( {'stock':self.stock_ratio, 'bond':self.bond_ratio}, name=daily_series.name )



if __name__ == "__main__":
    # 159922嘉实中证500ETF 和 511010国泰上证5年期ETF
    change = pd.read_vsv('', index_col=0).dropna()
    change.columns =['stock', 'bond']   # 两列收益率

    

    # 获取测试起止时间
    test_range = [change.index[0], change.index[-1]]
    print( test_range )

    # 计算benchmark收益率
    # 从tushare获取沪深300收盘数据
    hs300 = ts.get_k_data('hs300', start='2013-01-01', end='2017-8-1').set_index('date')['close']
    # 计算日涨跌幅
    hs300 = (hs300 - hs300.shift(1)) / hs300.shift(1)
    # 修改 series.name, pd.concate时可以直接转为名称
    hs300.name = 'hs300'
    # 截取测试对应时间段数据
    hs300 = hs300[ (hs300.index>=test_range[0]) & (hs300.index<=test_range[-1]) ]
    # 计算累计收益
    hs300 = (hs300+1).cumprod()


    # 创建Account对象
    account = Account()

    # 对收益率数据调用 account.data_in() 方法，每日资产比例变化结果存入 profolio_ratio 变量
    profolio_ratio = change.apply( account.data_in, axis=1 )

    # 从account中读取调仓记录，可以看到至少有一个是超过55%的比例的
    rebalance_record = pd.DataFrame( account.rebalance_record ).T

    # 从account中读取账户净值
    net_value = pd.Series(account.balance, name='strategy')

    # 绘制净值曲线：
    returns = pd.concate([net_value, hs300], axis=1)
    return.plot(figsize=(13, 9))
    plt.show()
