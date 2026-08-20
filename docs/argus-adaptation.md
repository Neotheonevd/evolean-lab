# 从 Microsoft ArgusAgent 借鉴的机制

EvoLean Lab 借鉴 Microsoft ArgusAgent 数学 vertical 的证据纪律，但暂时不嵌入完整的 Manager、Planner、Engineer、Reviewer 四角色运行时。

## 已采用的原则

- **命题不可静默修改**：命题由版本号和精确文本的 SHA-256 摘要标识；修改命题必须创建新版本。
- **证据绑定内容**：证据绑定命题摘要，而不是时间戳。命题变化后，旧证据不会继续显示为有效。
- **状态实时推导**：命题状态应由现有证据计算，不在记录中手工写死。
- **路线不等于证明**：证明路线可以是 AND/OR 图，但即使所有子任务完成，也需要验证这些子任务确实推出目标。
- **证据层级分离**：机械验证、计算实验、文献内容和 Agent 判断不能相互冒充。
- **提出与审查分离**：生成候选路线的角色不能只凭自己的总结宣布任务完成。

## EvoLean Lab 的补充方向

ArgusAgent 当前数学文档把 `computational` 证据层保留在模型中，但明确说明还没有正式 producer。EvoLean Lab 已经拥有有限穷举和独立差分检查原型，下一步会把它们升级为 proof-producing producer：搜索器输出紧凑证书，Lean 或独立小检查器只负责验证证书。

## 当前文件

- `research/MATH_STATE.json`：命题版本和证据记录；
- `research/PROOF_GRAPH.json`：AND/OR 证明路线；
- `experiments/002-sidon-saturation/`：首个计算与 Lean 联合实验。

这些文件目前是数据契约原型，还不是完整的追加式账本实现。后续需要为以下性质增加自动测试：摘要一致性、版本不可覆盖、证据权限、状态推导和路线蕴含审查。
