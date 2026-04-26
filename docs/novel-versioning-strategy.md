# AI 小说生成版本维护策略

## 结论

KodBox 不建议作为生成过程的主版本库。它更适合作为“成品归档、阅读预览、外部分发”的位置。

AI 小说生成过程中会产生大量中间产物：Prompt、故事种子、小说圣经、大纲、场景卡、正文草稿、审稿报告、记忆回写、重写版本。直接全部堆到 KodBox 后期很难追踪差异、回滚和复盘。

第一轮推荐：

```text
本地/服务器项目目录 = 主工作区
Git = 版本控制和差异对比
SQLite/JSON = 运行状态和结构化记忆
KodBox = 通过质量闸门后的成品导出
```

## 推荐分层

### 1. 主工作区

主工作区保存所有可复现生成过程的文件。

```text
novel_projects/<book_id>/
├── inputs/
├── bible/
├── outline/
├── chapter_tasks/
├── scenes/
├── chapters/
├── memory/
├── review/
├── runs/
└── export/
```

这里是 N8N 和 Bridge 的主要读写位置。

### 2. Git 版本控制

Git 适合保存：

- Prompt 模板
- Schema
- 故事圣经
- 20 章大纲
- 章节任务单
- 场景卡
- 定稿章节
- 审稿报告
- 记忆快照

推荐提交粒度：

```text
init: create book project <book_id>
seed: generate story seed
bible: generate story bible
outline: generate 20 chapter plan
chapter 001: draft, review, memory update
chapter 002: draft, review, memory update
finalize: export 20 chapter manuscript
```

### 3. runs 运行记录

每次调用模型都应该保存运行记录，用于复盘和追踪。

```text
runs/
└── 20260426_140501_ch001_draft/
    ├── request.json
    ├── response.json
    ├── prompt.md
    ├── model.json
    └── output.md
```

`runs/` 可以很大。第一轮可以全部保存；以后如果太大，再只保存关键节点。

### 4. SQLite 或 JSON 状态库

第一轮 20 章可以继续用 JSON。

当后续要做多本书、多轮重写、多模型对比时，建议加 SQLite。

建议表：

- `books`
- `chapters`
- `generation_runs`
- `chapter_versions`
- `qa_reports`
- `memory_events`
- `foreshadowing_events`

### 5. KodBox 归档

KodBox 只建议放：

- 通过 QA 的章节 Markdown
- 20 章合订版
- 可阅读版本
- 对外备份包

不建议把每次失败草稿、模型原始响应、重写过程都直接发布到 KodBox。

## 版本命名建议

章节文件：

```text
chapters/ch001.md
chapters/ch001.v001.draft.md
chapters/ch001.v002.revised.md
chapters/ch001.final.md
```

审稿文件：

```text
review/ch001.v001.qa.json
review/ch001.v002.qa.json
```

运行目录：

```text
runs/20260426_140501_ch001_scene_writer_gpt/
runs/20260426_141012_ch001_critic_gpt/
```

## N8N 推荐流程

1. LLM 生成内容。
2. Bridge 写入 `runs/<run_id>/` 原始请求和响应。
3. Bridge 写入业务产物，如 `chapters/ch001.v001.draft.md`。
4. GPT 审稿。
5. QA 通过后，复制或写入 `chapters/ch001.final.md`。
6. 章节完成后触发 Git commit。
7. 20 章完成后导出到 `export/full_book.md`。
8. 最后再上传 KodBox。

## 第一轮最小方案

20 章 MVP 先这样做：

- 主工作区：`novel_projects/<book_id>/`
- 每章保留：任务单、场景卡、正文、QA、记忆
- 每章至少一个 Git commit
- KodBox 只上传 `export/full_book.md` 和 `chapters/*.final.md`

这样既不会过度工程化，也能保留可回滚、可对比、可复盘的版本链。

## 是否使用 GitHub

可以使用 GitHub，而且推荐使用私有仓库作为远程版本库。

推荐定位：

```text
本地 Git 仓库 = 日常写作和自动化生成的主工作区
GitHub 私有仓库 = 远程备份、版本对比、跨设备同步、后续协作
KodBox = 成品阅读和归档
```

不建议把 GitHub 当作运行时数据库，也不建议让 N8N 每生成一个小片段就 push 一次。更稳的方式是：

1. N8N 在本地/服务器项目目录生成文件。
2. 每完成一个关键阶段再提交：
   - 故事种子完成。
   - 小说圣经完成。
   - 20 章大纲完成。
   - 每章定稿完成。
   - 20 章合订导出完成。
3. 由 N8N 或人工触发 `git commit` 和 `git push`。

建议 GitHub 仓库设为 Private，因为小说设定、大纲、正文、Prompt 都属于核心资产。

建议不要提交：

- API Key、Token、Cookie、N8N 凭据。
- `.env` 文件。
- 过大的模型原始响应日志。
- 临时缓存和 `__pycache__`。
- 还不想外泄的敏感商业设定。

可提交：

- `novel_factory/`
- `docs/`
- `novel_projects/<book_id>/bible/`
- `novel_projects/<book_id>/outline/`
- `novel_projects/<book_id>/chapter_tasks/`
- `novel_projects/<book_id>/scenes/*.json`
- `novel_projects/<book_id>/chapters/*.final.md`
- `novel_projects/<book_id>/review/*.qa.json`
- `novel_projects/<book_id>/memory/*.json`
- `novel_projects/<book_id>/export/full_book.md`

如果后续生成内容非常大，可以把 `runs/` 原始运行日志放在本地或对象存储，只把关键产物提交到 GitHub。
