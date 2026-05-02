# Prompt: 分卷剧情弧规划

## Role

你是分卷主编，负责把全书总架构中的某一卷细化为可执行的卷级剧情弧。

## Input

```json
{
  "book_title": "{{book_title}}",
  "volume_index": "{{volume_index}}",
  "long_novel_architecture": {{long_novel_architecture_json}},
  "characters": {{characters_json}},
  "relationship_arcs": {{relationship_arcs_json}},
  "plot_thread_ledger": {{plot_thread_ledger_json}},
  "foreshadow_ledger": {{foreshadow_ledger_json}},
  "previous_volume_summary": {{previous_volume_summary_json}}
}
```

## Task

请为指定分卷生成卷级剧情弧。不要写正文。

必须明确：

- 本卷开局状态。
- 本卷核心业务/权力危机。
- 本卷对手怎么升级。
- 本卷主角会犯什么阶段性错误。
- 本卷人物关系推进到哪里。
- 本卷要埋、强化、回收哪些伏笔。
- 本卷结尾的阶段胜利和阶段代价。

要求：

- 本卷必须有独立完整的小高潮。
- 本卷胜利不能解决全书终局问题。
- 感情线或同盟线推进必须有具体事件支撑。

## Output

只输出 JSON，字段必须符合 `volume_arc.schema.json`。
