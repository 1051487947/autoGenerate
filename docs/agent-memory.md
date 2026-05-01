# Agent Memory

## 2026-04-26 N8N 服务器排查

- 服务器：`8.140.56.75`，SSH 端口 `22` 可达，主机名 `iz2zeibnqthwmywf9csshyz`。
- N8N 部署方式：Docker Compose，目录为 `/opt/n8n-cn`。
- Compose 文件：`/opt/n8n-cn/docker-compose.yml`。
- 数据目录：`/opt/n8n-cn/data` 挂载到容器 `/home/node/.n8n`。
- 容器：`n8n-cn`，镜像 `n8nio/n8n:latest`，端口 `0.0.0.0:5678->5678/tcp`，重启策略 `unless-stopped`。
- 健康检查：`curl http://127.0.0.1:5678/healthz` 返回 `{"status":"ok"}`，编辑器页面可访问。
- N8N 版本：`1.76.1`。
- 当前数据库：`/opt/n8n-cn/data/database.sqlite`，大小约 `389120` 字节，最后修改时间 `2026-04-19 15:11 CST`。
- 当前库内数据：`workflow_entity=0`，`credentials_entity=0`，`execution_entity=0`，`user=1`（空用户信息）。
- `docker exec n8n-cn n8n list:workflow` 未列出工作流。
- 已搜索 `/opt`、`/root`、`/home`、`/var/lib/docker/volumes` 下的 N8N SQLite、workflow JSON、备份文件，只发现当前这份空库，未发现旧 N8N 工作流备份。
- 服务器上另有小说归档服务：
  - `/opt/novel-archive`，端口 `18082`，将内容写入文件归档。
  - `/opt/kodbox-novel-archive`，端口 `18083`，通过 KodBox API 写入 `novel_archive`。
  - KodBox 中发现示例归档文件：`/kodbox/site/data/files/novel_archive/20260419_095854_kodbox_smoke.md`、`/kodbox/site/data/files/novel_archive/20260419_100252_夜港协议.md`。
- N8N 日志提示 `/home/node/.n8n/config` 权限为 `0644` 偏宽，可后续设置 `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true` 或修正权限。

### 结论

当前运行中的 N8N 服务是健康的，但数据库为空，没有“写小说”的 N8N 工作流、凭据或执行记录。该工作流如果曾存在，可能在其他服务器、其他历史备份、浏览器导出文件、本地文件，或曾经部署时没有挂载持久化目录而被容器重建覆盖。

### 常用只读排查命令

```powershell
plink.exe -ssh root@8.140.56.75 -P 22 -pw '<password>' -batch 'docker ps -a'
plink.exe -ssh root@8.140.56.75 -P 22 -pw '<password>' -batch 'sqlite3 -header -column /opt/n8n-cn/data/database.sqlite "select count(*) from workflow_entity;"'
plink.exe -ssh root@8.140.56.75 -P 22 -pw '<password>' -batch 'curl -sS http://127.0.0.1:5678/healthz'
```

## 2026-04-26 AI 小说 N8N 工作流架构讨论

- 基本判断：用 N8N 编排 AI 小说生产流程是正确方向，但 N8N 应定位为“调度与状态治理系统”，不是直接负责创作的唯一 AI。
- 长篇小说核心难点不是单次生成正文，而是长期一致性、状态持久化、上下文检索、版本管理和人工干预。
- 推荐把创作流程拆成：设定库 -> 总纲/分卷/章节大纲 -> 场景拆解 -> 场景生成 -> 合并润色 -> 一致性审查 -> 摘要/状态更新 -> 版本归档。
- 状态管理应分层：
  - 全局状态：世界观、核心人设、势力关系、文风规则、禁忌规则。
  - 滑动窗口：最近 2-3 章摘要或关键正文片段。
  - 关键事实：受伤、装备、关系变化、伏笔、地点状态等必须可持续追踪。
- 不建议直接“一次生成一整章”。更稳的粒度是先拆成 3-5 个场景，逐场景生成，再统一合并润色。
- 多模型协作有价值：逻辑模型负责大纲、推演、漏洞检查；文风模型负责正文扩写和润色；审核模型负责找设定矛盾、吃书、节奏问题。
- RAG/知识库不应只是资料文档，而应能按角色、地点、道具、事件、伏笔等实体检索相关上下文，动态注入 Prompt。
- N8N 工作流应加入人工干预节点：当逻辑评分低、设定冲突、章节质量不达标时暂停流程，等待人工修改或确认后继续。
- 所有输出应保留版本，不直接覆盖。可用 Git、数据库版本号、Notion 历史或文件命名方式保存大纲、场景、正文、摘要和审稿结果。
- 下一步优先级建议：先做“设定库 + 场景级生成 + 摘要/关键事实回写”的最小闭环，再扩展多模型路由、自动审稿和发布流程。

## 2026-04-26 N8N 工作流查看权限状态

- 用户表示已将工作流导入 N8N，目标是查看并优化现有流程。
- 本地项目目录未发现 N8N workflow JSON 导出文件。
- N8N Web 地址 `http://8.140.56.75:5678` 可打开，但浏览器会话停在登录页 `/signin`。
- `http://8.140.56.75:5678/healthz` 返回 `{"status":"ok"}`。
- `http://8.140.56.75:5678/rest/workflows` 返回 `401 Unauthorized`，需要 N8N 登录态或 API 凭据。
- 已尝试服务器侧 SSH：
  - `ssh -o BatchMode=yes root@8.140.56.75 ...` 未获得免密登录。
  - `plink.exe -v -ssh root@8.140.56.75 -P 22 -batch ...` 能连接到 SSH 端口，但最终提示 `User aborted during password authentication`。
- 结论：当前已知服务器地址和 N8N 部署线索，但本机没有可用的 SSH/N8N 认证状态；需要用户提供 N8N 登录、SSH 密码/密钥，或直接导出 workflow JSON 后才能查看节点详情。

## 2026-04-26 N8N 工作流 JSON 初审

- 已收到工作流导出文件：`C:\Users\Administrator\Downloads\Novel MVP - Agent Skill Guarded.json`。
- 工作流名称：`Novel MVP - Agent Skill Guarded`，导出状态为 `active: true`。
- 当前主链路：Webhook/Manual Trigger -> Init Params -> Skill Router -> Skill Preflight -> Outline -> Parse Outline -> Split In Batches -> Continuity Context -> Draft -> Edit -> QA -> Evidence Gate -> Archive Chapter -> Collect Chapter -> Finalize Book -> Archive Full。
- 结构优点：
  - 已有 Skill Registry / Preflight / Evidence Gate，说明流程有“能力证明”和治理意识。
  - 已有 Outline、Draft、Edit、QA、Archive 分层，不是简单单次生成。
  - 已有最近 3 章滑动上下文雏形。
  - 已有 KodBox 章节级与全书级归档节点。
- 关键问题：
  - `Archive Chapter To Kodbox` 后直接进入 `Collect Chapter`，如果 HTTP Request 节点不回显原始输入，`Collect Chapter` 会拿到归档接口响应而不是章节正文，导致 `chapterIndex/finalText/qa` 丢失。优先改为先 `Collect Chapter` 再归档，或让 HTTP Request 保留/合并输入数据。
  - `Parse Outline` 将 `g.fullOutline` 写成 `arcOutline`，但 `Prepare Continuity Context` 用 `chapterIndex` 去查找下一章；`arcOutline` 没有 `chapterIndex`，因此 `nextChapterTitle/nextChapterGoal` 基本为空。应持久化 `obj.chapters` 为 chapter plan。
  - 使用 `$getWorkflowStaticData('global')` 存储章节、上下文和失败次数，存在并发执行串数据、失败残留污染下一次运行的问题。运行态数据应带 runId/bookId，或放入数据库/文件/外部状态服务。
  - `Parse Outline` 重置了 `g.generatedChapters`，但没有同步重置 `g.chapters`；如果流程中途失败，下一次执行可能混入旧章节。
  - QA 失败后进入 `QA Fail Handler` 但没有后续重试、人工确认或通知节点，当前更像“终止记录”，还不是闭环。
  - 当前仍是“章节级生成”，还没有真正拆到 Scene 级，也没有关键事实抽取/回写/RAG 检索。
- 优先优化顺序：
  1. 修复 Collect 与 Archive 的数据传递顺序。
  2. 修复 chapter plan / next chapter context。
  3. 引入 runId/bookId，隔离全局静态数据。
  4. 增加章节后摘要与关键事实抽取。
  5. 再做 Scene 级拆解、RAG、多模型路由和人工审批。

## 2026-04-26 AI 中长篇小说架构复盘

- 当前总体思路成立：用 N8N 做“小说生产调度器”，用 GPT 类模型做逻辑导演/审稿，用 Kimi 类中文模型做正文扩写/润色，是合理的双模型架构。
- 需要警惕的点：目标可以是“只输入标题自动生成”，但工程实现不能从全自动长篇开始。更稳的路线是先把“单章闭环”跑通，再扩展到“整卷/整书批处理”。
- 不建议把所有能力都塞进一个巨大 N8N Workflow。推荐拆成多个子流程：
  - `seed_planner`：标题 -> 题材定位、世界观种子、主角/反派、主线冲突。
  - `book_architect`：故事种子 -> 分卷大纲、章节列表、关键伏笔。
  - `chapter_planner`：章节目标 -> 3-5 个场景。
  - `scene_writer`：场景卡 + 上下文 -> 正文片段。
  - `chapter_editor`：合并场景、统一文风、消除重复。
  - `critic_auditor`：逻辑审查、设定一致性、节奏评分。
  - `memory_archivist`：摘要、关键事实、角色状态、伏笔状态回写。
- 本地工程文件是必需的，不只是可选项。N8N 适合编排，但不适合承载全部知识资产。建议项目目录长期维护：
  - `data/world.md`：世界观、力量体系、历史规则。
  - `data/characters.json`：角色状态表，记录位置、生死、关系、能力、秘密。
  - `data/foreshadowing.json`：伏笔池，记录引入章节、状态、预计回收位置。
  - `prompts/director.md`：GPT 导演提示词。
  - `prompts/writer_kimi.md`：Kimi 正文提示词。
  - `prompts/auditor.md`：审稿提示词。
  - `output/<book_id>/chapters/`：章节正文版本。
  - `output/<book_id>/summaries/`：章节摘要与关键事实。
  - `n8n_workflows/`：N8N 导出 JSON 备份。
- “只给标题生成全文”的推荐执行链路：
  1. 输入标题和可选参数，如题材、目标字数、读者定位、禁忌内容。
  2. GPT 生成故事种子和项目圣经。
  3. GPT 生成分卷/章节大纲，输出结构化 JSON。
  4. N8N 按章节循环，每章先由 GPT 拆场景。
  5. Kimi 逐场景扩写，避免一次生成整章导致漂移。
  6. GPT 审稿打分，低于阈值则重写或进入人工确认。
  7. 通过后归档正文，生成摘要、关键事实、角色状态更新。
  8. 每 5-10 章做一次全局复盘，检查主线是否偏离。
- 最小可用版本优先级：
  1. 标题 -> 故事种子 -> 章节大纲。
  2. 单章：章节目标 -> 场景拆解 -> Kimi 正文 -> GPT 审稿 -> Markdown 归档。
  3. 章节后自动摘要和关键事实回写。
  4. 再接入角色表、伏笔表、RAG 检索、多版本对比。
- 关键架构原则：长篇小说生成的核心不是“更长上下文”，而是“可维护状态”。所有会影响后文的事实都应该结构化保存，不能只藏在正文里。

## 2026-04-26 AI 小说系统下一阶段建设蓝图

- 总体定位：这套系统不应只是“自动写字机器”，而应是“作者工作台 + 编辑部 + 资料库 + 生产流水线”。AI 负责生成和分析，N8N 负责调度，本地工程负责承载可长期复用的创作资产。
- 从小说创作角度，最核心的不是先追求章节数量，而是先定义“故事发动机”：
  - 读者承诺：这本书到底满足读者什么期待，如升级爽感、悬疑反转、情绪陪伴、权谋博弈。
  - 主角欲望：主角长期想要什么，短期每章想要什么。
  - 阻力系统：反派、制度、资源、误会、时间限制如何持续制造压力。
  - 成长曲线：主角能力、关系、认知、代价如何逐步变化。
  - 章节钩子：每章结尾必须留下悬念、冲突升级、选择代价或信息反转。
- 从系统架构角度，推荐采用“三层记忆”：
  - Canon Memory：不可轻易改变的设定，如世界规则、主线终局、核心人物底层动机。
  - State Memory：会随章节变化的状态，如地点、伤势、装备、关系、阵营、伏笔状态。
  - Context Memory：生成当前章节时临时注入的上下文，如最近 3 章摘要、相关角色卡、相关地点卡。
- 每一章建议先生成“章节任务单”，再写正文。章节任务单至少包含：本章目标、出场人物、地点、冲突、情绪曲线、信息增量、状态变化、结尾钩子、禁止事项。
- 每个场景建议使用固定 Scene Card：场景目的、POV 角色、地点、参与角色、冲突、转折、付出代价、输出事实、下一场景衔接。Kimi 只根据 Scene Card 扩写，不负责临时改大逻辑。
- N8N 工作流后续应从单链路升级为可组合子流程：
  - `01_seed_from_title`：标题生成题材定位、卖点、主角、核心矛盾。
  - `02_story_bible`：生成并保存小说圣经。
  - `03_outline_architect`：生成卷纲和章节表。
  - `04_chapter_pipeline`：单章从任务单到正文归档。
  - `05_memory_update`：抽取摘要、事实、角色状态、伏笔状态。
  - `06_quality_review`：审稿、评分、重写、人工审批。
  - `07_export_publish`：导出 Markdown、Epub、Word 或归档到 KodBox。
- 质量控制不应只看“是否生成成功”，而应有评分维度：逻辑一致性、人设一致性、节奏密度、信息增量、情绪强度、文风一致性、重复表达、章节钩子强度。
- 人工介入点建议保留在三个位置：故事圣经确认、每卷大纲确认、低分章节/重大剧情节点确认。常规章节可以自动跑，但主线转折、人物死亡、感情线确认、世界规则变更不应完全放任自动化。
- 技术落地优先顺序：
  1. 建立本地小说工程目录和 Prompt 版本管理。
  2. 修复现有 N8N 工作流的数据传递、runId/bookId 隔离、章节计划持久化。
  3. 增加章节任务单和 Scene Card，不再直接按整章写。
  4. 增加 Memory Update 子流程，把正文中的事实结构化回写。
  5. 增加 Quality Gate，低分自动重写，高风险转人工。
  6. 再接入向量检索、多模型路由、全书一键生成。
- 长期目标：让“只输入标题”成为入口，但内部必须经历标题解析、故事圣经、大纲、章节任务单、场景卡、正文、审稿、记忆回写这些中间产物。中间产物越清晰，长篇越不容易崩。

## 2026-04-26 20 章 MVP 蓝图

- 已为第一轮“只做 20 章”的目标创建专门蓝图文档：`docs/novel-20ch-mvp-blueprint.md`。
- 示例标题：`我要送快递可是你非要我做董事长`。
- 设计重点：标题解析 -> 故事种子 -> 小说圣经 -> 20 章大纲 -> 章节任务单 -> 场景卡 -> Kimi 扩写 -> GPT 审稿 -> 摘要/状态回写 -> 20 章合订归档。
- 第一轮明确不做复杂向量库、百万字全自动、多平台发布、过多模型路由。先验证 20 章是否连续、好读、不吃书，并且每章都有摘要和状态变化。

## 2026-04-26 小说工厂工程落地

- 已创建小说工厂目录：`novel_factory/`。
- 已创建 Prompt 模板目录：`novel_factory/prompts/`，包含标题生成故事种子、小说圣经、20 章大纲、章节任务单、场景卡、Kimi 场景扩写、章节合并、GPT 审稿、记忆回写等 9 个模板。
- 已创建 JSON Schema 目录：`novel_factory/schemas/`，包含 `story_seed`、`chapter_plan`、`chapter_task`、`scene_card`、`qa_report`、`memory_update` 的结构约束。
- 已创建 N8N 节点映射文档：`novel_factory/n8n/20ch-workflow-node-map.md`。
- 已创建初始化脚本：`novel_factory/scripts/init_book_project.py`。
  - Python 路径遵循项目要求：`C:\Python311\python.exe`。
  - 示例命令：`C:\Python311\python.exe .\novel_factory\scripts\init_book_project.py --title "我要送快递可是你非要我做董事长" --book-id kuaidi_dongshizhang`。
- 已用示例标题初始化项目：`novel_projects/kuaidi_dongshizhang/`。
- 示例项目已填充：
  - `bible/story_seed.json`
  - `bible/story_bible.md`
  - `bible/characters.json`
  - `bible/foreshadowing.json`
  - `outline/chapters_20.json`
  - `memory/state_memory.json`
  - `chapter_tasks/ch001.task.json`
  - `scenes/ch001.scenes.json`
- 已用 PowerShell `ConvertFrom-Json` 校验 `novel_factory` 和示例项目内 JSON 文件，结果均可正常解析。
- 后续用户给新标题时，按该流程生成完整依赖框架：初始化项目目录 -> 填故事种子 -> 填小说圣经 -> 填角色/伏笔/初始状态 -> 填 20 章大纲 -> 按章生成任务单和场景卡 -> 进入正文生成与审稿。

## 2026-04-26 N8N 与小说工厂集成方式

- 用户追问“这个工程结合 N8N 怎么用”，核心理解：`novel_factory` 是文件资产层和状态落盘层，N8N 是调度层；N8N 通过读取 Prompt/Schema、调用模型、保存产物来驱动整个 20 章流程。
- 已新增集成文档：`novel_factory/n8n/integration-guide.md`。
- 已新增轻量 HTTP Bridge：`novel_factory/scripts/novel_bridge.py`。
- Bridge 默认用途：让 N8N 通过 HTTP Request 节点访问本地小说工程，而不是在 N8N 节点里写死 Windows 路径和复杂文件逻辑。
- Bridge 启动示例：
  - `C:\Python311\python.exe .\novel_factory\scripts\novel_bridge.py --host 127.0.0.1 --port 8765 --token your_token`
- Bridge 主要接口：
  - `GET /health`
  - `POST /api/books/init`
  - `GET /api/prompts/<name>`
  - `GET /api/schemas/<name>`
  - `GET /api/books/<book_id>/read?path=<relative_path>`
  - `POST /api/books/<book_id>/write`
  - `GET /api/books/<book_id>/manifest`
- 已用 `C:\Python311\python.exe -m py_compile` 校验 `novel_bridge.py` 和 `init_book_project.py`。
- 已做 Bridge 冒烟测试：启动本地 `127.0.0.1:8765`，带 `X-Novel-Token` 访问 `/health` 和 `/api/prompts/01_seed_from_title.md` 成功。
- 关键部署判断：如果 N8N 在远程服务器 `8.140.56.75`，它不能直接读取本地 `G:\Documents\xiaoshuo`。第一轮建议把 `novel_factory` 部署到 N8N 同机，或让服务器通过 Bridge/VPN/内网穿透访问本地工程。

## 2026-04-26 AI 小说版本维护建议

- 用户担心直接发布到 KodBox 不好维护。建议：KodBox 不作为生成过程主版本库，只作为通过质量闸门后的成品归档和阅读预览。
- 已创建版本维护策略文档：`docs/novel-versioning-strategy.md`。
- 推荐分层：
  - `novel_projects/<book_id>/`：主工作区，保存全部中间产物。
  - Git：版本控制、差异对比、回滚。
  - JSON/SQLite：结构化状态、运行记录、章节版本元数据。
  - KodBox：只保存 `export/full_book.md`、`chapters/*.final.md` 等成品。
- 第一轮 20 章 MVP 可全部用 GPT 跑通逻辑、正文、审稿、记忆回写。Kimi 暂未接入时，把 writer 节点也指向 GPT 即可，后续只替换写作节点模型。

## 2026-04-26 GitHub 管理建议

- 可以用 GitHub 管理 AI 小说工程，推荐使用 Private 仓库。
- 定位：本地 Git 仓库做主工作区，GitHub 做远程备份/版本对比/跨设备同步，KodBox 只做成品阅读和归档。
- 不建议 N8N 每生成一个小片段就 push；建议按关键阶段提交：故事种子、小说圣经、20 章大纲、每章定稿、20 章合订导出。
- 不应提交 API Key、Token、Cookie、N8N 凭据、`.env`、过大原始模型日志和临时缓存。
- 该策略已补充到 `docs/novel-versioning-strategy.md`。

## 2026-04-26 GitHub 仓库同步

- 用户提供 GitHub 克隆目录：`G:\Documents\autoGenerate`。
- 远程仓库：`https://github.com/1051487947/autoGenerate.git`。
- 已同步核心目录到 Git 仓库：
  - `docs/`
  - `novel_factory/`
  - `novel_projects/`
- 已新增根目录 `README.md`，说明仓库用途、目录结构、初始化新书命令和 N8N Bridge 启动命令。
- 已新增 `.gitignore`，排除密钥、环境文件、Python 缓存、N8N 本地噪声、日志、Playwright 临时文件、`%SystemDrive%/`、`NVIDIA Corporation/` 环境噪声目录和 `novel_projects/**/runs/` 原始运行日志。

## 2026-04-26 现有 N8N Workflow 升级判断

- 用户提供现有 workflow 文件：`C:\Users\Administrator\Downloads\Novel MVP - Agent Skill Guarded.json`，并说明该 workflow 已在服务器上。
- 已检查该 workflow：名称 `Novel MVP - Agent Skill Guarded`，共 28 个节点，当前链路为 Webhook/Manual -> Init -> Skill Guard -> Outline -> Draft -> Edit -> QA -> KodBox 归档。
- 结论：需要更新，但不需要推倒重做。旧 workflow 的大纲、正文、润色、QA 骨架可以复用。
- 主要问题：
  - 当前 LLM 节点使用 `/v1/messages`、`glm-5-turbo`、Anthropic 风格响应解析；如果先用 GPT 跑，需要改成 OpenAI/兼容网关，并解析 `choices[0].message.content`。
  - 当前状态大量依赖 `$getWorkflowStaticData('global')`，多运行/失败重试时容易串数据。
  - 当前归档直接走 KodBox，不适合作为过程版本库。
  - 当前没有接入 `novel_factory` 的 Prompt/Schema/Bridge，也没有把故事种子、圣经、大纲、章节任务单、场景卡等产物落到 Git 工作区。
- 已新增安全测试 workflow：`novel_factory/n8n/Novel Seed - Bridge GPT MVP.json`。
  - 用途：先跑通标题 -> Bridge 初始化项目 -> 读取 Prompt/Schema -> GPT 生成 `story_seed.json` -> Bridge 写回。
  - 该 workflow 不替换服务器上的旧 workflow，适合作为 V2 冒烟链路导入测试。
- 已新增升级说明：`novel_factory/n8n/existing-workflow-upgrade-notes.md`。

## 2026-04-26 服务器 Novel Bridge 部署配置

- 已通过 N8N 后端确认服务器当前有两个 workflow：
  - `ZfOcpJ2nHvEzjuos`：`小说工作流`，inactive，旧架构。
  - `CyRqZLtMyPxdOkpE`：`Novel Seed - Bridge GPT MVP`，inactive，新建 UTF-8 正常导入版。
- 曾首次导入 `YtUMjV7MPeqULw7n`，发现 PowerShell 默认提交导致中文变问号，已删除后用显式 UTF-8 重新导入。
- 公网访问 `http://8.140.56.75:8765/health` 超时，说明 Novel Bridge 尚未部署或未对外暴露。推荐 Bridge 只在 Docker 内网给 N8N 访问，不需要公网暴露。
- 已新增部署参考：
  - `novel_factory/deploy/docker-compose.novel-bridge.example.yml`
  - `novel_factory/deploy/server-deploy.md`
- 服务器侧下一步需要在 N8N Docker Compose 同机部署 `novel-bridge`，并给 N8N 容器增加环境变量：
  - `NOVEL_BRIDGE_URL=http://novel-bridge:8765`
  - `NOVEL_BRIDGE_TOKEN`
  - `OPENAI_BASE_URL`
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL=gpt-4o`

## 2026-04-26 端口开放权限判断

- 用户要求开放 `8765` 并从本地验证可达。
- 已从本地验证 `http://8.140.56.75:8765/health` 当前不可达/超时。
- 已尝试免密 SSH 到 `root@8.140.56.75`，未获得可用宿主机命令执行能力。
- 已确认 N8N 后端账号可以管理 workflow，但不能修改宿主机防火墙、Docker Compose 端口映射或云厂商安全组。
- 结论：开放公网 `8765` 需要 SSH/root 权限或云控制台安全组权限。仅凭 N8N 登录账号无法完成。
- 仍建议优先使用 Docker 内网访问 `http://novel-bridge:8765`，公网开放只作为调试选项。

## 2026-04-26 Novel Bridge 服务器部署完成

- 用户提供 SSH/root 权限后，已在服务器 `8.140.56.75` 上完成 Novel Bridge 部署与端口开放。
- 代码目录：`/opt/autoGenerate`，已从 GitHub 仓库拉取。
- N8N Compose 目录：`/opt/n8n-cn`。
- 新增 Compose override：`/opt/n8n-cn/docker-compose.override.yml`。
- 新增容器：
  - `novel-bridge`
  - 镜像：`python:3.11-slim`
  - 端口：`0.0.0.0:8765->8765/tcp`
  - 工作目录：`/workspace`
  - 挂载：`/opt/autoGenerate:/workspace`
- N8N 容器已重建并加载环境变量：
  - `NOVEL_BRIDGE_URL=http://novel-bridge:8765`
  - `NOVEL_BRIDGE_TOKEN` 已生成并保存在 `/opt/n8n-cn/.env`
  - `OPENAI_BASE_URL=https://api.openai.com`
  - `OPENAI_MODEL=gpt-4o`
- 为避免强制重建 N8N 时拉取最新 `n8nio/n8n:latest`，已将当前运行镜像打 tag 为 `n8n-local-current:preserve`，并在 override 中让 `n8n` 使用该本地镜像，避免意外升级。
- firewalld 已放行：`8765/tcp`。
- 验证结果：
  - 服务器本机无 token 请求 `http://127.0.0.1:8765/health` 返回 `401 Unauthorized`，符合预期。
  - 服务器本机带 token 请求返回 `{"status":"ok","root":"/workspace"}`。
  - N8N 容器内访问 `http://novel-bridge:8765/health` 带 token 返回 `200`。
  - 本地访问 `http://8.140.56.75:8765/health` 无 token 返回 `401`，说明公网端口可达且鉴权生效。
  - 本地带 token 访问返回 `{"status":"ok","root":"/workspace"}`。
- 当前仍未配置真实 `OPENAI_API_KEY`。运行 `Novel Seed - Bridge GPT MVP` 前，需要在 `/opt/n8n-cn/.env` 中补充 `OPENAI_API_KEY` 并重建 N8N 容器，或通过其他安全方式注入。

## 2026-04-26 自定义 OpenAI 兼容模型接入完成

- 用户提供自定义 OpenAI 兼容网关和 API Key。Key 只写入服务器 `/opt/n8n-cn/.env`，未写入 GitHub 或文档。
- 已配置：
  - `OPENAI_BASE_URL=https://codexa.leizhen.cloud`
  - `OPENAI_MODEL=gpt-5.4`
  - `OPENAI_API_KEY` 已写入服务器 `.env`
- 已验证网关 `/v1/models` 可用，可用模型包括 `gpt-5.4`、`gpt-5.4-mini`、`gpt-5.5` 等。
- 已验证 `gpt-5.4` 的 `/v1/chat/completions` 可用，支持 `response_format: { "type": "json_object" }`。
- 已重建 N8N 容器，确认 N8N 容器内环境变量加载成功，并能直接调用自定义网关返回 `200`。
- 已修复 `Novel Seed - Bridge GPT MVP` workflow 的解析兼容问题：
  - 自定义网关响应有时会被 N8N HTTP Request 节点作为字符串或 `data` 包装传给下游。
  - `Parse Story Seed` 已改为兼容字符串、`data`、`body` 和标准 `choices[0].message.content`。
  - `Init Params` 默认 `openai_model` 已改为空字符串，优先使用服务器环境变量 `OPENAI_MODEL`。
- 已激活并通过公网 Webhook 跑通完整最小闭环：
  - 请求：`POST http://8.140.56.75:5678/webhook/novel-seed-bridge-gpt`
  - 测试 `book_id`：`kuaidi_dongshizhang_server_test`
  - 返回：`{"ok":true,"saved_path":"bible/story_seed.json"}`
  - 落盘文件：`/opt/autoGenerate/novel_projects/kuaidi_dongshizhang_server_test/bible/story_seed.json`

## 2026-04-26 N8N Bootstrap 链路扩展到小说圣经与 20 章大纲

- 已继续扩展 `Novel Seed - Bridge GPT MVP` workflow。
- 当前链路：
  - Webhook 输入标题。
  - Bridge 初始化书籍项目。
  - 读取 `01_seed_from_title.md` 和 `story_seed.schema.json`。
  - GPT 生成并保存 `bible/story_seed.json`。
  - 读取 `02_story_bible.md`。
  - GPT 生成并保存 `bible/story_bible.md`。
  - 读取 `03_outline_20.md` 和 `chapter_plan.schema.json`。
  - GPT 生成并保存 `outline/chapters_20.json`。
- Webhook 已改为 `responseMode=onReceived`，长任务会立即返回 `{"message":"Workflow was started"}`，实际结果以 N8N execution 和文件落盘为准。
- 已测试 `book_id=kuaidi_dongshizhang_story_bible_test`：
  - 执行成功。
  - `bible/story_bible.md` 已落盘，大小约 27KB。
- 已测试 `book_id=kuaidi_dongshizhang_outline_test`：
  - 执行成功。
  - `outline/chapters_20.json` 已落盘，包含 20 章。
  - 前三章为：
    - 第 1 章：`快递送进董事会`
    - 第 2 章：`想辞职的人先被锁死`
    - 第 3 章：`董事会不讲人话`
- 当前下一步：基于 `chapters_20.json` 生成第 1 章任务单和场景卡，然后再接正文生成。

## 2026-04-26 N8N Workflow 扩展到第 1 章任务单与场景卡

- 已将 `Novel Seed - Bridge GPT MVP` workflow 从 22 个节点扩展到 34 个节点。
- 当前 active workflow ID 仍为 `CyRqZLtMyPxdOkpE`，旧 workflow `ZfOcpJ2nHvEzjuos` 未改动。
- 当前链路：
  - Webhook 输入标题。
  - Bridge 初始化书籍项目。
  - GPT 生成并保存 `bible/story_seed.json`。
  - GPT 生成并保存 `bible/story_bible.md`。
  - GPT 生成并保存 `outline/chapters_20.json`。
  - GPT 生成并保存 `chapter_tasks/ch001.task.json`。
  - GPT 生成并保存 `scenes/ch001.scenes.json`。
- 已新增服务器 workflow 更新脚本：`novel_factory/deploy/update_n8n_sqlite_workflow.py`。
  - 用途：在服务器 Docker 环境中，从仓库 workflow JSON 覆盖更新 N8N SQLite 中已有 workflow。
  - 运行方式示例：
    - `docker run --rm -v /opt/autoGenerate:/workspace -v /opt/n8n-cn:/n8n python:3.11-slim python /workspace/novel_factory/deploy/update_n8n_sqlite_workflow.py --workflow-id CyRqZLtMyPxdOkpE`
  - 脚本会先备份原 workflow 到 `/opt/n8n-cn/backups/workflow_<id>_<timestamp>.json`。
- 关键稳定性调整：
  - 模型 HTTP Request 节点增加 `timeout: 300000`，避免模型长时间无响应导致流程无限挂起。
  - Story Bible 生成提示词限制为 3500-6000 中文字符，避免初期设定稿过长拖慢 MVP。
  - Webhook 恢复为 `responseMode=onReceived`：请求立即返回 `{"message":"Workflow was started"}`，后台继续生成文件。
  - `book_id` 截断长度从 48 放宽到 80，避免带时间戳的测试 ID 被过度截断。
- 已提交并推送相关 Git 提交：
  - `3c37a99 add chapter one task and scene card workflow`
  - `d3f010d add n8n sqlite workflow updater`
  - `3be803e add model request timeouts`
  - `fd04e68 restore async webhook and expand book id length`
- 已部署到服务器 `/opt/autoGenerate`，并通过更新脚本同步到 N8N SQLite。
- 最终异步 webhook 测试：
  - 请求返回：`{"message":"Workflow was started"}`。
  - 测试 `book_id`：`async_final_test_20260426_191242`。
  - N8N execution：`10`，状态 `success`。
  - 落盘目录：`/opt/autoGenerate/novel_projects/async_final_test_20260426_191242`。
  - 已确认生成文件：
    - `bible/story_seed.json`
    - `bible/story_bible.md`
    - `outline/chapters_20.json`
    - `chapter_tasks/ch001.task.json`
    - `scenes/ch001.scenes.json`
- 观察结论：
  - 同步 webhook `lastNode` 会等待数分钟，可能被 HTTP 层返回 `503`，但后台 execution 仍可能成功；MVP 更适合使用异步 `onReceived`，再通过文件落盘或 execution 状态查看结果。
  - 下一步应继续接正文生成：按 `scenes/ch001.scenes.json` 拆分场景，生成 `scenes/ch001_scene01.md` 等，再合并为 `chapters/ch001.md`。

## 2026-04-26 N8N Workflow 扩展到第 1 章正文、QA 与记忆回写

- 已将 `Novel Seed - Bridge GPT MVP` workflow 从 34 个节点扩展到 57 个节点。
- 当前 active workflow ID 仍为 `CyRqZLtMyPxdOkpE`，旧 workflow `ZfOcpJ2nHvEzjuos` 未改动。
- 新增链路：
  - 读取 `06_writer_kimi_scene.md`。
  - 基于 `scenes/ch001.scenes.json` 拆成多条场景正文请求。
  - 保存 `scenes/ch001_scene01.md`、`scenes/ch001_scene02.md` 等场景正文片段。
  - 读取 `07_chapter_editor.md`，合并润色为 `chapters/ch001.md`。
  - 读取 `08_critic_auditor.md` 和 `qa_report.schema.json`，保存 `review/ch001.qa.json`。
  - 读取 `09_memory_update.md` 和 `memory_update.schema.json`，保存 `memory/ch001.memory.json`。
- 已处理两个运行问题：
  - 场景正文节点原本会并发请求多个场景，触发自定义模型网关 `429 Concurrency limit exceeded`；已给 `OpenAI Scene Writer` 增加 batching：`batchSize=1`、`batchInterval=90000`。
  - `Done` 汇总节点使用 `.item` 访问多 item 节点时触发 n8n item linking 错误；已改为 `.all()[0].json`。
- 已提交并推送相关 Git 提交：
  - `15ff503 add chapter one writing qa memory workflow`
  - `87bf74d throttle scene writer requests`
  - `e4df1fc fix done node item access`
- 已部署到服务器 `/opt/autoGenerate`，并通过更新脚本同步到 N8N SQLite。
- 最终异步 webhook 测试：
  - 请求返回：`{"message":"Workflow was started"}`。
  - 测试 `book_id`：`chapter1_done_success_test_20260426_203123`。
  - N8N execution：`13`，状态 `success`。
  - 落盘目录：`/opt/autoGenerate/novel_projects/chapter1_done_success_test_20260426_203123`。
  - 已确认生成文件：
    - `bible/story_seed.json`
    - `bible/story_bible.md`
    - `outline/chapters_20.json`
    - `chapter_tasks/ch001.task.json`
    - `scenes/ch001.scenes.json`
    - `scenes/ch001_scene01.md` 至 `scenes/ch001_scene05.md`
    - `chapters/ch001.md`
    - `review/ch001.qa.json`
    - `memory/ch001.memory.json`
- 验证数据：
  - `chapters/ch001.md` 长度约 `4752` 字符。
  - QA 总分 `88`。
  - QA 标记 `needs_rewrite=true`、`needs_manual_review=true`，但 `major_conflict=false`。
- 当前观察：
  - 第一章闭环已经跑通，但 QA 规则需要再优化；高分章节不应默认进入强制重写和人工确认，建议把 `needs_rewrite` 与 `needs_manual_review` 的判断规则显式写入 prompt 或增加 Code 节点二次归一化。
  - 下一步应做“QA 修订闭环”：当 QA 只是定点问题时，自动生成一版 `chapters/ch001.revised.md`，并保留原始 `chapters/ch001.md` 作为版本对照。
  - 再下一步才建议推广到 20 章循环，避免把单章质量门槛的问题放大到整本书。

## 2026-04-26 章节循环 Worker 修复与 2 章验证

- 背景：用户指出当前流程看起来都是第 1 章相关，担心没有真正的章节循环。
- 已确认旧的 `Novel Seed - Bridge GPT MVP` 是第 1 章硬编码 MVP；新的循环设计应使用：
  - 主流程：`novel_book_loop_mvp` / `Novel Book Loop MVP`
  - 单章子流程：`novel_single_chapter_worker` / `Novel Single Chapter Worker`
- 已修复 `Novel Single Chapter Worker` 中 `Build Scene Draft Requests` 的 JS 转义问题：
  - 原写法：`join('\n')`
  - 在 n8n 反序列化后会变成 JS 字符串里的真实换行，导致 `Unterminated string constant`。
  - 新写法：`join(String.fromCharCode(10))`，避免转义被 n8n 二次解释。
- 已用 Node 对 `Novel Single Chapter Worker.json` 和 `Novel Book Loop MVP.json` 的所有 Code 节点做语法预检，结果通过。
- 已提交并推送 GitHub：
  - `754dcfd fix scene draft worker newline join`
- 已部署到服务器 N8N SQLite：
  - 更新目标 workflow：`novel_single_chapter_worker`
  - 更新后节点数：37
  - 服务器备份：`/opt/n8n-cn/backups/workflow_novel_single_chapter_worker_20260426_134240.json`
- 已完成 1 章 smoke：
  - 测试书 ID：`loop_worker_smoke2_20260426_214300`
  - 主执行：`16`，`novel_book_loop_mvp`，success
  - 子执行：`17`，`novel_single_chapter_worker`，success
  - 生成文件包含：
    - `outline/chapters_20.json`
    - `chapter_tasks/ch001.task.json`
    - `scenes/ch001.scenes.json`
    - `scenes/ch001_scene01.md` 至 `scenes/ch001_scene05.md`
    - `chapters/ch001.md`
    - `review/ch001.qa.json`
    - `memory/ch001.memory.json`
- 已完成 2 章循环验证：
  - 测试书 ID：`loop_worker_2ch_20260426_215817`
  - 主执行：`18`，`novel_book_loop_mvp`，success
  - 第 1 章 Worker：`19`，success
  - 第 2 章 Worker：`20`，success
  - 关键证据：
    - 第 1 章完成后，主流程自动启动第 2 章 Worker。
    - 已生成 `chapter_tasks/ch002.task.json`、`scenes/ch002.scenes.json`、`chapters/ch002.md`、`review/ch002.qa.json`、`memory/ch002.memory.json`。
  - 第 1 章标题：`# 第1章 这单送完我就辞职`，约 5149 字符。
  - 第 2 章标题：`# 第2章 会议室里来了个送件的`，约 4023 字符。
  - 两章 QA 总分均为 `89`，`major_conflict=false`，但仍为 `needs_rewrite=true`。
- 当前结论：
  - “章节循环”已经被运行验证，不再是只生成第 1 章的硬编码链路。
  - 当前主要风险已从“流程结构错误”转为“质量门槛和自动精修策略”：高分但有定点问题的章节应进入自动精修，而不是简单视为失败。
- 建议下一步：
  - 增加 QA 归一化规则：例如 `total_score >= 85` 且 `major_conflict=false` 时，`needs_rewrite` 视为 `needs_polish`。
  - 增加 `chapter_revision` 节点：根据 `rewrite_instruction` 生成 `chapters/chXXX.revised.md`，保留原稿。
  - 再跑 `start_chapter=1,end_chapter=3` 或直接低速跑 20 章，验证长期状态回写是否稳定。

## 2026-04-26 3 章连续循环验证

- 用户确认继续后，已触发 `Novel Book Loop MVP` 的 1-3 章连续验证。
- 测试书 ID：`loop_worker_3ch_20260426_223237`。
- 请求参数：
  - `start_chapter=1`
  - `end_chapter=3`
  - `max_chapters_per_run=3`
  - 标题：`我要送快递可是你非要我做董事长`
- N8N 执行结果：
  - 主流程执行：`21`，`novel_book_loop_mvp`，success。
  - 第 1 章 Worker：`22`，success。
  - 第 2 章 Worker：`23`，success。
  - 第 3 章 Worker：`24`，success。
- 已生成正文：
  - `chapters/ch001.md`，标题：`# 第1章 董事长的工牌挂在快递员脖子上`，约 4515 字符。
  - `chapters/ch002.md`，标题：`# 第2章 第一场会，谁也别跟我讲黑话`，约 4972 字符。
  - `chapters/ch003.md`，标题：`# 第3章 讨薪的人比报表诚实`，约 5434 字符。
- 每章均已生成对应产物：
  - `chapter_tasks/ch00X.task.json`
  - `scenes/ch00X.scenes.json`
  - `scenes/ch00X_sceneYY.md`
  - `chapters/ch00X.md`
  - `review/ch00X.qa.json`
  - `memory/ch00X.memory.json`
- QA 概况：
  - 第 1 章：`total_score=89`，`major_conflict=false`，`needs_rewrite=true`，`needs_manual_review=true`。
  - 第 2 章：`total_score=91`，`major_conflict=false`，`needs_rewrite=true`，`needs_manual_review=false`。
  - 第 3 章：`total_score=92`，`major_conflict=false`，`needs_rewrite=true`，`needs_manual_review=false`。
- 结论：
  - 主流程已经稳定验证到 3 章连续循环，不是只跑第 1 章。
  - 当前执行速度大约 10 分钟/章，完整 20 章预计约 3 小时上下，主要瓶颈是模型长文本生成。
  - QA 仍然偏保守：89-92 分且无重大冲突时仍标记 `needs_rewrite=true`，后续应优先做 `needs_polish` 和自动精修闭环。

## 2026-04-27 完整 20 章原稿生成验证

- 在 3 章验证成功后，已启动完整 20 章生成。
- 第一次完整 20 章尝试：
  - 测试书 ID：`full20_draft_20260426_230549`。
  - 结果：失败。
  - 失败节点：`OpenAI Scene Writer`，第 1 章第 4 个场景。
  - 错误：`502 Bad gateway`，`Upstream stream ended without a terminal response event`。
  - 判断：模型网关/上游流式响应中断，不是章节循环逻辑错误。
- 已修复稳定性：
  - 给 `Novel Single Chapter Worker` 中所有 OpenAI HTTP 节点添加 n8n 原生重试：
    - `retryOnFail=true`
    - `maxTries=3`
    - 普通模型节点 `waitBetweenTries=60000`
    - `OpenAI Scene Writer` 为 `waitBetweenTries=120000`
  - 给 `Novel Book Loop MVP` 中书籍级 OpenAI 节点也添加同样重试。
  - 已提交并推送：`9f3761f add retries to novel model requests`。
  - 已部署到服务器 N8N SQLite：
    - `novel_single_chapter_worker`
    - `novel_book_loop_mvp`
- 第二次完整 20 章生成：
  - 测试书 ID：`full20_retry_20260426_232722`。
  - 主执行：`27`，`novel_book_loop_mvp`，success。
  - 子执行：`28` 至 `47`，20 个单章 Worker 全部 success。
  - 总耗时：约 3 小时 16 分钟，从 `2026-04-26 23:27` 到 `2026-04-27 02:43`（北京时间）。
- 已生成并同步到本地：
  - `novel_projects/full20_retry_20260426_232722/chapters/ch001.md` 至 `ch020.md`
  - `review/ch001.qa.json` 至 `ch020.qa.json`
  - `memory/ch001.memory.json` 至 `ch020.memory.json`
  - `chapter_tasks/ch001.task.json` 至 `ch020.task.json`
  - `scenes/ch001.scenes.json` 至 `ch020.scenes.json`
  - `export/full_book.md`
- 合订本：
  - 初始 `export/full_book.md` 只是占位文件，后已用 Python 重新按 UTF-8 合并 20 章。
  - 文件：`novel_projects/full20_retry_20260426_232722/export/full_book.md`
  - 大小约 300KB，约 10.4 万中文字符。
- 章节标题：
  - 第 1 章：`骑手被请进董事会`
  - 第 2 章：`临时董事长，工服没换`
  - 第 3 章：`第一场会，没人说人话`
  - 第 4 章：`报表说稳定，仓库在冒烟`
  - 第 5 章：`一张调度单，撕开第一道口子`
  - 第 6 章：`站点炸了，没人肯再赔`
  - 第 7 章：`董事长下场抢单`
  - 第 8 章：`赵姐不听战略，只问今天送不送得到`
  - 第 9 章：`先救午高峰，再谈明天`
  - 第 10 章：`热搜比单量跑得更快`
  - 第 11 章：`系统没疯，是有人让它疯`
  - 第 12 章：`谁都说为大局，赔钱的是底下人`
  - 第 13 章：`高价挖人，挖的是信心`
  - 第 14 章：`名单是怎么漏出去的`
  - 第 15 章：`先卸他的椅子`
  - 第 16 章：`锅已经扣下来，人得先救出来`
  - 第 17 章：`顺着一条日志，摸到一只手`
  - 第 18 章：`他抢人，我抢真相`
  - 第 19 章：`董事会上，把单号一笔一笔摊开`
  - 第 20 章：`这公司，我先不让它倒`
- QA 概况：
  - 20 章均 `major_conflict=false`。
  - 总分范围大致为 `89-92`。
  - QA 仍偏保守，多章高分但仍标记 `needs_rewrite=true` 或 `needs_manual_review=true`。
- 当前结论：
  - 标题 -> 20 章大纲 -> 逐章任务单 -> 场景卡 -> 场景正文 -> 合章 -> QA -> 记忆回写 -> 合订本的完整原稿闭环已经跑通。
  - 下一阶段重点应从“能不能生成 20 章”转为“如何自动精修和定稿”。

## 2026-04-27 单章运行耗时基准

- 统计样本：`full20_retry_20260426_232722` 这轮完整 20 章生成。
- 统计对象：N8N execution `28` 至 `47`，即 20 个 `novel_single_chapter_worker` 子流程。
- 单章 Worker 总耗时：约 `192.78` 分钟。
- 单章平均耗时：约 `9分38秒`。
- 单章中位数：约 `10分02秒`。
- 最快一章：约 `8分14秒`。
- 最慢一章：约 `10分43秒`。
- 主流程总耗时：约 `3小时16分29秒`，从 `2026-04-26 23:27:21` 到 `2026-04-27 02:43:50`（北京时间）。
- 如果把标题初始化、故事种子、小说圣经、20 章大纲等前置流程摊到 20 章中，约 `9分49秒/章`。
- 估算建议：
  - 按当前串行配置，单章预算按 `10分钟` 估比较稳。
  - 20 章完整原稿预算按 `3小时15分钟` 到 `3小时30分钟` 比较稳。

## 2026-04-27 系统架构文档

- 已新增完整架构文档：`docs/novel-system-architecture.md`。
- 文档内容覆盖：
  - 当前总体定位：N8N 编排、Novel Bridge 文件网关、`novel_factory` 工程资产、`novel_projects` 产物、GitHub 版本管理。
  - 服务器部署结构：`n8n-cn`、`novel-bridge`、`/opt/autoGenerate`、`/opt/n8n-cn`。

## 2026-04-27 小说生成架构问题复盘

- 用户要求检查此前生成过程中暴露出的架构性问题。
- 已新增复盘文档：`docs/novel-architecture-issues-review.md`。
- 核心结论：
  - 历史上主要问题包括：旧流程硬编码第 1 章、全局静态状态容易串数据、KodBox 不适合做过程版本库、n8n Code 节点换行转义错误、场景正文并发触发模型网关 429、长文本生成遇到 502、`.item` 多 item 链接错误、合订本 UTF-8 合并风险。
  - 当前 20 章完整原稿已经跑通，主流程架构成立。
  - 仍需补强：QA 归一化、自动精修闭环、强状态机记忆、RAG/检索、Kimi 写作模型接入、合订本 N8N 节点化、关键剧情人工审核。

## 2026-04-27 长期故事记忆与去 AI 味优化方向

- 用户补充关键判断：后续优化 N8N 不应只新增“AI 润色节点”，而要增加长期故事记忆层。
- 已沉淀方案文档：`docs/n8n-novel-logic-humanization-foreshadowing.md`。
- 核心改造：
  - 新增 `memory/foreshadow_ledger.json`、`memory/character_arc_ledger.json`、`memory/causality_ledger.json` 三类账本。
  - 章节循环新增 `Foreshadow Planner`、`Logic Causality Planner`、`Logic Humanization Auditor`、`Foreshadow Auditor`、`Foreshadow Ledger Update`。
  - QA Gate 新增硬规则：`logic_ai_risk <= 45`、`foreshadow_score >= 75`、最近 3 章至少 1 个中伏笔、最近 6 章至少回收 1 个伏笔、主角不能连续 3 章全程判断正确、章末钩子类型不能连续 3 章相同。
  - 最关键节点是 `Logic Causality Planner`，每章生成前必须明确“为什么这事现在发生、谁获利、谁付代价、缺什么信息、主角犯什么错”。
- 后续优化路线：
  - 先补账本 Schema 和初始化模板。
  - 再改 `Build Chapter Context`，让三类账本进入章节输入。
  - 然后加入生成前规划器和生成后审计器。
  - 最后再做 Kimi、RAG、自动精修和人工审核节点。

## 2026-05-01 人物卡与金手指建模确认

- 用户追问当前整体设计是否已有人物卡和金手指。
- 当前判断：
  - 已有人物卡雏形，但没有独立的人物卡系统。
  - 金手指目前藏在 `story_seed`、`story_bible` 和章节爽点机制里，还没有独立建模。
- 已补充方案文档：`docs/n8n-novel-logic-humanization-foreshadowing.md`。
- 建议后续新增：
  - `character_card.schema.json`
  - `bible/golden_finger.json`
  - `memory/golden_finger_ledger.json`
  - 人物卡和金手指都要进入 `Build Chapter Context`

## 2026-05-01 中长篇小说系统扩展设计调研

- 用户要求从中长篇小说专家、GitHub 开源项目、去 AI 化、文风一致性、AI 观念和措辞规避几个角度继续扩展设计。
- 已新增文档：`docs/novel-system-expanded-design-considerations.md`。
- 调研参考的公开项目包括：
  - `NousResearch/autonovel`
  - `RhythmicWave/NovelForge`
  - `iLearn-Lab/NovelClaw`
  - `forsonny/book-os`
  - `LewdLeah/Auto-Cards`
  - `bal-spec/sillytavern-character-memory`
  - `pixelnull/sillytavern-DeepLore-Enhanced`
  - `principia-ai/WriteHERE`
  - `sam-paech/slop-forensics`
  - `EQ-Bench/creative-writing-bench`
- 新增建议方向：
  - 读者承诺账本、压力账本、信息差账本、反派行动账本、场景功能账本、章末钩子账本。
  - 去 AI 化增加 `Friction Planner`、`Dialogue Humanization Auditor`、`Anti-AI Phrase Auditor`。
  - 文风一致性增加 `style_bible.md`、`voice_fingerprint.json`、`review/chXXX.style.json`。

## 2026-05-01 小说工厂 V0.2 落地

- 用户确认不再继续大范围分析，先落地一个版本。
- 已新增 V0.2 实现文档：`docs/novel-v0.2-implementation.md`。
- 已新增 Prompt：
  - `10_character_cards.md`
  - `11_golden_finger.md`
  - `12_style_bible.md`
  - `13_voice_fingerprint.md`
  - `14_logic_causality_planner.md`
  - `15_foreshadow_planner.md`
  - `16_anti_ai_audit.md`
  - `17_style_consistency_auditor.md`
- 已新增 Schema：
  - `characters.schema.json`
  - `golden_finger.schema.json`
  - `foreshadow_plan.schema.json`
  - `causality_plan.schema.json`
  - `voice_fingerprint.schema.json`
  - `anti_ai_audit.schema.json`
  - `style_audit.schema.json`
- 已升级 `novel_factory/scripts/init_book_project.py`，新书初始化会创建人物卡、金手指、文风圣经、反 AI 词表、长期账本和审计汇总文件。
- 已用 `C:\Python311\python.exe` 初始化测试项目 `v02_landing_test`，并验证新增 Schema 和项目 JSON 文件均可正常解析。
- 验证项目目录：`novel_projects/v02_landing_test` 和 `novel_projects/v02_landing_test_2`，均已生成人物卡、金手指、文风圣经、反 AI 词表和长期记忆账本占位文件；验证后已清理测试目录，不作为版本产物保留。
- 已提交并推送 GitHub：`7678d40 add novel factory v0.2 assets`。
- 已同步服务器 `/opt/autoGenerate` 的 `docs` 和 `novel_factory` 目录。
- 服务器直接 `git pull --ff-only` 被 `novel_projects/full20_retry_20260426_232722` 等未跟踪生成产物阻止；为避免覆盖生成内容，本次改用 `git fetch` 后按目录检出 `docs` 和 `novel_factory`。
- 已重启 `novel-bridge` 容器，确保 `/api/books/init` 加载新版初始化脚本。
- 服务器 Bridge 验证通过：
  - 可读取 `10_character_cards.md`、`17_style_consistency_auditor.md`。
  - 可读取 `characters.schema.json`。
  - `/api/books/init` 创建测试书后能生成 `bible/golden_finger.json`、`memory/causality_ledger.json`、`bible/style_bible.md`。
  - 测试书 `server_v02_smoke_test` 已清理。

## 2026-05-01 V0.2 三章生成 Smoke Test

- 先触发过一次 `v02_3ch_smoke_20260501_1850`，由于本地 shell 脚本用 ASCII 写入请求，中文标题变成 `???????????????`，导致模型生成成悬疑档案题材；该错误测试目录已清理。
- 已改用 UTF-8 JSON 请求文件重新触发：
  - `book_id`: `v02_3ch_smoke_20260501_1935`
  - 标题：`我要送快递可是你非要我做董事长`
  - 主流程 execution：`52`，success。
  - 单章 worker：`53`、`54`、`55`，均 success。
- 生成结果已同步到本地：`novel_projects/v02_3ch_smoke_20260501_1935`。
- 三章结果：
  - 第 1 章：`骑手进董事会`，5634 字符，QA `89`，`major_conflict=false`，`needs_rewrite=true`，`needs_manual_review=true`。
  - 第 2 章：`PPT里一切正常`，4656 字符，QA `91`，`major_conflict=false`，`needs_rewrite=false`，`needs_manual_review=false`。
  - 第 3 章：`董事长下仓`，4484 字符，QA `91`，`major_conflict=false`，`needs_rewrite=true`，`needs_manual_review=true`。
- 结论：
  - V0.2 资产层没有破坏原有 3 章生成链路。
  - 当前 N8N workflow 尚未接入 V0.2 的人物卡、金手指、风格圣经、因果规划、伏笔规划、去 AI 审计、风格审计节点，因此这些文件目前仍是占位或未参与生成。
  - QA 仍偏保守，高分无重大冲突章节仍可能被标为 rewrite/manual，需要下一步做 QA 归一化。

## 2026-05-01 小说阅读站部署

- 用户要求小说生成后能在服务器部署阅读网站，并返回外网 URL；每本书一个目录，方便以后切换阅读。
- 已新增静态站构建脚本：`novel_factory/scripts/build_reader_site.py`。
- 已在服务器生成静态站目录：`/opt/autoGenerate/novel_reader_site`。
- 已启动 Nginx 容器：
  - 容器名：`novel-reader`
  - 镜像：`nginx:alpine`
  - 端口：`18088 -> 80`
  - 数据卷：`/opt/autoGenerate/novel_reader_site:/usr/share/nginx/html:ro`
  - 重启策略：`unless-stopped`
- 已开放防火墙端口：`18088/tcp`。
- 外网验证通过：
  - 首页：`http://8.140.56.75:18088/`
  - 3 章测试书：`http://8.140.56.75:18088/books/v02_3ch_smoke_20260501_1935/index.html`
  - 20 章完整书：`http://8.140.56.75:18088/books/full20_retry_20260426_232722/index.html`
- 已新增部署文档：`docs/novel-reader-site-deployment.md`。
  - 2026-05-01 追加修复：`build_reader_site.py` 改为只清空输出目录内容、保留 `novel_reader_site` 目录本身，避免 Nginx bind mount 因目录被删除重建而出现 403/404。
  - 已生成 `assets/favicon.svg` 和根目录 `favicon.ico`，浏览器访问首页无资源 404。
  - 已在服务器验证连续重建后首页、favicon、20 章书籍页仍返回 200。
  - 当前 N8N workflow：
    - `小说工作流`：旧流程，inactive。
    - `Novel Seed - Bridge GPT MVP`：早期第 1 章硬编码 MVP，active，可做备份参考。
    - `Novel Book Loop MVP`：当前主流程，active。
    - `Novel Single Chapter Worker`：单章子流程，inactive 但可被主流程调用。
  - 标题到 20 章的主链路：标题 -> 故事种子 -> 小说圣经 -> 20 章大纲 -> 逐章 Worker -> 场景正文 -> 合章 -> QA -> 记忆回写 -> 合订本。
  - 当前限制和下一阶段建议：QA 归一化、自动精修、合订本节点化、Kimi 接入、记忆系统增强、人工审核节点。
