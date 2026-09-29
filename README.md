# Spanmark

单根电缆上的 SSTDR 距离仿真。发射一条 m 序列，反射回来之后做相关，主峰以外的那个峰对应故障距离。

这是合成仿真，不是仪器，也不是实测数据集。默认波速只是仿真参数，不是某根电缆的标定值。

## 本仓库不收录别人的内容

这里只有 Spanmark 自己的代码、说明和图标。没有别人的波形、网表、探头记录、论文图或文案。测试在运行时自己生成序列，不提交外部数据文件。

## 它不是什么

不做多支路电网，不做 Simscape 网表，不读硬件探头，不区分电弧类型。那些是别的项目的事。

## 用法

```python
from spanmark import locate_fault

found = locate_fault(distance_m=50, reflection=-1.0, noise_std=0.0)
print(found.distance_m, found.lag_samples)
```

`reflection` 取 +1 近似开路，取 -1 近似短路。相关峰的符号跟反射系数一致。零延迟那一峰是直达波，搜峰时会跳过它。

## 许可

MIT。见 [LICENSE](LICENSE)。
