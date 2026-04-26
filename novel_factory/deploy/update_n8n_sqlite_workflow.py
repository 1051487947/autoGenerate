import argparse
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path


def load_json_column(value, fallback):
    if not value:
        return fallback
    return json.loads(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update or insert an n8n SQLite workflow from an exported workflow JSON.")
    parser.add_argument("--workflow-id", required=True, help="Existing n8n workflow id to update.")
    parser.add_argument("--db", default="/n8n/data/database.sqlite", help="Mounted n8n SQLite database path.")
    parser.add_argument(
        "--workflow-json",
        default="/workspace/novel_factory/n8n/Novel Seed - Bridge GPT MVP.json",
        help="Mounted workflow JSON export path.",
    )
    parser.add_argument("--backup-dir", default="/n8n/backups", help="Directory used to store workflow backups.")
    parser.add_argument("--insert-if-missing", action="store_true", help="Create the workflow when it does not exist.")
    parser.add_argument("--project-id", default=None, help="Project id for newly inserted workflows.")
    args = parser.parse_args()

    db_path = Path(args.db)
    workflow_path = Path(args.workflow_json)
    backup_dir = Path(args.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    row = cursor.execute(
        "select id,name,active,nodes,connections,settings,pinData,meta from workflow_entity where id=?",
        (args.workflow_id,),
    ).fetchone()
    if not row:
        if not args.insert_if_missing:
            raise SystemExit(f"workflow not found: {args.workflow_id}")
        project_id = args.project_id
        if not project_id:
            project_row = cursor.execute("select projectId from shared_workflow limit 1").fetchone()
            if project_row:
                project_id = project_row[0]
        if not project_id:
            project_row = cursor.execute("select id from project order by createdAt limit 1").fetchone()
            if project_row:
                project_id = project_row[0]
        if not project_id:
            raise SystemExit("project id is required when inserting a new workflow")

        cursor.execute(
            """
            insert into workflow_entity (
                id, name, active, nodes, connections, settings, staticData,
                pinData, versionId, triggerCount, meta
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                args.workflow_id,
                workflow.get("name") or args.workflow_id,
                1 if workflow.get("active") else 0,
                json.dumps(workflow.get("nodes") or [], ensure_ascii=False),
                json.dumps(workflow.get("connections") or {}, ensure_ascii=False),
                json.dumps(workflow.get("settings") or {}, ensure_ascii=False),
                None,
                json.dumps(workflow.get("pinData") or {}, ensure_ascii=False),
                str(uuid.uuid4()),
                0,
                json.dumps(workflow.get("meta") or {}, ensure_ascii=False),
            ),
        )
        cursor.execute(
            """
            insert or ignore into shared_workflow (workflowId, projectId, role)
            values (?, ?, ?)
            """,
            (args.workflow_id, project_id, "workflow:owner"),
        )
        connection.commit()
        print(
            json.dumps(
                {
                    "inserted": args.workflow_id,
                    "nodes": len(workflow.get("nodes") or []),
                    "connections": len(workflow.get("connections") or {}),
                    "project_id": project_id,
                },
                ensure_ascii=False,
            )
        )
        return

    backup = {
        "id": row[0],
        "name": row[1],
        "active": bool(row[2]),
        "nodes": load_json_column(row[3], []),
        "connections": load_json_column(row[4], {}),
        "settings": load_json_column(row[5], {}),
        "pinData": load_json_column(row[6], {}),
        "meta": load_json_column(row[7], {}),
    }
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"workflow_{args.workflow_id}_{timestamp}.json"
    backup_path.write_text(json.dumps(backup, ensure_ascii=False, indent=2), encoding="utf-8")

    cursor.execute(
        """
        update workflow_entity
           set name=?,
               nodes=?,
               connections=?,
               settings=?,
               pinData=?,
               meta=?,
               versionId=?,
               updatedAt=strftime('%Y-%m-%d %H:%M:%f', 'now')
         where id=?
        """,
        (
            workflow.get("name") or row[1],
            json.dumps(workflow.get("nodes") or [], ensure_ascii=False),
            json.dumps(workflow.get("connections") or {}, ensure_ascii=False),
            json.dumps(workflow.get("settings") or {}, ensure_ascii=False),
            json.dumps(workflow.get("pinData") or {}, ensure_ascii=False),
            json.dumps(workflow.get("meta") or {}, ensure_ascii=False),
            str(uuid.uuid4()),
            args.workflow_id,
        ),
    )
    connection.commit()

    print(
        json.dumps(
            {
                "updated": args.workflow_id,
                "nodes": len(workflow.get("nodes") or []),
                "connections": len(workflow.get("connections") or {}),
                "backup": str(backup_path),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
