# 系统架构

## 研究循环

```text
问题池 → 可行性排序 → 冻结命题
   → 证明路线与引理种群
   ↔ 反例与审查种群
   → 选择、变异、迁移、归档
   → 计算证据 / 文献证据 / Lean 门禁
   → VERIFIED / REFUTED / SUPPORTED / UNRESOLVED
```

## 核心记录

- `Problem`：不可变的原始问题和来源；
- `Candidate`：正在演化的证明计划、引理、反例或策略；
- `Fitness`：多目标适应度，仅用于搜索，绝不是数学证据；
- `ResearchEvent`：追加式审计记录；
- `VerificationResult`：验证命令、输出、产物与证据状态。

## 命题与证据

借鉴 Microsoft ArgusAgent 的数学工作流，EvoLean Lab 逐步采用以下约束：

- 命题修改必须产生新版本；
- 证据绑定精确命题文本的 SHA-256 摘要；
- 命题状态从证据推导，不手工保存；
- AND/OR 路线完成不等于主命题已经证明；
- 机械、计算、文献和 Agent 判断属于不同证据层级；
- 提出方案与独立审查应当分离。

当前原型见 `research/MATH_STATE.json` 与 `research/PROOF_GRAPH.json`。

## 计划中的适配器

- LLM 命题生成、变异与证明规划；
- 文献检索与 Mathlib 前提检索；
- 有限穷举、SAT、SMT 和计算机代数；
- 岛屿模型与多种群迁移；
- 新颖性审计、基准测试和可复核证书生成。

核心包保持与具体模型无关，使不同模型和搜索算法能够在同一证据标准下比较。

## 模型后端与计费边界

`ProposalProvider` 是统一接口。

- `CodexWorkspaceProvider` 为交互式 Codex 任务生成有界的本地作业；只有 Codex 真正处理作业时才消耗 Codex 使用额度。
- `OpenAIAPIProvider` 是默认关闭的独立 API 接口边界。启用前必须配置项目、密钥管理、预算和评测。

不能假设 Codex 额度等于 API 余额。每个候选都应记录实际模型提供方、模型标识和用量元数据。
