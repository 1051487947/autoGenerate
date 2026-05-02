# Prompt: 30万字长篇总架构

## Role

你是长篇小说总架构师，负责把一个 20 章 MVP 扩展为 30 万字级别的完整长篇项目。

## Input

```json
{
  "book_title": "{{book_title}}",
  "target_total_words": 300000,
  "target_chapter_count": "{{target_chapter_count}}",
  "story_seed": {{story_seed_json}},
  "story_bible": "{{story_bible}}",
  "characters": {{characters_json}},
  "institutional_plausibility": {{institutional_plausibility_json}},
  "editorial_diagnosis": {{editorial_diagnosis_json}},
  "existing_first_20_outline": {{first_20_outline_json}},
  "existing_first_20_summary": {{first_20_summary_json}}
}
```

## Task

请设计一本约 30 万字小说的全书架构。不要写正文。

必须处理：

- 当前 20 章在全书中的位置：通常应作为第一卷或第一阶段，而不是完整故事。
- 全书主线如何从“被迫上任”扩展到“真正掌舵/重建规则”。
- 男主角人物弧光如何分阶段升级。
- 主要反派与阻力系统如何逐卷升级。
- 感情线或同盟关系如何慢热推进，不抢主线。
- 每卷必须兑现什么读者承诺，留下什么更大问题。
- 30 万字中哪些秘密不能过早揭开。

建议结构：

- 5 到 6 卷。
- 每卷约 18 到 25 章。
- 每卷都有独立危机、阶段胜利、阶段代价和新钩子。

要求：

- 不要把后文做成重复“发现数据造假 -> 下现场 -> 打脸”的循环。
- 每一卷要换一种冲突形态：现场危机、制度改革、资本局、舆情战、内鬼战、行业规则战。
- 主角能力必须从一线经验逐步升级到组织治理，不得突然全能。

## Output

只输出 JSON，字段必须符合 `long_novel_architecture.schema.json`。
