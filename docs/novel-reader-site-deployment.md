# 小说阅读站部署记录

日期：2026-05-01

## 访问地址

```text
http://8.140.56.75:18088/
```

当前已验证：

- 首页：`http://8.140.56.75:18088/`
- favicon：`http://8.140.56.75:18088/favicon.ico`
- 3 章测试书：`http://8.140.56.75:18088/books/v02_3ch_smoke_20260501_1935/index.html`
- 3 章测试书第 1 章：`http://8.140.56.75:18088/books/v02_3ch_smoke_20260501_1935/chapters/ch001.html`
- 20 章完整书：`http://8.140.56.75:18088/books/full20_retry_20260426_232722/index.html`

## 部署方式

阅读站是静态站点，不依赖数据库。

源数据：

```text
/opt/autoGenerate/novel_projects
```

站点生成目录：

```text
/opt/autoGenerate/novel_reader_site
```

构建脚本：

```text
novel_factory/scripts/build_reader_site.py
```

注意：构建脚本会清空输出目录内的文件，但保留 `novel_reader_site` 目录本身。不要在已挂载给 Nginx 的情况下删除并重建整个输出目录，否则容器会挂到旧目录句柄，导致首页变成 403/404。

服务器构建命令：

```bash
docker exec novel-bridge sh -lc 'cd /workspace && python novel_factory/scripts/build_reader_site.py --projects-dir /workspace/novel_projects --output-dir /workspace/novel_reader_site'
```

Nginx 容器：

```text
container: novel-reader
image: nginx:alpine
port: 18088 -> 80
volume: /opt/autoGenerate/novel_reader_site:/usr/share/nginx/html:ro
restart: unless-stopped
```

启动命令：

```bash
docker run -d --name novel-reader --restart unless-stopped \
  -p 18088:80 \
  -v /opt/autoGenerate/novel_reader_site:/usr/share/nginx/html:ro \
  nginx:alpine
```

防火墙：

```bash
firewall-cmd --permanent --add-port=18088/tcp
firewall-cmd --reload
```

## 页面结构

每本书一个目录：

```text
/books/<book_id>/index.html
/books/<book_id>/chapters/ch001.html
/books/<book_id>/chapters/ch002.html
```

首页自动扫描 `novel_projects` 下有 `chapters/ch*.md` 的项目。

## 后续接入 N8N

当前阅读站已经可用，但还不是 N8N 自动发布节点。

后续可以在主流程 `Finalize Book` 后增加一个 Execute Command / HTTP 运维节点，执行静态站构建命令。这样每次小说生成完成后，书架会自动刷新。

已验证连续执行构建命令后，`novel-reader` 容器仍可正常访问首页和 favicon。
