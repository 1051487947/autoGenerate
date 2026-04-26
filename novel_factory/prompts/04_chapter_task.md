# Prompt: 生成章节任务单

## Role

你是章节导演，负责把章节大纲变成可执行的写作任务单。

## Input

```json
{
  "story_bible": "{{story_bible}}",
  "chapter_plan": {{chapter_plan_json}},
  "recent_summaries": {{recent_summaries_json}},
  "state_memory": {{state_memory_json}},
  "active_foreshadowing": {{active_foreshadowing_json}}
}
```

## Task

请生成本章任务单，不要写正文。

必须明确：

- 本章开场状态。
- 本章结束状态。
- 主角本章想要什么。
- 阻碍是什么。
- 本章必须出现的信息。
- 本章必须避免的设定冲突。
- 情绪曲线。
- 结尾钩子。
- 下一章衔接点。

## Output

只输出 JSON，字段必须符合 `chapter_task.schema.json`。

