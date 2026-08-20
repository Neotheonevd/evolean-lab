# 实验 002：极小的极大 Sidon 集

## 问题

令 `s(N)` 表示 `[1,N]` 中按包含关系极大的 Sidon 集的最小大小。本实验研究它的精确小值、一般界和极值结构。

一般方向并非空白：Ruzsa 在 1998 年研究过 small maximal Sidon sets。任何新颖性声明都必须在阅读相关文献后重新审计。

## 第一轮结果：`s(43)=6`

精确扫描最初得到的转移点为 `2,5,11,23`，一度诱导出错误的倍增规律。固定五元素搜索主动推翻了这一规律，并得到：

- 五元素 Sidon 集最多饱和到 `[1,42]`；
- `{1,2,4,13,32,37}` 是 `[1,43]` 中六元素极大 Sidon 集。

`Saturation43.lean` 对六元素上界见证进行 Lean 核验；`independent_difference_check.py` 使用独立的正差实现，检查 `[1,43]` 中大小 1 至 5 的全部 1,099,295 个子集，没有发现极大 Sidon 集。

因此完整等式当前是 `COMPUTATIONALLY_VERIFIED`；其中上界证书是 Lean `VERIFIED`，穷举下界尚未转换为 Lean 证明证书。详细过程见 [完整中文实验报告](EXPERIMENT_REPORT.zh-CN.md)。

## 演化续跑：六元素下界

固定随机种子的演化种群搜索找到 `{22,30,31,33,43,58}`。该六元素 Sidon 集在 `[1,61]` 中按包含关系极大。`Saturation43.lean` 已机械核验这个见证，因此：

`M(6) ≥ 61` 为 `VERIFIED`，

其中 `M(k)` 表示一个 `k` 元 Sidon 集能够饱和的最长初始区间。

见证在第 129 代出现；搜索运行到第 1500 代没有继续改进。但搜索停滞不是最优性证明，所以 `M(6)=61` 仍只是 `PROPOSED`。

复现实验：

```powershell
python evolutionary_order_scan.py --order 6 --limit 100 --population 500 --generations 1500 --output order6-evolution.json
```

## 主要文件

- `saturation_scan.py`：小规模精确扫描；
- `fixed_order_scan.py`：固定元素数的完整枚举；
- `find_witness.py`：寻找指定区间的极大见证；
- `independent_difference_check.py`：基于正差的独立复核；
- `evolutionary_order_scan.py`：演化式见证搜索；
- `Saturation43.lean`：`s(43)≤6` 与 `M(6)≥61` 的 Lean 证书；
- `order6-evolution.json`：六元素搜索轨迹。

## 下一步

1. 为 `s(43)>5` 生成 Lean 可检查的穷举证书；
2. 使用 SAT/约束规划判断是否存在六元素集合饱和 `[1,62]`；
3. 研究 `M(k)` 的一般上下界和极值见证结构；
4. 系统阅读 Ruzsa 及后续文献，确认精确小值是否已有记录。
