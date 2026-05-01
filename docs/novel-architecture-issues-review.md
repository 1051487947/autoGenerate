# 小说生成系统架构问题复盘

日期：2026-04-27

本文记录此前从单章 MVP 到 20 章完整生成过程中暴露出的架构性问题，以及当前修复状态。

## 总体结论

之前遇到的问题不是单纯的“模型写得不好”，而是典型的长流程自动化系统问题：

- 流程从单章 MVP 演进到 20 章循环时，暴露了硬编码、状态串扰、节点数据传递、重试策略不足等问题。
- 20 章生成已经验证成功，说明主链路架构成立。
- 当前主要矛盾已经从“能不能生成 20 章”转为“如何自动精修、稳定定稿、强化记忆状态机”。

## 已暴露并修复的问题

### 1. 旧流程硬编码第 1 章

早期 `Novel Seed - Bridge GPT MVP` 主要路径固定为：

- `chapter_tasks/ch001.task.json`
- `scenes/ch001.scenes.json`
- `chapters/ch001.md`
- `review/ch001.qa.json`
- `memory/ch001.memory.json`

这导致流程看起来始终围绕第 1 章生成，没有真正遍历 `chapters_20.json`。

当前状态：

- 已拆成主流程 `Novel Book Loop MVP` 和单章子流程 `Novel Single Chapter Worker`。
- 已验证 2 章、3 章、20 章连续循环。
- 20 章成功样本：`full20_retry_20260426_232722`。

### 2. n8n Code 节点字符串转义问题

`Build Scene Draft Requests` 中曾使用：

```javascript
join('\n')
```

n8n 反序列化后会把转义换行变成真实换行，导致 JS 报错：

```text
Unterminated string constant
```

当前状态：

- 已改为 `join(String.fromCharCode(10))`。
- 已对主流程和 worker 的 Code 节点做语法预检。

### 3. 场景正文并发触发模型网关 429

场景正文请求最初会并发调用，触发自定义模型网关：

```text
429 Concurrency limit exceeded
```

当前状态：

- 已将 `OpenAI Scene Writer` 改为串行批处理。
- 当前配置为 `batchSize=1`，`batchInterval=90000`。

### 4. 长文本生成遇到 502 中断

第一次完整 20 章长跑在 `OpenAI Scene Writer` 失败：

```text
502 Bad gateway
Upstream stream ended without a terminal response event
```

判断为模型网关或上游流式响应中断，不是章节循环逻辑错误。

当前状态：

- 已给模型 HTTP 节点增加 n8n 原生重试。
- `retryOnFail=true`
- `maxTries=3`
- 普通模型节点等待 `60000ms`
- Scene Writer 等待 `120000ms`
- 加重试后第二次完整 20 章生成成功。

### 5. n8n `.item` 多 item 链接错误

`Done` 汇总节点曾在多 item 节点之后使用 `.item`，触发 n8n item linking 错误。

当前状态：

- 已改为 `.all()[0].json`。
- 汇总节点运行通过。

### 6. 直接用 KodBox 做过程存储不适合

早期设计里 KodBox 承担了章节级和全书级归档。但它更适合阅读、预览、成品归档，不适合作为过程版本库。

当前状态：

- 已明确 GitHub + `novel_projects` 作为过程和版本管理主链路。
- KodBox 后续只建议放最终成品，如 `export/full_book.md` 或 `chapters/*.final.md`。

### 7. 远程 N8N 不能直接读取本地 G 盘

N8N 部署在服务器上，不能直接访问本地 `G:\Documents\autoGenerate`。

当前状态：

- 已把 repo 部署到服务器 `/opt/autoGenerate`。
- 已引入 `novel-bridge`，供 N8N 通过 HTTP 读取 Prompt、Schema 和项目文件。

### 8. 合订本 UTF-8 编码问题

早期通过 shell 方式合并中文 Markdown 时出现过乱码风险。

当前状态：

- 已使用 UTF-8 安全的 Python 合并方式重新生成 `export/full_book.md`。

## 仍然存在的架构债

### 1. QA 规则过于保守

20 章 QA 结果里，章节普遍 `major_conflict=false`，总分约 `89-92`，但仍频繁标记：

- `needs_rewrite=true`
- `needs_manual_review=true`

这说明 QA 的语义不够细：高分小修不应该等同于整章失败。

建议：

- 增加 QA 归一化节点。
- 当 `major_conflict=false` 且 `total_score>=85` 时，将 `needs_rewrite` 降级为 `needs_polish`。

### 2. 自动精修闭环还没完成

当前已能生成原稿、QA、memory，但还没有自动产出：

- `chapters/chXXX.revised.md`
- `chapters/chXXX.final.md`

建议：

- 增加 `Chapter Revision` 子流程。
- 输入原稿和 QA 修订建议。
- 输出精修版，并保留原稿做版本对比。

### 3. 记忆系统还不是强状态机

当前每章会生成 `memory/chXXX.memory.json`，但它更多是“章节后摘要”，还没有真正形成强约束的角色/伏笔/地点状态机。

建议后续拆成：

- `characters_state.json`
- `foreshadowing_state.json`
- `locations_state.json`
- `chapter_summaries.json`

生成下一章前必须先读取这些状态，并在 QA 阶段校验是否违反。

### 4. RAG/向量检索还没接入

当前上下文主要靠章节任务单、场景卡、memory 文件传递。对于更长篇幅，后续会遇到历史细节召回不足的问题。

建议：

- 第一阶段先做关键词检索。
- 第二阶段再接 Chroma、Qdrant 或其他向量库。

### 5. Kimi 写作模型还没接入

当前测试先全部使用 GPT 兼容模型跑通。目标架构里应让：

- GPT 负责故事种子、小说圣经、大纲、QA、记忆。
- Kimi 负责场景正文和章节润色。

建议：

- 优先只替换 `Scene Writer` 和 `Chapter Editor` 两类节点。
- 其他逻辑节点暂时保持 GPT。

### 6. 合订本生成还未完全内置到 N8N 主流程

当前 20 章合订本已经生成，但实际合并动作更像后处理，不是正式主流程节点。

建议：

- 在 `Novel Book Loop MVP` 末尾增加 `Export Full Book` 节点。
- 或新增独立 `Novel Export Worker` 子流程。

### 7. 人工审核节点还比较弱

当前系统可以全自动跑通，但对重大剧情节点还没有人工确认机制。

建议：

- 对低分章节、重大设定变更、角色死亡、主线反转、感情线推进增加人工确认。
- n8n 可以用 Wait/Webhook/通知节点实现暂停和继续。

## 下一步优先级

建议按下面顺序推进：

1. QA 归一化：先解决高分章节被误判重写的问题。
2. 自动精修：生成 `chXXX.revised.md`，保留原稿。
3. 合订本节点化：把 `export/full_book.md` 纳入 N8N 正式流程。
4. 强化状态机：角色、地点、伏笔拆成独立结构化状态。
5. 接入 Kimi：先替换正文写作和润色节点。
6. 增加人工审核：只在关键风险点暂停，不影响常规章节自动生成。

