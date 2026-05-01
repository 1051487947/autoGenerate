# 小说工厂 V0.2 落地记录

日期：2026-05-01

## 目标

V0.2 的目标不是重写 N8N 主流程，而是先补齐后续去 AI 化和长期连续性所需的稳定资产层：

- 人物卡。
- 金手指规则。
- 文风圣经。
- 作者声音指纹。
- 反 AI 措辞审计。
- 章节因果规划。
- 章节伏笔规划。
- 长期故事账本占位。

## 新增 Prompt

新增文件：

```text
novel_factory/prompts/10_character_cards.md
novel_factory/prompts/11_golden_finger.md
novel_factory/prompts/12_style_bible.md
novel_factory/prompts/13_voice_fingerprint.md
novel_factory/prompts/14_logic_causality_planner.md
novel_factory/prompts/15_foreshadow_planner.md
novel_factory/prompts/16_anti_ai_audit.md
novel_factory/prompts/17_style_consistency_auditor.md
```

这些 Prompt 可以通过 Novel Bridge 被 N8N 读取，例如：

```text
GET /api/prompts/10_character_cards.md
GET /api/prompts/14_logic_causality_planner.md
GET /api/prompts/16_anti_ai_audit.md
```

## 新增 Schema

新增文件：

```text
novel_factory/schemas/characters.schema.json
novel_factory/schemas/golden_finger.schema.json
novel_factory/schemas/foreshadow_plan.schema.json
novel_factory/schemas/causality_plan.schema.json
novel_factory/schemas/voice_fingerprint.schema.json
novel_factory/schemas/anti_ai_audit.schema.json
novel_factory/schemas/style_audit.schema.json
```

这些 Schema 用于约束模型输出，避免 N8N 后续节点解析不稳定。

## 初始化脚本升级

已更新：

```text
novel_factory/scripts/init_book_project.py
```

新书初始化时会额外生成：

```text
bible/golden_finger.json
bible/reader_promise.json
bible/style_bible.md
bible/voice_fingerprint.json
bible/anti_ai_phrasebook.zh.json
memory/foreshadow_ledger.json
memory/character_arc_ledger.json
memory/causality_ledger.json
memory/golden_finger_ledger.json
memory/pressure_ledger.json
memory/knowledge_state_ledger.json
memory/antagonist_move_ledger.json
memory/hook_ledger.json
review/anti_ai_report.json
review/style_report.json
review/logic_report.json
review/foreshadow_report.json
```

## 验证

已执行：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\init_book_project.py --title "V0.2 落地测试" --book-id v02_landing_test
```

生成目录：

```text
novel_projects/v02_landing_test
```

该目录仅用于 smoke test，验证后已清理；后续可用同一命令重新生成。

验证结果：

- 所有新增 Schema 均可被 JSON 解析。
- 初始化出的项目内所有 JSON 文件均可被解析。
- `README.md` 中已包含 V0.2 生成顺序和长期账本说明。

## 下一步

下一阶段再改 N8N 工作流，建议分两步：

1. 主流程增加书籍级节点：
   - `Character Cards`
   - `Golden Finger`
   - `Style Bible`
   - `Voice Fingerprint`

2. 单章 Worker 增加章节级节点：
   - `Logic Causality Planner`
   - `Foreshadow Planner`
   - `Anti-AI Audit`
   - `Style Consistency Auditor`

先跑 1 章和 3 章验证，再决定是否把 `Anti-AI Audit` 接入强制 QA Gate。
