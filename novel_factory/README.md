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

## 通过 HTTP Bridge 接入 N8N

如果希望 N8N 通过 HTTP Request 节点读写小说工程，可以启动轻量 Bridge：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\novel_bridge.py --host 127.0.0.1 --port 8765 --token your_token
```

详见：

```text
novel_factory/n8n/integration-guide.md
```
