# N8N 集成小说工厂指南

## 你真正要接起来的是什么

`novel_factory` 是小说生产系统的文件资产层，N8N 是调度层。

N8N 不需要把所有 Prompt、Schema、小说状态都写死在节点里，而是通过以下方式使用工程：

1. 创建一本书的项目目录。
2. 读取 Prompt 模板。
3. 调用 GPT / Kimi。
4. 校验模型输出 JSON。
5. 把每一步产物写回 `novel_projects/<book_id>/`。
6. 根据 QA 分数决定通过、重写或人工确认。

## 先确认 N8N 跑在哪里

### 方案 A：N8N 和小说工程在同一台机器

这是最简单的方式。

- Windows 本机 N8N：可以直接访问 `G:\Documents\xiaoshuo`。
- 服务器 N8N：需要把 `novel_factory` 和 `novel_projects` 部署到服务器，例如 `/opt/novel-factory-workspace`。

N8N 可以用 Execute Command 节点直接运行：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\init_book_project.py --title "标题" --book-id "book_id"
```

如果在 Linux 服务器，则使用服务器上的 Python 路径。

### 方案 B：N8N 通过 HTTP Bridge 调用小说工程

适合让 N8N 不直接碰文件系统，只通过 HTTP Request 节点读写文件。

启动 Bridge：

```powershell
C:\Python311\python.exe .\novel_factory\scripts\novel_bridge.py --host 127.0.0.1 --port 8765 --token your_token
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8765/health
```

N8N HTTP Request 节点统一加 Header：

```text
X-Novel-Token: your_token
```

### 方案 C：远程 N8N + 本地 Windows 工程

如果你的 N8N 在服务器 `8.140.56.75`，它不能直接读取本机 `G:\Documents\xiaoshuo`。

可选做法：

1. 把小说工程部署到 N8N 服务器上，作为正式执行环境。
2. 本地工程通过 Git / KodBox / rsync 同步到服务器。
3. 在本机启动 Bridge，并通过内网穿透、VPN、Tailscale、frp 等方式让服务器访问。

第一轮建议用第 1 种：把工程放到 N8N 同机，减少网络变量。

## Bridge API

## Bridge 和 LLM 的职责边界

这些 HTTP 接口本身不调用 GPT 或 Kimi，也不会自动生成小说内容。

它们只负责：

- 初始化书籍目录。
- 读取 Prompt 模板。
- 读取 JSON Schema。
- 保存 N8N 上游节点传来的内容。
- 读取已经保存过的内容。

真正生成内容的是 N8N 中间的 LLM 节点，例如 OpenAI 节点、HTTP Request 调 Kimi API 节点。

典型链路是：

```text
GET /api/prompts/01_seed_from_title.md
  -> N8N 把 Prompt + 标题发给 GPT
  -> GPT 返回 story_seed JSON
  -> POST /api/books/<book_id>/write 保存到 bible/story_seed.json
```

也就是说，`POST /write` 保存的内容通常来自 LLM 输出，但 Bridge 不关心内容是谁生成的。它只负责校验 JSON 是否能解析，并写入对应文件。

### 创建书籍项目

```http
POST /api/books/init
```

Body：

```json
{
  "title": "我要送快递可是你非要我做董事长",
  "book_id": "kuaidi_dongshizhang",
  "chapter_count": 20
}
```

返回：

```json
{
  "book_id": "kuaidi_dongshizhang",
  "project_dir": "G:\\Documents\\xiaoshuo\\novel_projects\\kuaidi_dongshizhang"
}
```

### 读取 Prompt

```http
GET /api/prompts/01_seed_from_title.md
```

返回：

```json
{
  "name": "01_seed_from_title.md",
  "content": "..."
}
```

### 读取 Schema

```http
GET /api/schemas/story_seed.schema.json
```

### 写入产物

```http
POST /api/books/kuaidi_dongshizhang/write
```

Body：

```json
{
  "path": "bible/story_seed.json",
  "content": {
    "title": "我要送快递可是你非要我做董事长"
  }
}
```

### 读取产物

```http
GET /api/books/kuaidi_dongshizhang/read?path=outline/chapters_20.json
```

### 查看项目文件

```http
GET /api/books/kuaidi_dongshizhang/manifest
```

## N8N 主链路怎么接

### 1. Webhook / Manual Trigger

输入：

```json
{
  "title": "我要送快递可是你非要我做董事长",
  "book_id": "kuaidi_dongshizhang",
  "chapter_count": 20
}
```

### 2. Init Book

HTTP Request：

```text
POST http://127.0.0.1:8765/api/books/init
```

### 3. Load Seed Prompt

HTTP Request：

```text
GET http://127.0.0.1:8765/api/prompts/01_seed_from_title.md
```

### 4. GPT Seed From Title

把 Prompt 和标题传给 GPT，要求输出 `story_seed.schema.json` 格式 JSON。

### 5. Save Story Seed

HTTP Request：

```text
POST http://127.0.0.1:8765/api/books/{{$json.book_id}}/write
```

写入：

```json
{
  "path": "bible/story_seed.json",
  "content": "{{$json.model_output}}"
}
```

### 6. Story Bible / Outline / Chapter Loop

后续重复同样模式：

```text
读 Prompt -> 读上游产物 -> 调模型 -> 校验 JSON/文本 -> 写回项目目录
```

## 单章循环的数据落盘

第 N 章建议固定写这些文件：

```text
chapter_tasks/chNNN.task.json
scenes/chNNN.scenes.json
scenes/chNNN_scene01.md
scenes/chNNN_scene02.md
chapters/chNNN.md
review/chNNN.qa.json
memory/chNNN.memory.json
```

N8N 每次只处理一个章节对象，处理完就写回记忆，再进入下一章。

## 最关键的设计原则

- N8N 节点只负责调度，不长期保存小说状态。
- 所有中间产物都写回 `novel_projects/<book_id>/`。
- GPT 负责逻辑、结构、审稿和记忆回写。
- Kimi 负责场景正文和章节润色。
- 每次执行都带 `book_id` 和 `run_id`，避免多本书串数据。
- 远程 N8N 不能直接读本机 G 盘，必须同机部署、同步文件，或通过 Bridge 暴露接口。
