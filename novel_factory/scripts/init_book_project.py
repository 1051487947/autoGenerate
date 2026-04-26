import argparse
import json
import re
from datetime import datetime
from pathlib import Path


def safe_book_id(title: str) -> str:
    cleaned = re.sub(r"\s+", "_", title.strip())
    cleaned = re.sub(r'[\\/:*?"<>|]+', "", cleaned)
    cleaned = cleaned[:32].strip("_")
    suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{cleaned or 'book'}_{suffix}"


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def build_project(root: Path, title: str, book_id: str, chapter_count: int) -> Path:
    project_dir = root / "novel_projects" / book_id
    dirs = [
        "inputs",
        "bible",
        "outline",
        "chapter_tasks",
        "scenes",
        "chapters",
        "memory",
        "review",
        "export",
    ]
    for name in dirs:
        (project_dir / name).mkdir(parents=True, exist_ok=True)

    write_json(
        project_dir / "inputs" / "title.json",
        {
            "book_id": book_id,
            "title": title,
            "chapter_count": chapter_count,
            "target_words_per_chapter": 2500,
            "status": "initialized",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
    )

    write_json(project_dir / "bible" / "story_seed.json", {})
    write_text(project_dir / "bible" / "story_bible.md", f"# {title}\n\n> 待由 `02_story_bible` 生成。\n")
    write_json(project_dir / "bible" / "characters.json", {"characters": []})
    write_json(project_dir / "bible" / "foreshadowing.json", {"items": []})
    write_json(project_dir / "outline" / "chapters_20.json", {"book_title": title, "chapter_count": chapter_count, "chapters": []})
    write_json(project_dir / "memory" / "chapter_summaries.json", {"chapters": []})
    write_json(project_dir / "memory" / "state_memory.json", {"characters": [], "locations": [], "organizations": [], "must_remember": []})
    write_text(project_dir / "memory" / "continuity_notes.md", "# 连续性记录\n\n")
    write_json(project_dir / "review" / "qa_report.json", {"chapters": []})
    write_text(project_dir / "export" / "full_book.md", f"# {title}\n\n")

    readme = f"""# {title}

book_id: `{book_id}`

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
"""
    write_text(project_dir / "README.md", readme)
    return project_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a 20 chapter AI novel project.")
    parser.add_argument("--title", required=True, help="Novel title.")
    parser.add_argument("--book-id", default=None, help="Optional stable book id.")
    parser.add_argument("--chapter-count", type=int, default=20, help="Chapter count, default 20.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    book_id = args.book_id or safe_book_id(args.title)
    project_dir = build_project(repo_root, args.title, book_id, args.chapter_count)
    print(project_dir)


if __name__ == "__main__":
    main()
