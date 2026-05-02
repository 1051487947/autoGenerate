# 第一本书优化路线图

日期：2026-05-02

书名：`我要送快递可是你非要我做董事长`

## 当前阶段判断

第一本书已经不再是“能不能生成”的阶段，而是进入“能不能稳定写成长篇”的阶段。

当前已经证明：

- 标题到故事种子、故事圣经、20 章大纲、章节生成的主链路成立。
- 20 章完整原稿曾经跑通。
- 3 章 V0.2 测试文本质量有亮点，主角职业烙印、行业质感和“签收”隐喻成立。
- 阅读站已经上线，可以外网浏览生成结果。

当前主要问题：

- V0.2/V0.3/V0.5 的新资产多数还停留在工程文件层，尚未完全接入 N8N 实际生成链路。
- 第一本书已有 `story_bible` 人设，但 `characters.json` 仍为空，独立人物卡未真正生成。
- 剧情线、人物线、关系线、感情线还没有进入稳定账本管理。
- Kimi 尚未正式作为正文主笔接入并回归测试。
- 现有 QA 仍偏粗，存在高分章节仍标记 rewrite/manual 的归一化问题。

## 昨天到现在已完成的优化

### 1. V0.2 长期资产层

新增并落地：

- 人物卡 Prompt 和 Schema。
- 金手指规则 Prompt 和 Schema。
- 文风圣经。
- 作者声音指纹。
- 反 AI 措辞审计。
- 因果规划。
- 伏笔规划。
- 长期账本占位。

代表文件：

```text
novel_factory/prompts/10_character_cards.md
novel_factory/prompts/11_golden_finger.md
novel_factory/prompts/12_style_bible.md
novel_factory/prompts/14_logic_causality_planner.md
novel_factory/prompts/15_foreshadow_planner.md
novel_factory/prompts/16_anti_ai_audit.md
```

### 2. V0.2 三章回归测试

生成项目：

```text
novel_projects/v02_3ch_smoke_20260501_1935
```

结果：

- 第 1 章：`骑手进董事会`
- 第 2 章：`PPT里一切正常`
- 第 3 章：`董事长下仓`

外部评价认为前三章有较强潜力：

- 林井安人物立住。
- 行业质感真实。
- “签收”隐喻有文学价值。
- 三章结构形成“质疑 -> 揭穿 -> 验证”的递进。

暴露问题：

- 高管群像偏工具人。
- “快递员当董事长”的制度可信度还需补丁。
- 主角判断略顺，缺少阶段性代价。

### 3. 阅读站部署

已部署外网阅读站：

```text
http://8.140.56.75:18088/
```

已支持：

- 每本书一个目录。
- 首页自动展示服务器生成过的书。
- 章节 HTML 阅读。
- favicon。
- 重建站点不会破坏 Nginx 挂载。

代表脚本：

```text
novel_factory/scripts/build_reader_site.py
```

### 4. V0.3 编辑反馈闭环

把外部评价转成可执行的工作流资产。

新增：

```text
18_editorial_diagnosis_from_feedback.md
19_institutional_plausibility_patch.md
20_antagonist_countermove_planner.md
21_protagonist_cost_failure_planner.md
22_motif_reader_promise_planner.md
```

目标：

- 让反派主动反制。
- 补制度可信度。
- 强制主角付代价。
- 追踪核心隐喻和读者承诺。

### 5. V0.5 30万字长篇模式

确认当前 20 章应作为第一卷或第一阶段，而不是完整书。

新增：

```text
23_long_novel_architect.md
24_volume_arc_planner.md
25_rolling_batch_20_planner.md
26_arc_continuity_auditor.md
```

推荐结构：

```text
第1卷  1-20章：被推上台，先活下来
第2卷  21-40章：建立真实信息网
第3卷  41-60章：制度改革反噬
第4卷  61-80章：资本和舆情局
第5卷  81-100章：创始人失联真相
第6卷  101-120章：重建规则，真正掌舵
```

### 6. 工厂通用化

检查并清理运行时 Prompt 中的第一本书硬编码。

已清理：

- 快递。
- 董事长。
- 林井安。
- 签收。
- 一线体感 vs PPT。
- 系统正常但现实爆仓。

结论：

- 小说工厂不用推翻。
- 第二本书可复用工厂。
- 第一本书题材内容应只存在于 `novel_projects/<book_id>` 内。

## 仍需优化的问题

### P0：资产完整性没有自动审计

当前 `characters.json` 仍可能为空，但流程不会主动报错。

需要新增：

```text
asset_completeness_auditor
review/asset_completeness_report.json
```

必须检查：

- `characters.json` 是否为空。
- `golden_finger.json` 是否还是占位。
- `style_bible.md` 是否还是“待生成”。
- `long_novel_architecture.json` 是否已生成。
- 章节生成后各类 ledger 是否回写。

### P0：第一本书人物卡未真正落地

当前男主林井安在 `story_bible.md` 中有人设，但 `bible/characters.json` 为空。

下一步必须先生成并保存：

```text
bible/characters.json
```

至少包含：

- 林井安。
- 彭凯茜。
- 许岩。
- 马静。
- 老周。
- 高承岳。

### P0：V0.3/V0.5 尚未接入 N8N 实际链路

目前新增 Prompt/Schema 已在服务器，但 N8N 主流程还没有完整使用它们。

需要接入：

```text
Institutional Plausibility Patch
Long Novel Architect
Volume Arc Planner
Antagonist Countermove Planner
Protagonist Cost Failure Planner
Motif Reader Promise Planner
Arc Continuity Auditor
```

### P1：Kimi 正文主笔尚未回归测试

推荐分工：

```text
GPT = 规划、逻辑、审稿、JSON
Kimi = 场景正文、章节合并、定向重写
```

需要用同一章节做 A/B：

- GPT 写正文版本。
- Kimi 写正文版本。
- GPT 审稿对比。

### P1：剧情线、人物线、关系线账本还不够实用

需要补强：

```text
memory/global_arc_ledger.json
memory/plot_thread_ledger.json
memory/character_arc_ledger.json
memory/relationship_ledger.json
memory/protagonist_cost_ledger.json
memory/motif_ledger.json
```

尤其是林井安和彭凯茜的关系线，建议先定位为：

```text
规则执行者 -> 有限协作 -> 事实同盟 -> 价值观靠近
```

不要过早写成明确爱情线。

### P1：QA Gate 需要归一化

现象：

- 第 1 章 QA 89，但仍 `needs_rewrite=true`、`needs_manual_review=true`。
- 第 3 章 QA 91，也被标记 rewrite/manual。

需要明确规则：

```text
major_conflict = true -> manual
total_score < 70 -> rewrite
70 <= total_score < 80 -> targeted rewrite
total_score >= 80 且无硬性违规 -> pass
```

### P2：合订本和阅读站自动发布还未完全节点化

阅读站可用，但 N8N 生成完后应自动触发：

```text
Finalize Full Book
-> Build Reader Site
-> Return Public URL
```

## 建议下一步推进顺序

### 第一步：补第一本书核心资产

先不要急着继续写第 21 章。

先补：

```text
bible/characters.json
bible/institutional_plausibility.json
bible/reader_promise.json
bible/long_novel_architecture.json
outline/volumes.json
```

目标是把“第一本书的脑子”先补完整。

### 第二步：做资产完整性审计

新增脚本或节点：

```text
novel_factory/scripts/audit_book_assets.py
```

让系统自动告诉我们：

```text
正文生成成功，但人物卡为空
正文生成成功，但长篇架构未生成
正文生成成功，但关系线账本未更新
```

### 第三步：改 N8N 主流程

把 V0.3/V0.5 的书籍级节点接入主流程：

```text
Character Cards
Institutional Plausibility
Long Novel Architect
Volume Arc Planner
```

把章节级节点接入 Worker：

```text
Antagonist Countermove
Protagonist Cost
Motif Plan
Anti-AI Audit
Style Audit
```

### 第四步：重跑第一本书前三章

不要先跑 20 章。

先跑：

```text
第1章-第3章
```

对比旧版：

- 林井安是否仍然立住。
- 高管是否更像真实权力动物。
- 制度补丁是否自然埋入。
- 主角是否有代价。
- “签收”隐喻是否还在，但不重复。

### 第五步：通过后再跑第1卷20章

前三章验证通过后，再跑：

```text
第1卷 1-20章
```

然后做：

```text
Arc Continuity Auditor
Asset Completeness Auditor
Reader Site Publish
```

## 近期最小可执行目标

下一轮建议只做一个小闭环：

```text
补齐第一本书 characters.json
补齐 institutional_plausibility.json
补齐 long_novel_architecture.json
补齐 volumes.json
做 asset completeness audit
```

完成后再动 N8N。
