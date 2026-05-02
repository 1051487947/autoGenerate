# 小说工厂 V0.5：30万字长篇模式

日期：2026-05-02

## 核心结论

当前前 20 章可以放大为整体一本书，但不应该直接把 20 章拉长成 30 万字。

正确做法是：

```text
前20章 = 第一卷 / 第一阶段 / 试写样章
30万字全书 = 约100到120章，5到6卷，每卷18到25章
```

也就是说，20 章负责证明题材、主角、文风和核心矛盾成立；30 万字需要额外的长篇架构层来管理剧情线、人物线、关系线、反派升级和伏笔回收。

## 推荐全书结构

以《我要送快递可是你非要我做董事长》为例，可以这样放大：

| 卷 | 章节 | 阶段功能 |
| --- | ---: | --- |
| 第一卷：被推上台，先活下来 | 1-20 | 陆小川被迫上任，识破信息失真，稳住第一场运营危机 |
| 第二卷：建立真实信息网 | 21-40 | 绕开总部汇报，建立一线、客服、财务、站点情报链 |
| 第三卷：制度改革反噬 | 41-60 | 推动异常闭环、罚款复核、结算透明，触动内部利益 |
| 第四卷：资本和舆情局 | 61-80 | 竞对、资本、媒体同时施压，主角第一次遭遇大败 |
| 第五卷：创始人失联真相 | 81-100 | 授权、代持、旧债、内鬼线集中揭开 |
| 第六卷：重建规则 | 101-120 | 稳住核心网络，清除关键内鬼，拿下真正掌舵资格 |

## 新增 Prompt

```text
novel_factory/prompts/23_long_novel_architect.md
novel_factory/prompts/24_volume_arc_planner.md
novel_factory/prompts/25_rolling_batch_20_planner.md
novel_factory/prompts/26_arc_continuity_auditor.md
```

## 新增 Schema

```text
novel_factory/schemas/long_novel_architecture.schema.json
novel_factory/schemas/volume_arc.schema.json
novel_factory/schemas/batch_outline.schema.json
novel_factory/schemas/arc_continuity_audit.schema.json
```

## 新增项目文件

新书初始化时额外创建：

```text
bible/long_novel_architecture.json
outline/volumes.json
outline/current_batch_outline.json
memory/global_arc_ledger.json
memory/plot_thread_ledger.json
memory/relationship_ledger.json
review/arc_continuity_report.json
```

## N8N 长篇模式

长篇模式不要一次性细化 120 章。推荐：

```text
Title
-> Story Seed
-> Story Bible
-> Character Cards
-> Institutional Plausibility
-> Long Novel Architect
-> Volume Arc Planner
-> Rolling Batch 20 Planner
-> Chapter Worker x 20
-> Arc Continuity Auditor
-> Next Batch
```

## 为什么要滚动20章

一次性生成 120 章详细大纲会有三个问题：

- 前面章节正文写出来后，后面大纲很快过时。
- 人物关系和伏笔会变成纸面计划，缺少根据正文结果的调整。
- 模型容易重复冲突模式，比如每卷都写成“发现造假、下现场、打脸高管”。

滚动 20 章的好处：

- 全书方向稳定。
- 每 20 章根据已生成正文校准。
- 允许人物和关系自然生长。

## 下一步建议

先不要直接生成 120 章正文。

建议顺序：

1. 先把当前 20 章定位为第一卷。
2. 生成 `long_novel_architecture.json`。
3. 生成 6 卷 `volumes.json`。
4. 只细化第 21-40 章批次。
5. 接 Kimi 生成第 21-23 章，做质量对比。
6. 如果人物线、关系线、反派阻力明显更稳，再继续后续批次。
