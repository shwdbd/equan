# fdata数据模块的说明

应用于 v0.2版本

fdata模块是金融数据访问的api模块，其负责对于已有的金融数据提供获取，不负责金融数据的采集和存储。

所有fdata的api都采用如下方式，即采用最外层api的方式：

```python
import equan.fdata as data_api

df = data_api.get_stock()
```

其下的子模块，如stock、fund等，只是不同数据类型的实现，外部不应该直接访问

另外，fdata有自己独立的日志体系。

;)
