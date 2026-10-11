"""
database.py
---------------------------------------------
AI Crowd Surveillance Enterprise Database Manager
Supports:
- Repository pattern tables (crowd_log, alerts, sensor_log, system_health)
- Indexing for high-speed queries on timestamp and status
- Pagination & time-range filtering (last hour, day, week)
- Thread-safe SQLite execution via RLock
---------------------------------------------
Author : Ved Rathod (Refactored)
"""

import sqlite3
import threading
from pathlib import Path
from datetime import datetime, timedelta

from config import DATABASE_FILE


class CrowdDatabase:
    """
    Enterprise SQLite Database Manager.
    """

    def __init__(self):
        Path(DATABASE_FILE).parent.mkdir(parents=True, exist_ok=True)

        self.lock = threading.RLock()
        self.connection = sqlite3.connect(
            DATABASE_FILE,
            check_same_thread=False
        )
        self.cursor = self.connection.cursor()

        self.create_tables()

    # ------------------------------------------------------
    # Create Tables & Indexing
    # ------------------------------------------------------

    def create_tables(self):
        with self.lock:
            # 1. Crowd Log Table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS crowd_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                people INTEGER,
                piezo INTEGER,
                ir INTEGER,
                sw420 INTEGER,
                risk_score INTEGER,
                crowd_status TEXT,
                trend TEXT
            )
            """)

            # 2. Alerts History Table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                message TEXT
            )
            """)

            # 3. Hardware Sensor Log Table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                piezo INTEGER,
                ir INTEGER,
                sw420 INTEGER,
                connected INTEGER
            )
            """)

            # 4. System Health Table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_health(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cpu REAL,
                ram REAL,
                db_status TEXT,
                camera_status TEXT,
                esp_status TEXT,
                ai_status TEXT,
                fps REAL
            )
            """)

            # 5. AI Model Evaluation Results Table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_results(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                dataset_name TEXT,
                model_version TEXT,
                images_tested INTEGER,
                tp INTEGER,
                fp INTEGER,
                fn INTEGER,
                tn INTEGER,
                accuracy REAL,
                evaluation_time_sec REAL
            )
            """)

            # ------------------------------------------------------
            # Indexing for Fast Analytical Queries
            # ------------------------------------------------------
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_crowd_log_timestamp ON crowd_log(timestamp);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_crowd_log_status ON crowd_log(crowd_status);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(level);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_log_timestamp ON sensor_log(timestamp);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_health_timestamp ON system_health(timestamp);")

            self.connection.commit()

    # ------------------------------------------------------
    # Save Methods
    # ------------------------------------------------------

    def save_crowd_data(self, people, piezo, ir, sw420, risk_score, crowd_status, trend):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            self.cursor.execute("""
            INSERT INTO crowd_log(
                timestamp, people, piezo, ir, sw420, risk_score, crowd_status, trend
            )
            VALUES(?,?,?,?,?,?,?,?)
            """, (timestamp, people, piezo, ir, sw420, risk_score, crowd_status, trend))
            self.connection.commit()

    def save_alert(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            self.cursor.execute("""
            INSERT INTO alerts(timestamp, level, message)
            VALUES(?,?,?)
            """, (timestamp, level, message))
            self.connection.commit()

    def save_sensor_data(self, piezo, ir, sw420, connected):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            self.cursor.execute("""
            INSERT INTO sensor_log(timestamp, piezo, ir, sw420, connected)
            VALUES(?,?,?,?,?)
            """, (timestamp, int(piezo), int(ir), int(sw420), 1 if connected else 0))
            self.connection.commit()

    def save_system_health(self, cpu, ram, db_status, camera_status, esp_status, ai_status, fps):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            self.cursor.execute("""
            INSERT INTO system_health(
                timestamp, cpu, ram, db_status, camera_status, esp_status, ai_status, fps
            )
            VALUES(?,?,?,?,?,?,?,?)
            """, (timestamp, cpu, ram, db_status, camera_status, esp_status, ai_status, fps))
            self.connection.commit()

    def save_evaluation_result(self, dataset_name, model_version, images_tested, tp, fp, fn, tn, accuracy, eval_time):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            self.cursor.execute("""
            INSERT INTO evaluation_results(
                timestamp, dataset_name, model_version, images_tested, tp, fp, fn, tn, accuracy, evaluation_time_sec
            )
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """, (timestamp, dataset_name, model_version, images_tested, tp, fp, fn, tn, accuracy, eval_time))
            self.connection.commit()

    # ------------------------------------------------------
    # Query Engine (Pagination & Time-Range Filtering)
    # ------------------------------------------------------

    def _get_threshold_timestamp(self, time_range):
        now = datetime.now()
        if time_range == "1h":
            return (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        elif time_range == "24h":
            return (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        elif time_range == "7d":
            return (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        return None

    def query_paginated(self, table_name, page=1, per_page=50, time_range="all", filter_col=None, filter_val=None):
        """
        Generic paginated query with timestamp range filtering and index utilization.
        """
        if table_name not in ("crowd_log", "alerts", "sensor_log", "system_health"):
            raise ValueError(f"Invalid table name: {table_name}")

        page = max(1, int(page))
        per_page = max(1, min(200, int(per_page)))
        offset = (page - 1) * per_page

        where_clauses = []
        params = []

        threshold = self._get_threshold_timestamp(time_range)
        if threshold:
            where_clauses.append("timestamp >= ?")
            params.append(threshold)

        if filter_col and filter_val is not None:
            where_clauses.append(f"{filter_col} = ?")
            params.append(filter_val)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        with self.lock:
            # Get total matching rows
            count_sql = f"SELECT COUNT(*) FROM {table_name} {where_sql}"
            self.cursor.execute(count_sql, tuple(params))
            total_count = self.cursor.fetchone()[0]

            # Get paginated data
            data_sql = f"SELECT * FROM {table_name} {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?"
            self.cursor.execute(data_sql, tuple(params + [per_page, offset]))
            rows = self.cursor.fetchall()

        pages = max(1, (total_count + per_page - 1) // per_page)

        return {
            "items": rows,
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "pages": pages
        }

    # ------------------------------------------------------
    # Latest Data Methods
    # ------------------------------------------------------

    def latest_data(self):
        with self.lock:
            self.cursor.execute("SELECT * FROM crowd_log ORDER BY id DESC LIMIT 1")
            return self.cursor.fetchone()

    def get_latest_evaluation_result(self):
        with self.lock:
            self.cursor.execute("SELECT * FROM evaluation_results ORDER BY id DESC LIMIT 1")
            row = self.cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "timestamp": row[1],
                    "dataset_name": row[2],
                    "model_version": row[3],
                    "images_tested": row[4],
                    "tp": row[5],
                    "fp": row[6],
                    "fn": row[7],
                    "tn": row[8],
                    "accuracy": row[9],
                    "evaluation_time_sec": row[10]
                }
            return None

    def get_recent_data(self, limit=50):
        with self.lock:
            self.cursor.execute("SELECT * FROM crowd_log ORDER BY id DESC LIMIT ?", (limit,))
            return self.cursor.fetchall()

    def execute_query(self, sql, params=()):
        with self.lock:
            self.cursor.execute(sql, params)
            self.connection.commit()
            return self.cursor

    def close(self):
        with self.lock:
            self.connection.close()


# Enterprise Global Database Singleton
db = CrowdDatabase()