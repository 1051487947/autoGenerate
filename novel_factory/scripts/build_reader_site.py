import argparse
import html
import json
import re
import shutil
import struct
from datetime import datetime
from pathlib import Path


def read_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def reset_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for child in output_dir.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def safe_slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\u4e00-\u9fff]+", "-", text.strip())
    cleaned = cleaned.strip("-_")
    return cleaned or "book"


def markdown_to_html(markdown: str) -> str:
    blocks = []
    paragraph = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        text = "<br>".join(html.escape(line) for line in paragraph)
        blocks.append(f"<p>{text}</p>")
        paragraph.clear()

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            flush_paragraph()
            continue
        if line.startswith("# "):
            flush_paragraph()
            blocks.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
            continue
        if line.startswith("## "):
            flush_paragraph()
            blocks.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
            continue
        if line.startswith("### "):
            flush_paragraph()
            blocks.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
            continue
        paragraph.append(line)
    flush_paragraph()
    return "\n".join(blocks)


def chapter_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip() or fallback
    return fallback


def discover_books(projects_dir: Path):
    books = []
    for project in sorted(projects_dir.iterdir() if projects_dir.exists() else []):
        if not project.is_dir():
            continue
        chapters_dir = project / "chapters"
        chapters = sorted(chapters_dir.glob("ch*.md"))
        if not chapters:
            continue
        title_data = read_json(project / "inputs" / "title.json", {})
        seed_data = read_json(project / "bible" / "story_seed.json", {})
        title = title_data.get("title") or seed_data.get("title") or project.name
        if "?" in title and title.count("?") >= max(3, len(title) // 2):
            title = project.name
        updated_at = max(path.stat().st_mtime for path in chapters)
        books.append(
            {
                "id": project.name,
                "slug": safe_slug(project.name),
                "title": title,
                "chapter_count": len(chapters),
                "project": project,
                "chapters": chapters,
                "updated_at": updated_at,
                "genre": seed_data.get("genre", ""),
                "core_hook": seed_data.get("core_hook", ""),
            }
        )
    books.sort(key=lambda item: item["updated_at"], reverse=True)
    return books


def site_css() -> str:
    return """
:root {
  --paper: #f7f0e4;
  --ink: #241b14;
  --muted: #7d6b58;
  --line: rgba(82, 61, 43, .18);
  --brand: #8f4d2f;
  --brand-dark: #4d2b1d;
  --panel: rgba(255, 252, 246, .78);
  --shadow: 0 18px 50px rgba(42, 27, 17, .13);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  background:
    linear-gradient(90deg, rgba(91, 55, 31, .05) 1px, transparent 1px) 0 0 / 42px 42px,
    radial-gradient(circle at 18% 0%, rgba(145, 80, 42, .12), transparent 34%),
    var(--paper);
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", SimSun, serif;
}
a { color: inherit; text-decoration: none; }
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(18px);
  background: rgba(247, 240, 228, .86);
  border-bottom: 1px solid var(--line);
}
.topbar-inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 16px 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}
.brand {
  font-weight: 800;
  letter-spacing: 0;
  color: var(--brand-dark);
}
.navlink {
  font-size: 14px;
  color: var(--muted);
}
.hero, .layout {
  max-width: 1180px;
  margin: 0 auto;
  padding: 36px 22px;
}
.hero h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.25;
}
.hero p {
  max-width: 760px;
  color: var(--muted);
  line-height: 1.9;
}
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}
.book-card {
  min-height: 190px;
  padding: 22px;
  border: 1px solid var(--line);
  background: var(--panel);
  box-shadow: var(--shadow);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.book-card h2 {
  margin: 0;
  font-size: 22px;
  line-height: 1.35;
}
.meta, .summary, .chapter-meta {
  color: var(--muted);
  font-size: 14px;
  line-height: 1.75;
}
.summary {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.button-row { margin-top: auto; display: flex; gap: 10px; align-items: center; }
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 6px;
  background: var(--brand-dark);
  color: #fff8ef;
  font-size: 14px;
}
.button.secondary {
  color: var(--brand-dark);
  background: rgba(77, 43, 29, .08);
}
.reader-shell {
  max-width: 1220px;
  margin: 0 auto;
  padding: 24px 22px 72px;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 28px;
}
.sidebar {
  position: sticky;
  top: 78px;
  align-self: start;
  max-height: calc(100vh - 96px);
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255, 252, 246, .78);
}
.sidebar-head { padding: 18px; border-bottom: 1px solid var(--line); }
.sidebar-head h2 { margin: 0 0 8px; font-size: 19px; line-height: 1.35; }
.chapter-list { display: grid; padding: 8px; }
.chapter-list a {
  padding: 10px 12px;
  border-radius: 6px;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.45;
}
.chapter-list a:hover, .chapter-list a.active {
  background: rgba(143, 77, 47, .12);
  color: var(--brand-dark);
}
.reader {
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255, 252, 246, .84);
  box-shadow: var(--shadow);
  padding: 46px min(7vw, 76px);
}
.reader h1 {
  margin: 0 0 20px;
  font-size: 30px;
  line-height: 1.35;
}
.reader h2, .reader h3 { margin-top: 34px; }
.reader p {
  margin: 1.05em 0;
  font-size: 20px;
  line-height: 2.05;
  text-align: justify;
}
.chapter-nav {
  margin-top: 42px;
  padding-top: 22px;
  border-top: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  gap: 14px;
}
@media (max-width: 860px) {
  .reader-shell { grid-template-columns: 1fr; }
  .sidebar { position: relative; top: auto; max-height: none; }
  .reader { padding: 28px 20px; }
  .reader p { font-size: 18px; line-height: 1.95; }
  .hero h1 { font-size: 28px; }
}
"""


def favicon_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#4d2b1d"/>
  <path d="M18 16h20c5 0 8 3 8 8v24H24c-4 0-6-2-6-6V16Z" fill="#f7f0e4"/>
  <path d="M24 24h16M24 31h14M24 38h12" stroke="#8f4d2f" stroke-width="3" stroke-linecap="round"/>
</svg>
"""


def favicon_ico() -> bytes:
    size = 32
    pixels = []
    for y in range(size):
        for x in range(size):
            if 8 <= x <= 23 and 7 <= y <= 25:
                color = (0xF7, 0xF0, 0xE4, 0xFF)
            elif 11 <= x <= 22 and y in (13, 17, 21):
                color = (0x8F, 0x4D, 0x2F, 0xFF)
            else:
                color = (0x4D, 0x2B, 0x1D, 0xFF)
            r, g, b, a = color
            pixels.append(bytes((b, g, r, a)))

    rows = []
    for row in range(size - 1, -1, -1):
        start = row * size
        rows.append(b"".join(pixels[start:start + size]))

    and_mask = b"\x00" * (size * 4)
    dib = struct.pack(
        "<IIIHHIIIIII",
        40,
        size,
        size * 2,
        1,
        32,
        0,
        size * size * 4,
        0,
        0,
        0,
        0,
    ) + b"".join(rows) + and_mask

    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(dib), 22)
    return header + entry + dib


def page(title: str, body: str, root_prefix: str = "") -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="icon" href="{root_prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{root_prefix}assets/site.css">
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="{root_prefix}index.html">AI 小说书架</a>
      <a class="navlink" href="{root_prefix}index.html">全部作品</a>
    </div>
  </header>
  {body}
</body>
</html>
"""


def build_book(book, output_dir: Path) -> None:
    book_dir = output_dir / "books" / book["slug"]
    chapters_dir = book_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    chapter_infos = []
    for index, chapter_path in enumerate(book["chapters"], start=1):
        markdown = read_text(chapter_path)
        title = chapter_title(markdown, f"第{index}章")
        filename = f"ch{index:03d}.html"
        chapter_infos.append({"title": title, "filename": filename})

    for index, chapter_path in enumerate(book["chapters"], start=1):
        markdown = read_text(chapter_path)
        title = chapter_infos[index - 1]["title"]
        links = "\n".join(
            f'<a class="{"active" if i == index else ""}" href="chapters/{info["filename"]}">{html.escape(info["title"])}</a>'
            for i, info in enumerate(chapter_infos, start=1)
        )
        prev_link = ""
        next_link = ""
        if index > 1:
            prev_info = chapter_infos[index - 2]
            prev_link = f'<a class="button secondary" href="{prev_info["filename"]}">上一章</a>'
        if index < len(chapter_infos):
            next_info = chapter_infos[index]
            next_link = f'<a class="button" href="{next_info["filename"]}">下一章</a>'
        body = f"""
<main class="reader-shell">
  <aside class="sidebar">
    <div class="sidebar-head">
      <h2>{html.escape(book["title"])}</h2>
      <div class="chapter-meta">{book["chapter_count"]} 章 · {html.escape(book["id"])}</div>
    </div>
    <nav class="chapter-list">{links}</nav>
  </aside>
  <article class="reader">
    {markdown_to_html(markdown)}
    <nav class="chapter-nav">
      <span>{prev_link}</span>
      <a class="button secondary" href="../index.html">目录</a>
      <span>{next_link}</span>
    </nav>
  </article>
</main>
"""
        (chapters_dir / chapter_infos[index - 1]["filename"]).write_text(page(title, body, "../../"), encoding="utf-8")

    first = chapter_infos[0]["filename"] if chapter_infos else ""
    chapter_links = "\n".join(
        f'<a href="chapters/{info["filename"]}">{html.escape(info["title"])}</a>'
        for info in chapter_infos
    )
    body = f"""
<main class="layout">
  <section class="hero">
    <h1>{html.escape(book["title"])}</h1>
    <p>{html.escape(book["core_hook"] or "已生成章节，可从目录开始阅读。")}</p>
    <p class="meta">{book["chapter_count"]} 章 · {html.escape(book["genre"] or "未标注类型")} · {html.escape(book["id"])}</p>
    <p><a class="button" href="chapters/{first}">开始阅读</a></p>
  </section>
  <section class="sidebar" style="position:relative;top:auto;max-height:none;">
    <div class="sidebar-head"><h2>目录</h2></div>
    <nav class="chapter-list">{chapter_links}</nav>
  </section>
</main>
"""
    (book_dir / "index.html").write_text(page(book["title"], body, "../../"), encoding="utf-8")


def build_site(projects_dir: Path, output_dir: Path) -> None:
    reset_output_dir(output_dir)
    (output_dir / "assets").mkdir(parents=True, exist_ok=True)
    (output_dir / "books").mkdir(parents=True, exist_ok=True)
    (output_dir / "assets" / "site.css").write_text(site_css(), encoding="utf-8")
    (output_dir / "assets" / "favicon.svg").write_text(favicon_svg(), encoding="utf-8")
    (output_dir / "favicon.ico").write_bytes(favicon_ico())

    books = discover_books(projects_dir)
    for book in books:
        build_book(book, output_dir)

    cards = []
    for book in books:
        updated = datetime.fromtimestamp(book["updated_at"]).strftime("%Y-%m-%d %H:%M")
        cards.append(
            f"""
<article class="book-card">
  <h2>{html.escape(book["title"])}</h2>
  <div class="meta">{book["chapter_count"]} 章 · {html.escape(book["genre"] or "未标注类型")} · {updated}</div>
  <div class="summary">{html.escape(book["core_hook"] or book["id"])}</div>
  <div class="button-row">
    <a class="button" href="books/{book["slug"]}/index.html">进入阅读</a>
    <a class="button secondary" href="books/{book["slug"]}/chapters/ch001.html">第一章</a>
  </div>
</article>
"""
        )
    body = f"""
<main>
  <section class="hero">
    <h1>小说书架</h1>
    <p>这里收纳服务器上已经生成过的小说项目。每本书都有独立目录，后续生成新书后重新构建站点即可加入书架。</p>
    <p class="meta">共 {len(books)} 本 · 最后生成 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
  </section>
  <section class="layout" style="padding-top:0;">
    <div class="book-grid">
      {''.join(cards) if cards else '<p class="meta">还没有可阅读章节。</p>'}
    </div>
  </section>
</main>
"""
    (output_dir / "index.html").write_text(page("小说书架", body), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a static reader site for generated novels.")
    parser.add_argument("--projects-dir", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    projects_dir = Path(args.projects_dir) if args.projects_dir else repo_root / "novel_projects"
    output_dir = Path(args.output_dir) if args.output_dir else repo_root / "novel_reader_site"
    build_site(projects_dir.resolve(), output_dir.resolve())
    print(output_dir.resolve())


if __name__ == "__main__":
    main()
