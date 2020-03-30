#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2020/03/30 19:52:50
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
"""fdata是金融数据获取包

外部使用如下方式访问数据

```python
import equan.fdata as fd

fd.xxxxx(...)
```
"""

"""
交易日历

+ get_cal 获取交易日历中的日期

"""
from equan.fdata.data_api import (
    # 取得日历数据
    get_cal
)

"""
国内公募基金数据
"""
from equan.fdata.data_api import (
    # 基金日价格
    fund_daily_price
)
