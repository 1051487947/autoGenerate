# 现有 N8N Workflow 升级说明

现有文件：`Novel MVP - Agent Skill Guarded.json`

结论：需要更新，但不需要推倒重做。旧 workflow 的 Outline / Draft / Edit / QA 骨架可以复用，主要需要改四类问题。

## 需要改的地方

### 1. 模型接口

现有 LLM 节点使用：

```text
{{$env.NOVEL_LLM_BASE_URL + '/v1/messages'}}
model: glm-5-turbo
x-api-key
anthropic-version
```

如果第一轮先全部用 GPT，需要改成 OpenAI Chat Completions 或你的 OpenAI 兼容网关：

```text
POST {{$env.OPENAI_BASE_URL || 'https://api.openai.com'}}/v1/chat/completions
Authorization: Bearer {{$env.OPENAI_API_KEY}}
model: {{$env.OPENAI_MODEL || 'gpt-4o'}}
```

同时所有解析节点要兼容：

```javascript
$json.choices?.[0]?.message?.content
```

不能只读：

```javascript
$json.content?.[0]?.text
```

### 2. 落盘方式

现有流程主要依赖 `$getWorkflowStaticData('global')` 和 KodBox 归档。

升级后应该写入 Bridge：

```text
POST /api/books/<book_id>/write
```

保存到：

```text
novel_projects/<book_id>/bible/
novel_projects/<book_id>/outline/
novel_projects/<book_id>/chapter_tasks/
novel_projects/<book_id>/scenes/
novel_projects/<book_id>/chapters/
novel_projects/<book_id>/review/
novel_projects/<book_id>/memory/
```

### 3. KodBox 位置

KodBox 不应该作为过程存储。

建议：

- 章节未通过 QA 前，不上传 KodBox。
- 只在 `chapters/*.final.md` 或 `export/full_book.md` 生成后上传。
- 第一轮甚至可以先关闭 KodBox，只保留本地/GitHub。

### 4. 章节结构

现有 workflow 是：

```text
Outline -> Draft Chapter -> Edit -> QA
```

后续应升级为：

```text
Story Seed -> Story Bible -> 20章大纲 -> 章节任务单 -> 场景卡 -> 场景正文 -> 合章 -> QA -> Memory Update
```

## 推荐升级顺序

1. 先导入 `Novel Seed - Bridge GPT MVP.json`。
2. 跑通：标题 -> story_seed.json。
3. 再加：story_seed -> story_bible.md。
4. 再加：story_bible -> chapters_20.json。
5. 最后迁移旧 workflow 的章节生成循环。

这样风险最低，因为每一步都有明确文件落盘，可以单独排查。

