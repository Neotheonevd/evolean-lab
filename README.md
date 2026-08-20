# EvoLean Lab：演化式形式化数学实验室

EvoLean Lab 是一个开放的 AI 数学研究实验项目。我们希望把“选择问题、生成猜想、搜索反例、演化证明路线、查阅文献、机械验证和独立审查”组织成一套可复现、可审计的长期研究流程。

项目的长期目标，是在专家复核和 Lean 形式验证的约束下，完成具有真实研究价值的新结果。现阶段仍是早期原型，不宣称已经实现自主数学发现。

## 当前能力

- 不可变的数学问题与候选命题记录；
- 多目标适应度和保持多样性的候选选择；
- 变异、代际和谱系追踪；
- 追加式研究事件与 JSON 快照；
- Lean 4 + Mathlib 验证适配器；
- Codex 工作区任务队列与独立付费 API 的接口边界；
- 可复现的有限搜索、反例检查和单元测试。

## 当前实验

- [实验 001：课题侦察](experiments/001-topic-scout/README.md)：选择有限极值组合数学作为首个领域，并用 Lean 验证 Sidon 集与正差搜索之间的关键桥梁。
- [实验 002：极小的极大 Sidon 集](experiments/002-sidon-saturation/README.md)：研究按包含关系极大的 Sidon 集能有多小。项目已经得到 `s(43)=6` 的计算验证，以及 Lean 验证的 `M(6) ≥ 63` 新下界见证。
- [实验 002 完整中文报告](experiments/002-sidon-saturation/EXPERIMENT_REPORT.zh-CN.md)：记录命题生成、错误猜想反驳、独立穷举、Lean 核验和文献查重。
- [实验 003：Ruzsa 构造中的对数缺口](experiments/003-ruzsa-log-gap/README.md)：转向 Erdős Problem #156，研究能否把极大 Sidon 集的已知 `O((N log N)^(1/3))` 上界改进到猜想中的 `O(N^(1/3))`。
- [实验 003 的完整 Lean 修补桥梁](experiments/003-ruzsa-log-gap/RepairLemma.lean)：已从“未阻塞点只落在旧类或异常类 `E`”严格推出 `|A\A₀|≤2K+|E|`。阻塞接口、新锚点到异常类的注入、非锚点差值注入和非零 `q` 倍数计数均已机械验证。
- [实验 003 的 Singer 有理三元参数化](experiments/003-ruzsa-log-gap/SingerTripleParam.lean)：把固定剩余类的 `p+1` 个三元表示统一写成单参数有限域有理式；代数重构已经 Lean 验证，Singer 成员关系调用文献的唯一混合表示定理。
- [实验 003 的结构高度与精确校准](experiments/003-ruzsa-log-gap/README.md)：已测试自由/超图搜索、CP-SAT、有限域迹高度、Singer 平移和完整仿射轨道；`p=11,M=4` 最佳坏类数为 49，`p=13,M=4` 为 55。失败路线和证据边界均被保留。
- [从 Microsoft ArgusAgent 借鉴的机制](docs/argus-adaptation.md)：命题版本、内容摘要绑定、证据分级和 AND/OR 证明路线。

### 当前证明前沿

当前冻结的主目标是 Erdős Problem #156。取 `q=p²+p+1`，Ruzsa 使用大小为 `p+1` 的 Singer 差集并为每个元素选择整数高度。随机高度需要 coupon-collector/union-bound 产生的对数因子；本项目正在寻找确定性替代。

目前已经得到：

- `VERIFIED`：极大 Sidon 集的阻塞刻画，以及端到端有限修补界
  `|A\A₀|≤2 floor((N-1)/q)+t`；因此“线性异常类数推出 `O(N^(1/3))`”的确定性桥梁已经闭合；
- `VERIFIED`：Singer 唯一混合表示的有理式代数重构。固定目标群元素 `R` 后，全部三元表示可由一个 Singer 参数 `V` 描述；成员关系使用已有文献定理；
- `COMPUTATIONALLY_VERIFIED`：当前最佳有限见证为 `p=11,M=4` 的 49 个坏类，以及 `p=13,M=4` 的 55 个坏类（覆盖 `615/676` 个目标单元）；这些不是全局最优或无限族证明；
- 已排除的主线：完整仿射轨道搬运不能改善现有固定高度；总二次能量 `O(p)` 虽是充分条件，但与当前优良见证的量级不符，已停止作为证明主线；
- 确定性容量障碍：必须取 `0<c<1/2`，因为每个剩余类至多产生约 `(p+1)/2` 个不同高度；
- `UNRESOLVED`：构造 Singer 高度，使出现缺层的额外剩余类数为 `O(p)`。这被登记为 `LINEAR-RESIDUE-DEFECT`，是当前唯一的核心构造定理；
- 当前精确障碍：新的 carry twist 已由 Lean 验证：若 `λq≡1 (mod M)`，改用 `d̃(b)=d(b)+λb (mod M)`，就能完全吸收循环覆盖方程中的进位。对 `q=p²+p+1` 且 `M | p+1` 可直接取 `λ=1`。这解决循环层的代数化，但不解决零绕数的整数提升。
- 最新缺陷分解：当前最佳见证中，`p=11` 的 54 个缺失单元分成 35 个循环未覆盖和 19 个仅绕数失败；`p=13` 的 61 个分成 39+22。Lean 已验证“真实缺陷 = 循环缺陷 ⊔ wrap-only 缺陷”，因此最后构造定理现在拆成两个并列的线性上界。
- 二阶矩路线审判：普通角色和平方根消去/Parseval 无法推出近乎处处覆盖。小参数审计也否定了“每层精确等重”作为必要结构（`p=11` 无一个等重剩余类，却仍有 86 个循环满射类）。当前正确的较弱目标是 `TWISTED-CYCLIC-SURJECTIVITY`：扭转后的层映射对除 `O(p)` 个目标单元外满射。

因此实验 003 并不是只做反例搜索；反例用于淘汰错误的中间路线，主流程始终朝向“构造高度 → 控制坏剩余类 → 修补成极大 Sidon 集 → 推出 Erdős #156”。

我们严格区分证据等级：

- `VERIFIED`：精确形式命题已经通过 Lean；
- `COMPUTATIONALLY_VERIFIED`：有限穷举或数值程序已经检查，但尚未生成完整 Lean 证书；
- `SUPPORTED`：有实验、文献或推理支持，但不是证明；
- `REFUTED`：存在已经核验的反例；
- `UNRESOLVED`：尚未解决。

## 快速开始

需要 Python 3.11 或更高版本。

```powershell
$env:PYTHONPATH = "src"
python -m evolean_lab.cli init
python -m evolean_lab.cli demo-cycle
python -m evolean_lab.cli status
python -m unittest discover -s tests -v
```

也可以在虚拟环境中执行 `pip install -e .`，随后使用命令行入口 `evolean`。

Lean 实验需要本地安装 Lean 4 和 Mathlib。仓库不包含庞大的 Mathlib 缓存，只保存可复核的 `.lean` 证明文件。

## 可信边界

只有 Lean 以退出码 0 完成编译，并通过证明洞与公理检查后，精确形式命题才可以标记为 `VERIFIED`。有限计算能够提供反例、证书或强证据，但不能自动证明无限命题。Lean 代码通过也只说明形式命题成立；仍需人工检查它是否忠实表达原始数学命题。

## 如何参与

目前特别需要以下方向的协作者：

- 组合数学、数论、图论等领域的问题选择与同行审查；
- Lean 4 / Mathlib 形式化；
- SAT、SMT、约束规划与计算证明证书；
- 演化计算、树搜索和多 Agent 调度；
- 数学文献检索与新颖性审计；
- 可用于长期实验的模型 Token 和计算资源。

欢迎提交 Issue、实验建议和 Pull Request。任何“新定理”声明在公开之前，都必须经过文献查重、独立复核和与证据等级相匹配的表述。

## 项目文档

- [当前研究状态：我们走到了哪里？](docs/current-status.md)
- [研究愿景](docs/vision.md)
- [系统架构](docs/architecture.md)
- [ArgusAgent 机制借鉴](docs/argus-adaptation.md)
- [结构化命题与证据账本](research/MATH_STATE.json)
- [证明路线图](research/PROOF_GRAPH.json)

## 许可证

项目目前尚未选择开源许可证。仓库公开可见并不自动授予复制、修改或再发布的权利；确定协作政策后再添加合适的许可证。
