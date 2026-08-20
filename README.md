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
- [实验 002：极小的极大 Sidon 集](experiments/002-sidon-saturation/README.md)：研究按包含关系极大的 Sidon 集能有多小。项目已经得到 `s(43)=6` 的计算验证，以及 Lean 验证的 `M(6) ≥ 61` 新下界见证。
- [实验 002 完整中文报告](experiments/002-sidon-saturation/EXPERIMENT_REPORT.zh-CN.md)：记录命题生成、错误猜想反驳、独立穷举、Lean 核验和文献查重。
- [从 Microsoft ArgusAgent 借鉴的机制](docs/argus-adaptation.md)：命题版本、内容摘要绑定、证据分级和 AND/OR 证明路线。

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

- [研究愿景](docs/vision.md)
- [系统架构](docs/architecture.md)
- [ArgusAgent 机制借鉴](docs/argus-adaptation.md)
- [结构化命题与证据账本](research/MATH_STATE.json)
- [证明路线图](research/PROOF_GRAPH.json)

## 许可证

项目目前尚未选择开源许可证。仓库公开可见并不自动授予复制、修改或再发布的权利；确定协作政策后再添加合适的许可证。
