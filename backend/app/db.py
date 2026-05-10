"""SQLite database for BioAEGIS — automatic path, no configuration needed."""
import sqlite3, os
from pathlib import Path

DB_PATH = Path.home() / "BIOAEGIS" / "bioaegis.db"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS custom_parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL, label TEXT NOT NULL,
        unit TEXT DEFAULT '', category TEXT DEFAULT 'custom',
        normal_min REAL, normal_max REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS custom_interventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, description TEXT DEFAULT '',
        icon TEXT DEFAULT '💊', color TEXT DEFAULT '#8b5cf6',
        strength TEXT DEFAULT 'moderate', effects TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT, months INTEGER DEFAULT 6,
        intervention_id TEXT DEFAULT 'none', intervention_name TEXT DEFAULT '',
        results_json TEXT, final_bio_age REAL, final_pace REAL, confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simulation_id INTEGER, agent_id TEXT, agent_name TEXT, tick INTEGER,
        reasoning TEXT, assessment TEXT, concerns TEXT, recommended_actions TEXT,
        confidence REAL, signals_emitted TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (simulation_id) REFERENCES simulations(id)
    );
    CREATE TABLE IF NOT EXISTS signal_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simulation_id INTEGER, signal_name TEXT, signal_priority TEXT,
        reasoning TEXT, emitted_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (simulation_id) REFERENCES simulations(id)
    );
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE, user_data_json TEXT, initial_bio_age REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    print(f"[DB] SQLite ready at {DB_PATH}")
