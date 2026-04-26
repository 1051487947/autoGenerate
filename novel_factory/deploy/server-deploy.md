# 服务器部署 Novel Bridge

适用服务器：N8N Docker Compose 同机部署。

当前已知 N8N 服务：

- 地址：`http://8.140.56.75:5678`
- Docker Compose 目录历史记录：`/opt/n8n-cn`
- N8N 容器名历史记录：`n8n-cn`

## 推荐目标

让 N8N workflow 访问：

```text
http://novel-bridge:8765
```

Novel Bridge 负责读写：

```text
/opt/autoGenerate/novel_factory
/opt/autoGenerate/novel_projects
```

## 1. 在服务器拉取仓库

```bash
cd /opt
git clone https://github.com/1051487947/autoGenerate.git
```

如果已经存在：

```bash
cd /opt/autoGenerate
git pull
```

## 2. 配置环境变量

在 `/opt/n8n-cn/.env` 或 Compose 使用的环境文件里追加：

```bash
NOVEL_BRIDGE_TOKEN=change_this_token
OPENAI_BASE_URL=https://api.openai.com
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
```

如果使用 OpenAI 兼容代理，修改 `OPENAI_BASE_URL`。

## 3. 合并 Compose 配置

参考：

```text
novel_factory/deploy/docker-compose.novel-bridge.example.yml
```

将其中的 `novel-bridge` 服务加入 `/opt/n8n-cn/docker-compose.yml`。

同时给现有 `n8n-cn` 服务增加：

```yaml
environment:
  NOVEL_BRIDGE_URL: http://novel-bridge:8765
  NOVEL_BRIDGE_TOKEN: ${NOVEL_BRIDGE_TOKEN}
  OPENAI_BASE_URL: ${OPENAI_BASE_URL:-https://api.openai.com}
  OPENAI_API_KEY: ${OPENAI_API_KEY}
  OPENAI_MODEL: ${OPENAI_MODEL:-gpt-4o}
depends_on:
  - novel-bridge
```

注意：如果 `n8n-cn` 已经有 `environment`，不要覆盖，追加这些字段即可。

## 4. 重启服务

```bash
cd /opt/n8n-cn
docker compose up -d
```

## 5. 验证 Bridge

从服务器宿主机验证：

```bash
docker exec n8n-cn node -e "fetch('http://novel-bridge:8765/health',{headers:{'X-Novel-Token':process.env.NOVEL_BRIDGE_TOKEN}}).then(r=>r.text()).then(console.log)"
```

期望返回：

```json
{
  "status": "ok"
}
```

## 6. 验证 N8N Workflow

N8N 中已新增 workflow：

```text
Novel Seed - Bridge GPT MVP
```

用途：

```text
标题 -> Bridge 初始化项目 -> 读取 Prompt/Schema -> GPT 生成 story_seed.json -> 写回项目目录
```

先手动执行该 workflow。成功后检查：

```text
/opt/autoGenerate/novel_projects/<book_id>/bible/story_seed.json
```

## 当前策略

旧 workflow `小说工作流` 暂时保留，不直接修改。

先用 `Novel Seed - Bridge GPT MVP` 跑通最小闭环，再把故事圣经、20 章大纲和章节循环逐步迁移过去。

