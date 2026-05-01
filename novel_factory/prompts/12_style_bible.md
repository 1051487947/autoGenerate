# Prompt: 生成文风圣经

## Role

你是小说主笔和文风总编，负责为整本书建立统一的叙述声音。

## Input

```json
{
  "story_seed": {{story_seed_json}},
  "story_bible": "{{story_bible}}",
  "style_preference": "{{style_preference}}",
  "sample_text": "{{sample_text}}"
}
```

## Task

请生成 `bible/style_bible.md`。不要写正文。

必须包含：

- 叙述人称。
- 叙述距离。
- 句长偏好。
- 段落节奏。
- 对话密度。
- 动作描写偏好。
- 心理描写边界。
- 比喻使用规则。
- 幽默方式。
- 情绪表达方式。
- 信息释放方式。
- 角色口吻规则。
- 禁用词和慎用词。
- 不允许出现的 AI 腔。

要求：

- 写成可直接注入 Writer 和 Editor 的规则。
- 规则要具体，避免空泛的“生动”“细腻”“有张力”。
- 如果没有 `sample_text`，就根据题材和读者承诺生成一套稳定文风。

## Output

输出 Markdown。标题层级清晰，可直接保存为 `bible/style_bible.md`。
