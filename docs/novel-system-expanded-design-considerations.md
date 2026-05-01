# AI 中长篇小说系统扩展设计清单

日期：2026-05-01

## 背景

当前系统已经考虑了：

- N8N 章节循环。
- 故事种子、小说圣经、20 章大纲。
- 人物卡雏形。
- 金手指雏形。
- 伏笔账本。
- 人物弧光账本。
- 因果账本。
- QA 与 Memory Update。

本文件补充从中长篇小说创作、开源 AI 写作项目、去 AI 化、文风一致性几个角度还应继续考虑的内容。

## 参考到的开源项目思路

本次调研重点参考了以下公开项目和做法：

- NousResearch/autonovel：小说生成管线中包含 world、characters、outline、canon、mystery、voice、anti-slop、anti-patterns 等文件，并采用生成、评估、修订循环。
- RhythmicWave/NovelForge：强调 Schema 驱动卡片、上下文注入、知识图谱一致性、角色/关系/场景/组织/物品/概念状态提取。
- iLearn-Lab/NovelClaw：强调 dynamic-memory-first、可检查运行日志、memory banks、world/character/style surfaces。
- forsonny/book-os：强调 Standards、Novel、Manuscripts 三层上下文，让 AI 写出像作者本人的风格。
- LewdLeah/Auto-Cards：自动检测命名实体并写入故事卡，解决长故事中的 object permanence。
- bal-spec/sillytavern-character-memory：角色卡定义“角色是谁”，Data Bank 记录“发生过什么”，并在生成时检索相关记忆。
- pixelnull/sillytavern-DeepLore-Enhanced：从 Obsidian lore vault 中检索设定，支持两阶段检索、关系图、缺口分析、上下文门控。
- principia-ai/WriteHERE：递归规划、检索/推理/写作混合、根据上下文动态调整写作过程。
- sam-paech/slop-forensics 与 EQ-Bench creative-writing-bench：用过度词、短语、三元短语、重复度、pairwise ranking 等方式评估 AI 味和创意写作质量。

## 作为中长篇小说系统还缺的内容

### 1. 读者承诺账本

需要新增：

```text
bible/reader_promise.json
memory/promise_delivery_ledger.json
```

它记录这本书答应读者什么：

- 爽点类型。
- 情绪类型。
- 主角魅力。
- 金手指期待。
- 反派压迫感。
- 情感线节奏。
- 喜剧/反差机制。

每章生成后检查：本章有没有兑现至少一个读者承诺。

### 2. 冲突压力账本

长篇不能只靠主角解决问题，还要有压力递增。

建议新增：

```text
memory/pressure_ledger.json
```

记录：

- 外部压力。
- 内部压力。
- 时间限制。
- 资源限制。
- 舆论压力。
- 关系压力。
- 主角个人代价。

QA 要检查：本章是否让问题更复杂，而不是只解决问题。

### 3. 信息差账本

故事好看往往来自“谁知道什么、谁误解什么、谁故意隐瞒什么”。

建议新增：

```text
memory/knowledge_state_ledger.json
```

字段：

- 读者知道什么。
- 主角知道什么。
- 反派知道什么。
- 配角误以为什么。
- 哪些信息暂时不能公开。
- 哪些信息应该被误读。

它能避免 AI 把所有人都写得太聪明、太透明。

### 4. 反派/阻力系统账本

反派不能只在需要冲突时突然出现。

建议新增：

```text
memory/antagonist_move_ledger.json
```

每章记录：

- 对手这章有没有行动。
- 对手获利还是受损。
- 对手是否根据前文做出合理反应。
- 对手下一步可能采取什么动作。

这样故事会更像双方博弈，而不是作者推着主角走。

### 5. 场景功能账本

每个场景都要有功能，不能只是“过剧情”。

建议每张 Scene Card 增加：

- scene_function：推进情节、暴露人物、制造误会、回收伏笔、制造代价。
- scene_turn：场景前后局势发生了什么反转。
- emotional_shift：人物情绪如何变化。
- information_delta：读者/主角/对手分别新增了什么信息。

### 6. 章节钩子类型账本

已有想法是避免章末钩子连续 3 章相同。可以进一步结构化：

```text
memory/hook_ledger.json
```

钩子类型：

- 危机型。
- 反转型。
- 信息揭露型。
- 人物选择型。
- 关系破裂型。
- 新问题型。
- 喜剧反差型。

## 去 AI 化还要做的设计

### 1. 反顺滑机制

每章生成前加入：

```text
Friction Planner
```

它强制制造一个不顺滑点：

- 主角判断错一次。
- 配角不配合。
- 线索出现但被误读。
- 金手指失效或有代价。
- 一个私人小事打断主线。

### 2. 反正确话机制

AI 常让人物说“正确、完整、解释剧情”的话。

建议 Dialogue Auditor 检查：

- 是否人人都像辩论赛。
- 是否每句都能直接推进剧情。
- 是否缺少打断、含糊、绕弯、口误、沉默。
- 是否角色说出了他不该知道的信息。

### 3. 反总结机制

AI 常在情绪后补一句解释。

规则：

- 情绪已经通过动作、沉默、对话表现，就不要再解释。
- 删除“他终于明白”“他意识到”“这意味着”这类过度总结。
- 审计节点可以标记 show_then_tell 问题。

### 4. 句式与结构反模式检测

需要检测：

- 连续三段结构相同。
- 连续章末钩子同构。
- 连续场景都是“冲突 -> 解释 -> 解决”。
- 对话中多角色使用同一种反问或排比。
- 太多“三件事”“三个形容词”“一二三式分析”。

### 5. 不完整人物机制

每章至少允许一个角色：

- 说错话。
- 没解释清楚。
- 误会别人。
- 自私一下。
- 做了正确但不讨喜的选择。

这比单纯“润色”更能降低 AI 味。

## 文笔笔锋一致性设计

### 1. 风格圣经

建议新增：

```text
bible/style_bible.md
```

内容包括：

- 叙述人称。
- 叙述距离。
- 句长范围。
- 对话密度。
- 动作描写偏好。
- 比喻使用规则。
- 幽默方式。
- 情绪表达方式。
- 禁用词和慎用词。
- 常用词库和角色专属口头禅。

### 2. 作者声音指纹

建议新增：

```text
bible/voice_fingerprint.json
```

可记录：

- 平均句长。
- 句长方差。
- 短句比例。
- 对话比例。
- 段落长度分布。
- 高频动词。
- 高频语气词。
- 常用标点。
- 比喻密度。
- 心理描写/动作描写比例。

后续每章 QA 比对一次。

### 3. Style Anchor 注入

每章写作前注入 2-3 段“风格锚点”，但不是让模型复写，而是提醒：

- 叙述节奏。
- 对话颗粒度。
- 幽默方式。
- 信息释放方式。

### 4. 风格漂移检测

建议新增：

```text
review/chXXX.style.json
```

检查：

- 是否比前几章更书面。
- 是否突然变成鸡汤文。
- 是否突然变成影视解说腔。
- 是否突然过度华丽。
- 是否角色说话方式趋同。

## AI 观念和措辞规避

### 1. 禁用观念

不仅要禁词，还要禁一些 AI 习惯性观念：

- 每个冲突都要被正向解释。
- 每个角色都要“成长”。
- 每个选择都要显得理性。
- 每章结尾都要总结主题。
- 所有人都在追求更好的自己。
- 反派必须立刻被道德批判。
- 主角观点总是正确。

### 2. 中文 AI 味措辞黑名单

建议建立：

```text
bible/anti_ai_phrasebook.zh.json
```

先按“聚集出现才扣分”的方式处理，不要绝对禁用。

可监控类型：

- 总结词：显然、毫无疑问、不可否认、归根结底、某种意义上。
- 情绪套话：空气仿佛凝固、眼神复杂、沉默良久、心头一震、嘴角勾起。
- 解释套话：他终于明白、他意识到、这意味着、这不仅是。
- 鸡汤句：真正的、从来不是、而是、命运的齿轮、属于他的战斗。
- 结构套话：不是因为 X，而是因为 Y；与其说 X，不如说 Y。

### 3. 术语替换不是最终答案

去 AI 味不是把词换掉，而是减少：

- 空泛抽象。
- 完美逻辑。
- 过度解释。
- 句式对称。
- 情绪总结。
- 人物正确化。

技术上要用“审计 + 定向重写”，而不是单纯同义词替换。

## 建议加入 N8N 的新节点

第一阶段建议新增：

```text
Build Enhanced Chapter Context
Foreshadow Planner
Logic Causality Planner
Friction Planner
Reader Promise Checker
Style Consistency Auditor
Dialogue Humanization Auditor
Anti-AI Phrase Auditor
Ledger Update
```

第二阶段再新增：

```text
Knowledge State Update
Antagonist Move Planner
Voice Fingerprint Extractor
Chapter Ending Variety Auditor
Pairwise Revision Judge
```

## 推荐的最终目录扩展

```text
bible/
  characters.json
  golden_finger.json
  reader_promise.json
  style_bible.md
  voice_fingerprint.json
  anti_ai_phrasebook.zh.json

memory/
  foreshadow_ledger.json
  character_arc_ledger.json
  causality_ledger.json
  pressure_ledger.json
  knowledge_state_ledger.json
  antagonist_move_ledger.json
  hook_ledger.json
  golden_finger_ledger.json

review/
  chXXX.logic.json
  chXXX.foreshadow.json
  chXXX.style.json
  chXXX.dialogue.json
  chXXX.anti_ai.json
```

## 下一步落地顺序

建议下一轮开发按这个顺序：

1. 新增 `style_bible.md`、`voice_fingerprint.json`、`anti_ai_phrasebook.zh.json`。
2. 新增 `reader_promise.json`、`pressure_ledger.json`、`knowledge_state_ledger.json`。
3. 修改 `Build Chapter Context`，注入人物卡、金手指、风格圣经、读者承诺、压力账本。
4. 新增 `Friction Planner` 和 `Style Consistency Auditor`。
5. 新增 `Anti-AI Phrase Auditor`，先只输出报告，不强制重写。
6. 跑 3 章观察报告是否有用，再决定是否进入强制 Gate。

