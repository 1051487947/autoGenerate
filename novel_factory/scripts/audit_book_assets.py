import argparse
import json
from datetime import datetime
from pathlib import Path


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def add_issue(issues, severity: str, path: str, message: str, recommendation: str) -> None:
    issues.append(
        {
            "severity": severity,
            "path": path,
            "message": message,
            "recommendation": recommendation,
        }
    )


def audit_project(project_dir: Path) -> dict:
    issues = []
    checks = []

    def record(name: str, passed: bool) -> None:
        checks.append({"name": name, "passed": passed})

    title = read_json(project_dir / "inputs" / "title.json", {})
    book_id = title.get("book_id") or project_dir.name
    book_title = title.get("title") or ""

    characters = read_json(project_dir / "bible" / "characters.json", {})
    character_count = len(characters.get("characters", [])) if isinstance(characters, dict) else 0
    record("characters_non_empty", character_count > 0)
    if character_count <= 0:
        add_issue(
            issues,
            "P0",
            "bible/characters.json",
            "人物卡为空，后续章节无法稳定保持主角、女主、反派和配角行为边界。",
            "先生成至少 5 个核心人物卡：男主、女主、主要对手、财务/规则角色、一线锚点。",
        )

    institutional = read_json(project_dir / "bible" / "institutional_plausibility.json", {})
    institutional_ok = bool(institutional) and not is_blank(institutional.get("legal_or_governance_mechanism"))
    record("institutional_plausibility_ready", institutional_ok)
    if not institutional_ok:
        add_issue(
            issues,
            "P0",
            "bible/institutional_plausibility.json",
            "制度可信度补丁缺失，核心强设定容易显得悬空。",
            "补齐核心强设定、授权链、知情人、利用制度缝隙的人和分章露出计划。",
        )

    long_arch = read_json(project_dir / "bible" / "long_novel_architecture.json", {})
    long_arch_ok = bool(long_arch) and len(long_arch.get("volumes", [])) > 0
    record("long_novel_architecture_ready", long_arch_ok)
    if not long_arch_ok:
        add_issue(
            issues,
            "P0",
            "bible/long_novel_architecture.json",
            "30 万字长篇总架构缺失，20 章无法稳定扩展为整本书。",
            "先确定 5-6 卷结构、主角全书弧线、反派升级、隐喻策略和秘密揭示节奏。",
        )

    volumes = read_json(project_dir / "outline" / "volumes.json", {})
    volumes_ok = bool(volumes) and len(volumes.get("volumes", [])) > 0
    record("volumes_ready", volumes_ok)
    if not volumes_ok:
        add_issue(
            issues,
            "P0",
            "outline/volumes.json",
            "分卷规划缺失，无法判断当前 20 章在全书中的位置。",
            "补齐每卷的开局状态、核心危机、阶段错误、关系推进、高潮、胜利和代价。",
        )

    style_bible = read_text(project_dir / "bible" / "style_bible.md")
    style_ready = bool(style_bible.strip()) and "待由" not in style_bible
    record("style_bible_ready", style_ready)
    if not style_ready:
        add_issue(
            issues,
            "P1",
            "bible/style_bible.md",
            "文风圣经仍是占位或过短，Kimi/GPT 正文容易漂移。",
            "基于前三章提取句式、比喻系统、对话差异、段落节奏和禁用腔调。",
        )

    reader_promise = read_json(project_dir / "bible" / "reader_promise.json", {})
    reader_promise_ready = bool(reader_promise.get("promises")) if isinstance(reader_promise, dict) else False
    record("reader_promise_ready", reader_promise_ready)
    if not reader_promise_ready:
        add_issue(
            issues,
            "P1",
            "bible/reader_promise.json",
            "读者承诺未结构化，章节容易只推进事件、不兑现爽点和情绪价值。",
            "补齐每章必须兑现的承诺、不能破坏的底线和本书核心阅读期待。",
        )

    ledger_paths = [
        "memory/global_arc_ledger.json",
        "memory/plot_thread_ledger.json",
        "memory/relationship_ledger.json",
        "memory/character_arc_ledger.json",
        "memory/protagonist_cost_ledger.json",
        "memory/motif_ledger.json",
    ]
    existing_ledgers = [path for path in ledger_paths if (project_dir / path).exists()]
    record("longform_ledgers_exist", len(existing_ledgers) == len(ledger_paths))
    missing_ledgers = sorted(set(ledger_paths) - set(existing_ledgers))
    for rel in missing_ledgers:
        add_issue(
            issues,
            "P1",
            rel,
            "长篇账本文件缺失。",
            "补齐初始化文件，后续 N8N 每章或每批次回写。",
        )

    chapters = sorted((project_dir / "chapters").glob("ch*.md"))
    record("has_generated_chapters", len(chapters) > 0)

    critical_count = sum(1 for issue in issues if issue["severity"] == "P0")
    warning_count = sum(1 for issue in issues if issue["severity"] == "P1")
    status = "pass" if critical_count == 0 else "blocked"
    if critical_count == 0 and warning_count > 0:
        status = "needs_attention"

    return {
        "book_id": book_id,
        "book_title": book_title,
        "audited_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "summary": {
            "critical_count": critical_count,
            "warning_count": warning_count,
            "character_count": character_count,
            "chapter_count_found": len(chapters),
        },
        "checks": checks,
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit generated novel project assets.")
    parser.add_argument("--book-id", required=True, help="Book id under novel_projects.")
    parser.add_argument("--projects-dir", default=None, help="Optional novel_projects directory.")
    parser.add_argument("--write", action="store_true", help="Write report to review/asset_completeness_report.json.")
    parser.add_argument("--fail-on-critical", action="store_true", help="Exit 2 if P0 issues exist.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    projects_dir = Path(args.projects_dir) if args.projects_dir else repo_root / "novel_projects"
    project_dir = projects_dir / args.book_id
    report = audit_project(project_dir)

    if args.write:
        review_dir = project_dir / "review"
        review_dir.mkdir(parents=True, exist_ok=True)
        (review_dir / "asset_completeness_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_critical and report["summary"]["critical_count"] > 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
