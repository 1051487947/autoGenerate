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

## 服务器同步

2026-05-01 已同步到服务器：

```text
/opt/autoGenerate
```

同步方式：

- 本地提交：`7678d40 add novel factory v0.2 assets`
- 已推送到 GitHub `main`
- 服务器从 `origin/main` 检出 `docs` 和 `novel_factory`

说明：

- 服务器 `/opt/autoGenerate/novel_projects` 下已有大量生成产物，直接 `git pull --ff-only` 会被未跟踪产物保护机制拦截。
- 本次只更新 `docs` 和 `novel_factory`，没有删除或覆盖服务器已有小说生成产物。
- 已重启 `novel-bridge` 容器，让 `/api/books/init` 重新加载新版 `init_book_project.py`。

服务器验证：

- Bridge 可读取 `10_character_cards.md`。
- Bridge 可读取 `characters.schema.json`。
- Bridge 可读取 `17_style_consistency_auditor.md`。
- 通过 `POST /api/books/init` 创建测试书后，已确认会生成：
  - `bible/golden_finger.json`
  - `memory/causality_ledger.json`
  - `bible/style_bible.md`
- 测试项目 `server_v02_smoke_test` 验证后已删除。

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

## 3 章 Smoke Test

2026-05-01 已执行一次正确 UTF-8 请求的 3 章生成：

```text
book_id: v02_3ch_smoke_20260501_1935
title: 我要送快递可是你非要我做董事长
```

执行结果：

- 主流程 execution：`52`，success。
- 单章 Worker：
  - `53`：第 1 章，success。
  - `54`：第 2 章，success。
  - `55`：第 3 章，success。
- 服务器目录：`/opt/autoGenerate/novel_projects/v02_3ch_smoke_20260501_1935`
- 本地已同步：`novel_projects/v02_3ch_smoke_20260501_1935`

章节结果：

| 章节 | 标题 | 字符数 | QA 总分 | major_conflict | needs_rewrite | needs_manual_review |
| --- | --- | ---: | ---: | --- | --- | --- |
| 1 | 骑手进董事会 | 5634 | 89 | false | true | true |
| 2 | PPT里一切正常 | 4656 | 91 | false | false | false |
| 3 | 董事长下仓 | 4484 | 91 | false | true | true |

观察：

- UTF-8 请求后，标题、题材、核心钩子均正确落入“快递骑手被推上董事长”的方向。
- 原有 3 章循环未被 V0.2 资产层破坏。
- QA 仍存在此前问题：高分且无重大冲突时仍可能标记 `needs_rewrite=true`、`needs_manual_review=true`。
- V0.2 的新文件已经初始化，但当前 N8N workflow 还没有生成/使用人物卡、金手指、风格圣经、因果规划、伏笔规划、去 AI 审计、风格审计等节点。

过程问题：

- 第一次测试使用 ASCII shell 脚本触发 webhook，中文标题被写成 `???????????????`，导致模型按未知标题生成了悬疑档案题材。
- 错误测试项目 `v02_3ch_smoke_20260501_1850` 已清理。
- 后续触发含中文的 N8N webhook，必须使用 UTF-8 请求文件或 JSON unicode escape，不能用 ASCII 写 shell 内嵌中文。
