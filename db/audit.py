import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("db/agentguard.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            user_id TEXT NOT NULL,
            resource TEXT NOT NULL,
            decision TEXT NOT NULL,
            policy_rule TEXT NOT NULL,
            reason TEXT NOT NULL,
            jit_expiry TEXT
        )""")

        columns = [row[1] for row in conn.execute("PRAGMA table_info(audit_log)").fetchall()]
        if "agent_name" not in columns:
            conn.execute("ALTER TABLE audit_log ADD COLUMN agent_name TEXT NOT NULL DEFAULT ''")

def log_decision(agent_id, agent_name, user_id, resource, decision, policy_rule, reason, jit_expiry=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO audit_log
            (timestamp,agent_id,agent_name,user_id,resource,decision,policy_rule,reason,jit_expiry)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (datetime.now().isoformat(), agent_id, agent_name, user_id, resource,
             decision, policy_rule, reason, jit_expiry))

def get_all_logs():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC").fetchall()
        return [dict(r) for r in rows]