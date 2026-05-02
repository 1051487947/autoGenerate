# AI 小说工厂

这个目录是“从标题生成 20 章小说”的工程骨架。它不是某一本书的正文目录，而是长期复用的生产系统资产。

## 第一轮目标

输入一个标题，自动生成并归档以下内容：

1. 故事种子
2. 小说圣经
3. 20 章大纲
4. 每章任务单
5. 每章 3-5 个场景卡
6. 场景正文
7. 合并润色后的章节正文
8. GPT 审稿报告
9. 章节摘要、角色状态、伏笔状态回写
10. 20 章合订版

## V0.2 扩展

在第一轮骨架之外，当前工厂还预留了以下长期创作资产：

1. 人物卡
2. 金手指规则
3. 文风圣经
4. 作者声音指纹
5. 反 AI 措辞表
6. 伏笔账本
7. 人物弧光账本
8. 因果账本
9. 压力账本
10. 信息差账本
11. 反派行动账本
12. 章末钩子账本

## V0.3 编辑反馈闭环

V0.3 专门解决试读评价里暴露出来的中长篇风险：

1. 高管和对手不能只是工具人，必须有个人利益、反制动作和失败风险。
2. “快递员当董事长”这类强设定必须有制度可信度补丁。
3. 主角不能连续无代价正确，胜利要带来物质、关系、名誉或时间成本。
4. “签收”等核心隐喻必须被账本追踪，避免开头有灵气、后面变普通爽文。
5. 外部 AI 或人工编辑评价要进入 `Editorial Diagnosis`，转成可执行的工作流改造项。

## V0.5 长篇模式

如果目标是 30 万字，不建议把 20 章直接当完整书生成。当前 20 章应升级为第一卷或第一阶段，然后按“全书架构 -> 分卷弧线 -> 滚动20章批次 -> 单章生成”的方式推进。

新增资产：

1. 30万字长篇总架构
2. 分卷剧情弧
3. 滚动20章批次规划
4. 剧情线、人物线、关系线连续性审计
5. 全局主线账本、剧情线程账本、关系账本

推荐规模：

- 30 万字约 100 到 120 章。
- 每章 2500 到 3000 字。
- 5 到 6 卷，每卷约 18 到 25 章。
- 当前 20 章更适合定位为第一卷“被推上台，先活下来”。

## 推荐目录分工

- `prompts/`：给 GPT、Kimi 使用的提示词模板。
- `schemas/`：模型必须返回的数据结构约束。
- `n8n/`：N8N 节点编排说明和数据契约。
- `scripts/`：本地辅助脚本。
- `../novel_projects/`：每本书的实际产物目录，由脚本或工作流生成。

## 初始化一本新书

使用指定 Python 路径：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\init_book_project.py --title "我要送快递可是你非要我做董事长"
```

可选指定 `book_id`：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\init_book_project.py --title "我要送快递可是你非要我做董事长" --book-id kuaidi_dongshizhang
```

初始化 30 万字长篇项目时可以指定 120 章：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\init_book_project.py --title "我要送快递可是你非要我做董事长" --book-id kuaidi_300k --chapter-count 120
```

生成后目录类似：

```text
novel_projects/
└── kuaidi_dongshizhang/
    ├── inputs/
    ├── bible/
    ├── outline/
    ├── chapters/
    ├── chapter_tasks/
    ├── scenes/
    ├── memory/
    ├── review/
    └── export/
```

## N8N 落地原则

N8N 不直接承载长 Prompt 和复杂设定，尽量只做这些事：

- 读取 `prompts/` 模板。
- 调用 GPT / Kimi。
- 校验 JSON 结构。
- 保存中间产物。
- 控制循环、重试、人工确认。
- 归档结果。

每个模型节点的输出都要写入文件或数据库，避免失败后丢失上下文。

## 资产完整性审计

生成或补齐一本书的核心资产后，运行：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\audit_book_assets.py --book-id v02_3ch_smoke_20260501_1935 --write
```

审计报告会写入：

```text
novel_projects/<book_id>/review/asset_completeness_report.json
```

该脚本会检查人物卡、制度可信度、长篇架构、分卷规划、文风圣经、读者承诺和长篇账本是否可用。

## 通过 HTTP Bridge 接入 N8N

如果希望 N8N 通过 HTTP Request 节点读写小说工程，可以启动轻量 Bridge：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\novel_bridge.py --host 127.0.0.1 --port 8765 --token your_token
```

详见：

```text
novel_factory/n8n/integration-guide.md
```
