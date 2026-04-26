# 20 章小说 N8N 节点映射

## 主流程

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
  -> GPT Outline 20
  -> Validate Outline
  -> Save Outline
  -> Split Chapters
      -> Build Chapter Context
      -> GPT Chapter Task
      -> GPT Scene Cards
      -> Split Scenes
          -> Kimi Scene Writer
      -> Collect Scenes
      -> Kimi/GPT Chapter Editor
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
    "must_remember": []
  }
}
```

### QA Gate

推荐规则：

- `total_score >= 80`：通过。
- `70 <= total_score < 80`：自动修订一次。
- `total_score < 70`：整章重写。
- `major_conflict = true`：暂停人工确认。

## 文件保存建议

每章至少保存：

```text
chapter_tasks/ch001.task.json
scenes/ch001.scenes.json
scenes/ch001_scene01.md
chapters/ch001.md
review/ch001.qa.json
memory/ch001.memory.json
```

## 避免的问题

- 不要用 `$getWorkflowStaticData('global')` 保存所有运行状态，容易串数据。
- 每次运行必须带 `book_id` 和 `run_id`。
- HTTP Request 归档节点不要吞掉原始章节正文。
- 归档前先 `Collect Chapter`，再调用外部归档接口。
- GPT 输出必须先校验 JSON，再进入下游节点。

