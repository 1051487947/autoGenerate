# 小说工厂抽象程度评估

日期：2026-05-02

## 结论

当前小说工厂不用推翻重来，可以支撑第二本书。

但在 2026-05-02 检查前，部分运行时 Prompt 仍残留第一本书的题材表达，例如快递、董事长、签收、一线体感 vs PPT。这类内容如果留在通用 Prompt 中，会污染第二本书。

本次已将运行时 Prompt 中的第一本书硬编码改为通用表达。

## 当前抽象分层

### 通用工厂层

这些资产应服务所有小说：

```text
novel_factory/scripts
novel_factory/schemas
novel_factory/prompts
novel_factory/n8n
novel_factory/scripts/build_reader_site.py
```

它们只应该表达通用能力，例如：

- 从标题生成种子。
- 建立故事圣经。
- 生成人物卡。
- 规划长篇总架构。
- 拆分分卷、批次、章节、场景。
- 审计逻辑、文风、伏笔、人物弧光、关系线。
- 管理长期记忆和阅读站发布。

### 单书题材层

这些内容应该只存在于每本书自己的项目目录：

```text
novel_projects/<book_id>/bible
novel_projects/<book_id>/outline
novel_projects/<book_id>/memory
novel_projects/<book_id>/review
novel_projects/<book_id>/chapters
```

例如第一本书的：

- 快递员。
- 董事长。
- 签收隐喻。
- 一线体感 vs PPT。
- 万路达。
- 陆小川、沈妙、许岩。

这些不应该进入通用 Prompt。

## 本次清理

已清理以下 Prompt 的题材硬编码：

```text
06_writer_kimi_scene.md
18_editorial_diagnosis_from_feedback.md
19_institutional_plausibility_patch.md
21_protagonist_cost_failure_planner.md
22_motif_reader_promise_planner.md
23_long_novel_architect.md
```

清理后的原则：

- 不写“快递员为什么能当董事长”，而写“核心强设定为什么成立”。
- 不写“董事长不是大号站长”，而写“新身份不是原能力的简单放大”。
- 不写“签收隐喻”，而写“从 story_bible、reader_promise、editorial_diagnosis 中提取核心隐喻”。
- 不写“被迫上任到掌舵”，而写“从初始钩子到最终承诺兑现”。

## 第二本书是否要推翻

不需要推翻。

第二本书应复用：

- 初始化脚本。
- Prompt 模板。
- JSON Schema。
- N8N 编排。
- 长篇架构流程。
- 资产完整性审计思路。
- 阅读站发布方式。

第二本书需要新生成：

- `story_seed.json`
- `story_bible.md`
- `characters.json`
- `golden_finger.json`
- `reader_promise.json`
- `institutional_plausibility.json`
- `long_novel_architecture.json`
- `volumes.json`
- 所有单书记忆账本

## 仍需继续抽象的方向

下一步建议新增 `project_profile.json` 或 `genre_contract.json`，用于在新书初始化时明确：

- 题材类型。
- 读者期待。
- 主角类型。
- 世界规则。
- 叙事尺度。
- 感情线强度。
- 爽点类型。
- 禁写方向。
- 是否需要金手指。
- 是否需要现实制度补丁。

这样第二本书就不会只是“换标题”，而是真正换一套题材契约。
