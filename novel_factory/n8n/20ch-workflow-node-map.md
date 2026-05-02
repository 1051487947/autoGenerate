# 小说 N8N 节点映射

## 主流程

### 20章试写模式

```text
Webhook / Manual Trigger
  -> Init Book Params
  -> Init Local Project
  -> Load Prompt Templates
  -> GPT Seed From Title
  -> Validate Story Seed
  -> Save Story Seed
  -> GPT Story Bible
  -> Save Story Bible
  -> GPT Character Cards
  -> Save Characters
  -> GPT Golden Finger
  -> Save Golden Finger
  -> GPT Style Bible
  -> Save Style Bible
  -> GPT Voice Fingerprint
  -> Save Voice Fingerprint
  -> GPT Institutional Plausibility Patch
  -> Save Institutional Plausibility
  -> GPT Outline 20
  -> Validate Outline
  -> Save Outline
  -> Optional Editorial Diagnosis From Feedback
  -> Save Editorial Diagnosis
  -> Split Chapters
      -> Build Chapter Context
      -> GPT Logic Causality Planner
      -> Save Logic Plan
      -> GPT Foreshadow Planner
      -> Save Foreshadow Plan
      -> GPT Antagonist Countermove Planner
      -> Save Antagonist Countermove
      -> GPT Protagonist Cost Failure Planner
      -> Save Cost Plan
      -> GPT Motif Reader Promise Planner
      -> Save Motif Plan
      -> GPT Chapter Task
      -> GPT Scene Cards
      -> Split Scenes
          -> Kimi Scene Writer
      -> Collect Scenes
      -> Kimi/GPT Chapter Editor
      -> GPT Anti-AI Audit
      -> Save Anti-AI Audit
      -> GPT Style Consistency Auditor
      -> Save Style Audit
      -> GPT Critic Auditor
      -> QA Gate
          -> Pass: Archive Chapter
          -> Retry: Rewrite Chapter
          -> Manual: Wait For Approval
      -> GPT Memory Update
      -> Save Memory
  -> Finalize 20 Chapters
  -> Archive Full Book
```

### 30万字长篇模式

```text
Webhook / Manual Trigger
  -> Init Book Params
  -> Init Local Project
  -> Load Prompt Templates
  -> GPT Seed From Title
  -> Validate Story Seed
  -> Save Story Seed
  -> GPT Story Bible
  -> Save Story Bible
  -> GPT Character Cards
  -> Save Characters
  -> GPT Golden Finger
  -> Save Golden Finger
  -> GPT Style Bible
  -> Save Style Bible
  -> GPT Voice Fingerprint
  -> Save Voice Fingerprint
  -> GPT Institutional Plausibility Patch
  -> Save Institutional Plausibility
  -> GPT Long Novel Architect
  -> Save Long Novel Architecture
  -> Split Volumes
      -> GPT Volume Arc Planner
      -> Save Volume Arc
  -> Select Current Batch 20 Chapters
  -> GPT Rolling Batch 20 Planner
  -> Save Current Batch Outline
  -> Split Chapters
      -> Run Chapter Worker
  -> GPT Arc Continuity Auditor
  -> Save Arc Continuity Audit
  -> If Can Continue
      -> Next Batch
  -> If Needs Repair
      -> Repair Outline / Manual Review
  -> Asset Completeness Audit
  -> Finalize Full Book
  -> Archive Full Book
```

## 关键数据字段

### Init Book Params

```json
{
  "book_id": "kuaidi_dongshizhang",
  "title": "我要送快递可是你非要我做董事长",
  "chapter_count": 20,
  "target_words_per_chapter": 2500,
  "style": "都市轻喜剧爽文",
  "models": {
    "logic": "gpt",
    "writer": "kimi"
  }
}
```

30万字长篇建议：

```json
{
  "book_id": "kuaidi_300k",
  "title": "我要送快递可是你非要我做董事长",
  "chapter_count": 120,
  "target_total_words": 300000,
  "target_words_per_chapter": 2500,
  "batch_size": 20,
  "style": "都市轻喜剧爽文",
  "models": {
    "logic": "gpt",
    "writer": "kimi"
  }
}
```

### Chapter Loop 输入

```json
{
  "book_id": "...",
  "chapter_plan": {
    "chapter_index": 1,
    "chapter_title": "...",
    "chapter_goal": "...",
    "main_conflict": "...",
    "cliffhanger": "..."
  },
  "memory": {
    "recent_summaries": [],
    "active_characters": [],
    "active_foreshadowing": [],
    "must_remember": [],
    "character_arc_ledger": {},
    "causality_ledger": {},
    "hook_ledger": {}
  },
  "bible_assets": {
    "characters": {},
    "golden_finger": {},
    "institutional_plausibility": {},
    "long_novel_architecture": {},
    "style_bible": "",
    "voice_fingerprint": {},
    "anti_ai_phrasebook": {},
    "reader_promise": {}
  }
}
```

### V0.2 新增文件

书籍级：

```text
bible/characters.json
bible/golden_finger.json
bible/institutional_plausibility.json
bible/long_novel_architecture.json
bible/style_bible.md
bible/voice_fingerprint.json
bible/anti_ai_phrasebook.zh.json
```

长篇大纲：

```text
outline/volumes.json
outline/current_batch_outline.json
```

章节级：

```text
review/ch001.logic.json
review/ch001.foreshadow.json
review/ch001.antagonist.json
review/ch001.cost.json
review/ch001.motif.json
review/ch001.anti_ai.json
```

长期账本：

```text
memory/foreshadow_ledger.json
memory/character_arc_ledger.json
memory/causality_ledger.json
memory/golden_finger_ledger.json
memory/global_arc_ledger.json
memory/plot_thread_ledger.json
memory/relationship_ledger.json
memory/protagonist_cost_ledger.json
memory/motif_ledger.json
memory/editorial_feedback_ledger.json
memory/hook_ledger.json
```

批次级审计：

```text
review/arc_continuity_report.json
review/asset_completeness_report.json
```

### QA Gate

推荐规则：

- `total_score >= 80`：通过。
- `70 <= total_score < 80`：自动修订一次。
- `total_score < 70`：整章重写。
- `major_conflict = true`：暂停人工确认。
- `logic_ai_risk > 45`：定向重写。
- 最近 3 章主角都无明显误判或代价：强制进入 `Protagonist Cost Failure Planner` 重排。
- 本章对手无主动反制动作：回退到 `Antagonist Countermove Planner`。
- 制度强设定被角色直接质疑但无补丁：暂停人工确认。

## 文件保存建议

每章至少保存：

```text
chapter_tasks/ch001.task.json
scenes/ch001.scenes.json
scenes/ch001_scene01.md
chapters/ch001.md
review/ch001.logic.json
review/ch001.foreshadow.json
review/ch001.antagonist.json
review/ch001.cost.json
review/ch001.motif.json
review/ch001.anti_ai.json
review/ch001.style.json
review/ch001.qa.json
memory/ch001.memory.json
```

## 避免的问题

- 不要用 `$getWorkflowStaticData('global')` 保存所有运行状态，容易串数据。
- 每次运行必须带 `book_id` 和 `run_id`。
- HTTP Request 归档节点不要吞掉原始章节正文。
- 归档前先 `Collect Chapter`，再调用外部归档接口。
- GPT 输出必须先校验 JSON，再进入下游节点。
