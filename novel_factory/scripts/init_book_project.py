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
    write_json(project_dir / "bible" / "characters.json", {"book_title": title, "characters": []})
    write_json(project_dir / "bible" / "golden_finger.json", {
        "name": "",
        "type": "",
        "origin": "",
        "activation_condition": "",
        "visible_effect": "",
        "true_mechanism": "",
        "limitations": [],
        "costs": [],
        "failure_modes": [],
        "growth_stages": [],
        "misuse_risks": [],
        "anti_deus_ex_machina_rules": [],
    })
    write_json(project_dir / "bible" / "reader_promise.json", {
        "book_title": title,
        "promises": [],
        "must_deliver_every_chapter": [],
        "must_not_break": [],
    })
    write_json(project_dir / "bible" / "institutional_plausibility.json", {
        "central_premise": "",
        "plausibility_gap": "",
        "legal_or_governance_mechanism": "",
        "authorization_chain": [],
        "documents_to_seed": [],
        "people_who_know_truth": [],
        "people_who_exploit_gap": [],
        "reveal_schedule": [],
        "chapter_injections": [],
        "forbidden_explanations": [],
    })
    write_json(project_dir / "bible" / "long_novel_architecture.json", {
        "book_title": title,
        "target_total_words": 300000,
        "target_chapter_count": chapter_count,
        "core_premise": "",
        "first_20_role": "",
        "global_arc": "",
        "volumes": [],
        "protagonist_arc": [],
        "relationship_strategy": "",
        "antagonist_escalation": [],
        "motif_strategy": [],
        "secrets_reveal_policy": [],
        "forbidden_longform_patterns": [],
    })
    write_json(project_dir / "bible" / "foreshadowing.json", {"items": []})
    write_text(project_dir / "bible" / "style_bible.md", f"# {title} 文风圣经\n\n> 待由 `12_style_bible` 生成。\n")
    write_json(project_dir / "bible" / "voice_fingerprint.json", {
        "source_name": "",
        "average_sentence_length": 0,
        "sentence_length_variance": 0,
        "short_sentence_ratio": 0,
        "dialogue_ratio": 0,
        "paragraph_length_profile": [],
        "high_frequency_verbs": [],
        "high_frequency_particles": [],
        "preferred_punctuation": [],
        "metaphor_density": 0,
        "psychology_to_action_ratio": 0,
        "style_anchor_notes": [],
    })
    write_json(project_dir / "bible" / "anti_ai_phrasebook.zh.json", {
        "summary_phrases": ["显然", "毫无疑问", "不可否认", "归根结底", "某种意义上"],
        "emotion_cliches": ["空气仿佛凝固", "眼神复杂", "沉默良久", "心头一震", "嘴角勾起"],
        "explanation_cliches": ["他终于明白", "他意识到", "这意味着", "这不仅是"],
        "structure_cliches": ["不是因为", "而是因为", "与其说", "不如说"],
        "usage_note": "先用于审计和扣分，不做绝对禁用。",
    })
    write_json(project_dir / "outline" / "chapters_20.json", {"book_title": title, "chapter_count": chapter_count, "chapters": []})
    write_json(project_dir / "outline" / "volumes.json", {"book_title": title, "volumes": []})
    write_json(project_dir / "outline" / "current_batch_outline.json", {"book_title": title, "chapters": []})
    write_json(project_dir / "memory" / "chapter_summaries.json", {"chapters": []})
    write_json(project_dir / "memory" / "global_arc_ledger.json", {"items": []})
    write_json(project_dir / "memory" / "plot_thread_ledger.json", {"threads": []})
    write_json(project_dir / "memory" / "relationship_ledger.json", {"relationships": []})
    write_json(project_dir / "memory" / "state_memory.json", {"characters": [], "locations": [], "organizations": [], "must_remember": []})
    write_json(project_dir / "memory" / "foreshadow_ledger.json", {"items": []})
    write_json(project_dir / "memory" / "character_arc_ledger.json", {"characters": []})
    write_json(project_dir / "memory" / "causality_ledger.json", {"events": []})
    write_json(project_dir / "memory" / "golden_finger_ledger.json", {"history": []})
    write_json(project_dir / "memory" / "pressure_ledger.json", {"items": []})
    write_json(project_dir / "memory" / "knowledge_state_ledger.json", {"items": []})
    write_json(project_dir / "memory" / "antagonist_move_ledger.json", {"moves": []})
    write_json(project_dir / "memory" / "protagonist_cost_ledger.json", {"items": []})
    write_json(project_dir / "memory" / "motif_ledger.json", {"items": []})
    write_json(project_dir / "memory" / "editorial_feedback_ledger.json", {"diagnoses": []})
    write_json(project_dir / "memory" / "hook_ledger.json", {"items": []})
    write_text(project_dir / "memory" / "continuity_notes.md", "# 连续性记录\n\n")
    write_json(project_dir / "review" / "qa_report.json", {"chapters": []})
    write_json(project_dir / "review" / "anti_ai_report.json", {"chapters": []})
    write_json(project_dir / "review" / "style_report.json", {"chapters": []})
    write_json(project_dir / "review" / "logic_report.json", {"chapters": []})
    write_json(project_dir / "review" / "foreshadow_report.json", {"chapters": []})
    write_json(project_dir / "review" / "arc_continuity_report.json", {"batches": []})
    write_text(project_dir / "export" / "full_book.md", f"# {title}\n\n")

    readme = f"""# {title}

book_id: `{book_id}`

## 生成顺序

1. 用 `01_seed_from_title` 生成 `bible/story_seed.json`。
2. 用 `02_story_bible` 生成 `bible/story_bible.md`。
3. 用 `10_character_cards` 生成 `bible/characters.json`。
4. 用 `11_golden_finger` 生成 `bible/golden_finger.json`。
5. 用 `12_style_bible` 生成 `bible/style_bible.md`。
6. 用 `13_voice_fingerprint` 生成 `bible/voice_fingerprint.json`。
7. 用 `19_institutional_plausibility_patch` 生成 `bible/institutional_plausibility.json`。
8. 长篇模式：用 `23_long_novel_architect` 生成 `bible/long_novel_architecture.json`。
9. 长篇模式：用 `24_volume_arc_planner` 生成 `outline/volumes.json`。
10. 20章试写模式：用 `03_outline_20` 生成 `outline/chapters_20.json`。
11. 长篇模式：用 `25_rolling_batch_20_planner` 生成当前批次 `outline/current_batch_outline.json`。
12. 可选：用 `18_editorial_diagnosis_from_feedback` 消化人工或外部 AI 评价，写入 `memory/editorial_feedback_ledger.json`。
13. 按章节循环生成：
   - `review/ch001.logic.json`
   - `review/ch001.foreshadow.json`
   - `review/ch001.antagonist.json`
   - `review/ch001.cost.json`
   - `review/ch001.motif.json`
   - `chapter_tasks/ch001.task.json`
   - `scenes/ch001.scenes.json`
   - `scenes/ch001_scene01.md`
   - `chapters/ch001.md`
   - `review/ch001.anti_ai.json`
   - `review/ch001.qa.json`
   - `memory/ch001.memory.json`
14. 回写长期账本：
   - `memory/foreshadow_ledger.json`
   - `memory/character_arc_ledger.json`
   - `memory/causality_ledger.json`
   - `memory/global_arc_ledger.json`
   - `memory/plot_thread_ledger.json`
   - `memory/relationship_ledger.json`
   - `memory/antagonist_move_ledger.json`
   - `memory/protagonist_cost_ledger.json`
   - `memory/motif_ledger.json`
15. 每个 20 章批次后，用 `26_arc_continuity_auditor` 生成 `review/arc_continuity_report.json`。
16. 最后合并到 `export/full_book.md`。

## 当前状态

项目骨架已初始化，等待 AI 工作流填充内容。V0.5 已包含人物卡、金手指、风格圣经、制度可信度补丁、编辑反馈诊断、反派反制、主角代价、核心隐喻、30万字长篇架构、分卷弧线、滚动20章批次规划和长期记忆账本占位。
"""
    write_text(project_dir / "README.md", readme)
    return project_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize an AI novel project.")
    parser.add_argument("--title", required=True, help="Novel title.")
    parser.add_argument("--book-id", default=None, help="Optional stable book id.")
    parser.add_argument("--chapter-count", type=int, default=20, help="Chapter count, default 20. Use about 100-120 for a 300k-word novel.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    book_id = args.book_id or safe_book_id(args.title)
    project_dir = build_project(repo_root, args.title, book_id, args.chapter_count)
    print(project_dir)


if __name__ == "__main__":
    main()
