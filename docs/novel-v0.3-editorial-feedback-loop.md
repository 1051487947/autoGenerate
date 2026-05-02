# 小说工厂 V0.3 编辑反馈闭环

日期：2026-05-02

## 背景

用户提供了外部 AI 对前三章《我要送快递可是你非要我做董事长》的整体评价。评价认为现有开头的优势是：

- 林井安职业烙印鲜明，“快递员的世界理解方式”已经立住。
- 三章形成“质疑 -> 揭穿 -> 验证”的递进结构。
- “签收”从劳动动作升级为权力隐喻，是全书最值得保留的核心意象。
- 物流一线细节有真实感，“一线体感 vs 管理层 PPT”的冲突成立。

同时暴露了四个系统性问题：

- 高管和对手偏工具人，反制动作不够狡猾。
- “快递员被推成董事长”的制度可信度仍悬空。
- 主角前三章判断太准，阶段胜利略顺。
- 核心隐喻如果不建账本，后续容易从行业现实主义退化成普通爽文。

## 结论

这不是简单加一个“AI 润色节点”能解决的问题。应该新增编辑反馈闭环，把外部评价转成可执行的数据和节点。

## 新增 Prompt

```text
novel_factory/prompts/18_editorial_diagnosis_from_feedback.md
novel_factory/prompts/19_institutional_plausibility_patch.md
novel_factory/prompts/20_antagonist_countermove_planner.md
novel_factory/prompts/21_protagonist_cost_failure_planner.md
novel_factory/prompts/22_motif_reader_promise_planner.md
```

## 新增 Schema

```text
novel_factory/schemas/editorial_diagnosis.schema.json
novel_factory/schemas/institutional_plausibility.schema.json
novel_factory/schemas/antagonist_countermove.schema.json
novel_factory/schemas/protagonist_cost_plan.schema.json
novel_factory/schemas/motif_plan.schema.json
```

## 新增项目文件

新书初始化时额外创建：

```text
bible/institutional_plausibility.json
memory/protagonist_cost_ledger.json
memory/motif_ledger.json
memory/editorial_feedback_ledger.json
```

## 推荐 N8N 改造

书籍级生成增加：

```text
GPT Institutional Plausibility Patch
-> Save Institutional Plausibility
```

人工或外部 AI 评价后增加：

```text
Editorial Diagnosis From Feedback
-> Save Editorial Diagnosis
-> Update Editorial Feedback Ledger
```

章节循环在 `Chapter Task` 前增加：

```text
Build Chapter Context
-> Logic Causality Planner
-> Foreshadow Planner
-> Antagonist Countermove Planner
-> Protagonist Cost Failure Planner
-> Motif Reader Promise Planner
-> Chapter Task
```

章节生成后在 QA 前检查：

```text
Anti-AI Audit
Style Consistency Auditor
Critic Auditor
QA Gate
```

## QA Gate 新规则

- 本章对手没有主动反制动作：回退到 `Antagonist Countermove Planner`。
- 主角连续 3 章无明显误判或代价：强制进入 `Protagonist Cost Failure Planner` 重排。
- 强设定被角色质疑但没有制度补丁：暂停人工确认。
- 核心隐喻连续 3 章同一种表达方式：进入 `Motif Reader Promise Planner` 重排。
- `logic_ai_risk > 45`：定向重写，不只做语言润色。

## 关于 Skill

暂时不建议把这些直接做成 Codex Skill 来替代 N8N。原因：

- N8N 运行时需要稳定文件、JSON Schema、HTTP 节点和账本回写。
- Skill 更适合沉淀“我作为审稿/架构助手的工作方法”，用于之后反复审稿、生成改造清单、辅助调试工作流。

建议顺序：

1. 先把 V0.3 Prompt 和 Schema 接入 N8N。
2. 跑 3 章回归，看反派反制、主角代价、制度补丁和签收隐喻是否进入正文。
3. 再把成熟的审稿标准沉淀为 Codex Skill，供后续人工评价、章节复盘、重写策略使用。
