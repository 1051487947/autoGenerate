# 我要送快递可是你非要我做董事长

book_id: `full20_retry_20260426_232722`

## 生成顺序

1. 用 `01_seed_from_title` 生成 `bible/story_seed.json`。
2. 用 `02_story_bible` 生成 `bible/story_bible.md`。
3. 用 `03_outline_20` 生成 `outline/chapters_20.json`。
4. 按章节循环生成：
   - `chapter_tasks/ch001.task.json`
   - `scenes/ch001.scenes.json`
   - `scenes/ch001_scene01.md`
   - `chapters/ch001.md`
   - `review/ch001.qa.json`
   - `memory/ch001.memory.json`
5. 最后合并到 `export/full_book.md`。

## 当前状态

项目骨架已初始化，等待 AI 工作流填充内容。
