# N8N 小说长期记忆与去 AI 味优化方案

日期：2026-04-27

## 核心判断

后续优化 N8N 小说工作流时，不应只新增“AI 润色节点”。很多 AI 味并不是句子问题，而是故事机制问题：

- 剧情太顺。
- 线索出现得太刚好。
- 人物总能说正确的话。
- 主角连续判断正确。
- 事件像“作者想推进所以发生”，缺少前因、获利者、代价和信息缺口。

因此要新增长期故事记忆层，让每章生成前先被“因果、伏笔、人物弧光”约束。

## 新增三类账本

建议在每本书的 `memory/` 目录下新增：

```text
memory/foreshadow_ledger.json
memory/character_arc_ledger.json
memory/causality_ledger.json
```

### 伏笔账本

记录伏笔的生命周期：

- 伏笔 ID。
- 类型：微伏笔、中伏笔、主线伏笔。
- 首次埋设章节。
- 强化章节。
- 预计回收章节。
- 实际回收章节。
- 当前状态：open、reinforced、paid_off、abandoned。
- 是否太直白。
- 是否需要延迟回收。

### 人物弧光账本

记录人物不是“功能性工具人”，而是持续变化的人：

- 当前欲望。
- 当前误判。
- 当前恐惧。
- 最近付出的代价。
- 最近一次不体面的选择。
- 关系变化。
- 价值观裂缝。
- 是否连续太正确、太理性、太会说话。

### 因果账本

记录事件发生的前因后果：

- 本章事件为什么现在发生。
- 谁推动了事件。
- 谁获利。
- 谁付代价。
- 主角掌握了什么信息。
- 主角缺失了什么信息。
- 主角本章犯了什么判断错误。
- 该事件会推迟/触发哪些后续结果。

## 人物卡与金手指设计

当前系统已经有“人物卡”的雏形，但还不是完整的人物卡系统。

已有基础：

- 初始化脚本会创建 `bible/characters.json`。
- `story_bible.md` 会要求生成主角设定、主要配角设定、主要反派和阻力系统。
- `scene_card.schema.json` 中每个场景已有 `characters` 字段。
- `memory_update.schema.json` 中已有 `character_state_changes` 和 `relationship_changes`。

当前缺口：

- 没有独立的 `character_card.schema.json`。
- 没有单独的 `Character Card Builder` 节点。
- 没有把人物卡稳定注入 `Build Chapter Context`。
- 没有人物弧光字段，例如误判、羞耻点、私人习惯、说话边界、不能连续正确等。

建议新增：

```text
bible/characters.json
memory/character_arc_ledger.json
```

`bible/characters.json` 偏静态，记录人物底层设定；`memory/character_arc_ledger.json` 偏动态，记录人物在章节中的变化。

人物卡建议字段：

```json
{
  "character_id": "protagonist",
  "name": "主角姓名",
  "role": "protagonist",
  "surface_goal": "表层目标",
  "deep_desire": "深层欲望",
  "public_mask": "对外表现",
  "private_wound": "内在伤口",
  "core_contradiction": "核心矛盾",
  "speech_style": "说话风格",
  "habit_echo": ["可反复出现的人物习惯"],
  "competence": ["擅长什么"],
  "blind_spots": ["稳定盲区"],
  "wrong_beliefs": ["错误信念"],
  "relationship_edges": [],
  "forbidden_behaviors": ["不能违背的人设边界"]
}
```

金手指目前也只有雏形，还没有独立文件或 Schema。现在它大多隐藏在：

- `story_seed.core_hook`
- `story_seed.protagonist_seed`
- `story_bible.md` 的“爽点机制”
- 章节大纲中的解决问题方式

但中长篇最好把金手指单独建模，否则容易出现：

- 能力边界越来越松。
- 每次卡剧情都临时加能力。
- 主角赢得太轻松。
- 代价和限制不稳定。
- 爽点重复。

建议新增：

```text
bible/golden_finger.json
memory/golden_finger_ledger.json
```

`bible/golden_finger.json` 记录能力规则；`memory/golden_finger_ledger.json` 记录每章使用、升级、代价、误用。

金手指建议字段：

```json
{
  "name": "金手指名称",
  "type": "经验/系统/异能/资源/身份/信息差/工具",
  "origin": "来源",
  "activation_condition": "触发条件",
  "visible_effect": "表面效果",
  "true_mechanism": "真实机制",
  "limitations": ["限制"],
  "costs": ["代价"],
  "failure_modes": ["失效方式"],
  "growth_stages": [],
  "misuse_risks": ["误用风险"],
  "anti_deus_ex_machina_rules": [
    "不能无代价解决核心冲突",
    "不能连续多章让主角无损获胜",
    "每次升级必须有前置铺垫"
  ]
}
```

建议加入章节上下文：

- 本章允许使用的金手指能力。
- 本章禁止使用的金手指能力。
- 本章使用能力需要付出的代价。
- 本章是否必须让金手指失误、误判或产生副作用。

对于《我要送快递可是你非要我做董事长》这类标题，金手指不一定是玄幻能力，也可以是“职业经验型金手指”：

- 主角熟悉末端配送真实链路。
- 能从单号、路线、时段、投诉中看出管理系统的问题。
- 比董事会更懂一线成本和真实阻塞。
- 限制是：他不懂资本话术、法务博弈、董事会规则。
- 代价是：他越用一线方式解决问题，越得罪坐在系统上获利的人。

这类金手指更适合现实题材，也更不容易显得廉价。

## 改造后的章节循环

目标流程：

```text
Build Chapter Context
-> Foreshadow Planner
-> Logic Causality Planner
-> Chapter Task
-> Scene Cards
-> Writer
-> Editor
-> Logic Humanization Auditor
-> Foreshadow Auditor
-> DeAI Rewrite
-> QA Gate
-> Memory Update
-> Foreshadow Ledger Update
```

这里最关键的不是后面的 `DeAI Rewrite`，而是前面的：

- `Foreshadow Planner`
- `Logic Causality Planner`

它们决定本章是否有长期故事约束，而不是临场编剧情。

## 伏笔节奏规则

第一版可以先固定规则：

- 每章：至少 1 个微伏笔或人物习惯回声。
- 每 3 章：至少 1 个中伏笔。
- 每 5-7 章：回收 1 个中伏笔。
- 每 8-10 章：埋 1 个主线级伏笔。
- 第 20 章：回收阶段主线，同时留下更大的旧账。

这些规则用于 Build Chapter Context 和 QA Gate。

## Logic Causality Planner 必填结构

每章生成前必须先回答：

```json
{
  "why_this_event_happens_now": "为什么这件事现在发生",
  "who_benefits": ["谁获利"],
  "who_pays_cost": ["谁付代价"],
  "what_information_is_missing": ["还有什么信息缺口"],
  "what_mistake_protagonist_makes": "主角本章犯了什么判断错误"
}
```

这个节点要解决的问题是：事件不是因为作者想推进而发生，而是因为某些人、某些旧债、某些信息差在此刻压到了临界点。

## Build Chapter Context 需要新增的输入

原先只放大纲、前文摘要、人物状态是不够的。后续每章上下文应加入：

- 最近 3 章伏笔。
- 最近 6 章未回收伏笔。
- 最近 3 章主角判断是否都正确。
- 最近 3 章章末钩子类型。
- 本章必须新增、强化、回收的伏笔。
- 人物当前认知变化。
- 最近一次主角付出代价的位置。
- 最近一次配角反驳主角的位置。

## QA Gate 新增硬规则

建议新增硬指标：

```text
logic_ai_risk <= 45
foreshadow_score >= 75
最近 3 章至少有 1 个中伏笔
最近 6 章至少回收 1 个伏笔
主角不能连续 3 章全程判断正确
章末钩子类型不能连续 3 章相同
```

如果不满足，不应直接发布或合订为 final，而应进入 `DeAI Rewrite` 或人工审核。

## 两个审计节点的职责

### Logic Humanization Auditor

检查：

- 线索是否来得太及时。
- 角色是否过度理性。
- 对话是否总在解释剧情。
- 主角是否连续正确。
- 是否缺少私人细节、误会、犹豫、代价。
- 本章事件是否有前文原因。
- 反派或对手是否也有合理收益。

### Foreshadow Auditor

检查：

- 本章是否按计划埋伏笔。
- 伏笔是否过于直白。
- 应回收的伏笔是否回收。
- 回收是否有前文证据。
- 是否制造了新的无主线索。
- 最近几章伏笔密度是否失衡。

## 第一阶段落地边界

第一阶段不要一次性重构全部工作流，先新增 4 个节点：

1. `Foreshadow Planner`
2. `Logic Causality Planner`
3. `Logic Humanization Auditor`
4. `Foreshadow Ledger Update`

先让系统稳定生成和更新：

```text
memory/foreshadow_ledger.json
memory/character_arc_ledger.json
memory/causality_ledger.json
review/chXXX.logic.json
review/chXXX.foreshadow.json
```

## 第二阶段：20 章伏笔重排

在重写正文前，先生成全书级：

```text
outline/foreshadow_plan_20.json
```

示例结构：

```json
{
  "chapter": 5,
  "seed": ["调度参数异常"],
  "reinforce": ["何小满知道旧版模型"],
  "payoff": [],
  "new_question": "是谁有权限改参数"
}
```

这一步比单章润色更重要。没有全局伏笔规划，后面每章仍然容易变成 AI 临场编。

## 实施优先级

建议按以下顺序推进：

1. 新增账本 JSON Schema。
2. 新增 Prompt：Foreshadow Planner、Logic Causality Planner、Logic Humanization Auditor、Foreshadow Auditor、Ledger Update。
3. 修改 Build Chapter Context，读取三类账本。
4. 在单章 Worker 中插入 Planner 和 Auditor。
5. 修改 QA Gate，加入硬规则。
6. 跑 1 章验证账本能读写。
7. 跑 3 章验证节奏约束。
8. 跑 20 章生成 `foreshadow_plan_20.json` 和新一轮正文。

## 继续优化的路线图

如果要继续往下做，建议按“数据层 -> 生成层 -> 审计层 -> 学习层”四步走，不要一下子把所有能力都塞进一条线。

### 第 1 步：把账本先做实

先补齐三类 Schema 和初始化模板，让每本书一开始就有可写入的长期记忆：

- `foreshadow_ledger.schema.json`
- `character_arc_ledger.schema.json`
- `causality_ledger.schema.json`
- 初始化脚本：创建空账本和基础字段

这一阶段的目标不是写得更好，而是确保“写完以后知道写了什么、伏笔有没有被记住”。

### 第 2 步：让账本进入章节上下文

`Build Chapter Context` 要明确读取：

- 最近 3 章摘要。
- 最近 3 章伏笔。
- 最近 6 章未回收伏笔。
- 当前章节涉及的人物卡。
- 主角/关键配角的人物弧光账本。
- 当前可用金手指能力、限制和代价。
- 人物最近一次错误判断。
- 人物最近一次付出代价。
- 本章必须回收/强化/新增的伏笔。

这一步做完，Writer 才不容易每一章都像“重新开机”。

### 第 3 步：让生成前先有因果和伏笔计划

在写正文前先跑两个规划器：

- `Foreshadow Planner`：决定本章埋什么、强化什么、回收什么。
- `Logic Causality Planner`：决定为什么这件事现在发生、谁获利、谁付代价、主角犯什么错。

这两个节点的输出应该是结构化 JSON，而不是散文。

### 第 4 步：让审计节点决定是否重写

审计不要只看文风，要看故事机制：

- 是否太顺。
- 是否全员都在说正确的话。
- 是否没有信息差。
- 是否伏笔太直白。
- 是否主角连续正确。
- 是否章末钩子太重复。

如果审计失败，不是直接丢弃，而是进入 `DeAI Rewrite`，只修机制问题，不要把整章推倒重来。

### 第 5 步：先做 20 章伏笔表，再做正文

比单章优化更重要的是全书级编排。建议先生成：

- `outline/foreshadow_plan_20.json`

它负责规定每章的：

- 埋伏笔。
- 强化伏笔。
- 回收伏笔。
- 新问题。
- 旧账延迟。

没有这张表，后面的章节循环很容易重新变成“临场编故事”。

### 第 6 步：形成一个稳定的闭环

最终闭环应该长这样：

```text
标题
-> 故事种子
-> 小说圣经
-> 20章大纲
-> 伏笔总表
-> 章节循环
   -> 因果规划
   -> 伏笔规划
   -> 章节任务
   -> 场景卡
   -> 正文
   -> 人性化审计
   -> 伏笔审计
   -> QA
   -> 账本回写
   -> 下一章
```

### 第 7 步：最后再接更强模型和检索

等这套机制稳定后，再去做：

- Kimi 正文写作接入。
- RAG/向量检索。
- 更细的角色状态机。
- 自动精修版 `revised.md`。

这样改，最稳，也最不容易把流程越改越乱。
