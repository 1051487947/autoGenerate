# AutoGenerate

AI 小说生成工程仓库。

当前第一阶段目标：围绕一个标题生成 20 章中篇小说的完整生产闭环，包括故事种子、小说圣经、20 章大纲、章节任务单、场景卡、正文生成、审稿、记忆回写和最终导出。

## 目录

- `docs/`：架构讨论、版本维护策略、20 章 MVP 蓝图和 Agent 记忆。
- `novel_factory/`：可复用的小说生成工厂，包括 Prompt、Schema、N8N 集成说明和本地 Bridge。
- `novel_projects/`：具体小说项目产物。

## 初始化新书

```powershell
C:\Python311\python.exe .\novel_factory\scripts\init_book_project.py --title "你的小说标题" --book-id your_book_id
```

## N8N Bridge

```powershell
C:\Python311\python.exe .\novel_factory\scripts\novel_bridge.py --host 127.0.0.1 --port 8765 --token your_token
```

N8N 集成说明见：

```text
novel_factory/n8n/integration-guide.md
```

