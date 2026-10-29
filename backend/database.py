"""Small JSON-document repository backed by a local SQLite database."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any


class SQLiteCursor(list):
    def sort(self, key: str, direction: int = 1):
        super().sort(key=lambda row: (row.get(key) is None, row.get(key)), reverse=direction < 0)
        return self

    def limit(self, count: int):
        return SQLiteCursor(self[:count])


class SQLiteCollection:
    def __init__(self, database: "SQLiteDatabase", name: str):
        self.database = database
        self.name = name

    def create_index(self, key: str, unique: bool = False):
        if not unique:
            return key
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError("Invalid index field")
        safe_name = f"uq_{self.name}_{key}".replace("-", "_")
        with self.database._lock:
            rows = self.find()
            values = [row.get(key) for row in rows if row.get(key) is not None]
            if len(values) != len(set(values)):
                raise ValueError(f"Existing {self.name} records contain duplicate {key} values")
            self.database._commit()
        return safe_name

    def find(self, query: dict[str, Any] | None = None, projection: dict[str, int] | None = None):
        with self.database._lock:
            rows = self.database.connection.execute(
                "SELECT document FROM documents WHERE collection = ?", (self.name,)
            ).fetchall()
        matches = [json.loads(row[0]) for row in rows]
        matches = [row for row in matches if _matches(row, query or {})]
        if projection:
            included = {key for key, enabled in projection.items() if enabled}
            if included:
                matches = [{key: value for key, value in row.items() if key in included or key == "_id"} for row in matches]
        return SQLiteCursor(matches)

    def find_one(self, query: dict[str, Any] | None = None, projection: dict[str, int] | None = None):
        rows = self.find(query, projection)
        return rows[0] if rows else None

    def count_documents(self, query: dict[str, Any] | None = None) -> int:
        return len(self.find(query))

    def insert_one(self, document: dict[str, Any]):
        record = dict(document)
        if not record.get("_id"):
            raise ValueError("Every record needs an _id")
        with self.database._lock:
            self.database.connection.execute(
                "INSERT INTO documents(collection, record_id, document) VALUES (?, ?, ?)",
                (self.name, str(record["_id"]), json.dumps(record, ensure_ascii=False)),
            )
            self.database._commit()
        return record["_id"]

    def insert_many(self, documents: list[dict[str, Any]]):
        with self.database._lock:
            self.database.connection.executemany(
                "INSERT INTO documents(collection, record_id, document) VALUES (?, ?, ?)",
                [(self.name, str(row["_id"]), json.dumps(row, ensure_ascii=False)) for row in documents],
            )
            self.database._commit()

    def update_one(self, query: dict[str, Any], update: dict[str, Any]):
        row = self.find_one(query)
        if row is None:
            return 0
        row.update(update.get("$set", {}))
        self._replace(row)
        return 1

    def find_one_and_update(self, query: dict[str, Any], update: dict[str, Any], return_document: bool = True):
        row = self.find_one(query)
        if row is None:
            return None
        row.update(update.get("$set", {}))
        self._replace(row)
        return row

    def delete_one(self, query: dict[str, Any]):
        row = self.find_one(query)
        if row is None:
            return 0
        with self.database._lock:
            cursor = self.database.connection.execute(
                "DELETE FROM documents WHERE collection = ? AND record_id = ?",
                (self.name, str(row["_id"])),
            )
            self.database._commit()
        return cursor.rowcount

    def _replace(self, row: dict[str, Any]):
        with self.database._lock:
            self.database.connection.execute(
                "UPDATE documents SET document = ? WHERE collection = ? AND record_id = ?",
                (json.dumps(row, ensure_ascii=False), self.name, str(row["_id"])),
            )
            self.database._commit()


class SQLiteDatabase:
    COLLECTIONS = {"customers", "products", "users", "entitlements", "payments", "activations", "issues"}

    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS documents (collection TEXT NOT NULL, record_id TEXT NOT NULL, document TEXT NOT NULL, PRIMARY KEY(collection, record_id))"
        )
        self.connection.commit()
        self._lock = threading.RLock()
        self._transaction_depth = 0
        self._collections: dict[str, SQLiteCollection] = {}

    def __getattr__(self, name: str):
        if name in self.COLLECTIONS:
            return self[name]
        raise AttributeError(name)

    def __getitem__(self, name: str):
        if name not in self.COLLECTIONS:
            raise KeyError(name)
        if name not in self._collections:
            self._collections[name] = SQLiteCollection(self, name)
        return self._collections[name]

    @contextmanager
    def transaction(self):
        with self._lock:
            outermost = self._transaction_depth == 0
            if outermost:
                self.connection.execute("BEGIN IMMEDIATE")
            self._transaction_depth += 1
            try:
                yield
            except Exception:
                self._transaction_depth -= 1
                if outermost:
                    self.connection.rollback()
                raise
            else:
                self._transaction_depth -= 1
                if outermost:
                    self.connection.commit()

    def _commit(self):
        if self._transaction_depth == 0:
            self.connection.commit()

    def close(self):
        with self._lock:
            self.connection.close()


def _matches(document: dict[str, Any], query: dict[str, Any]) -> bool:
    for key, expected in query.items():
        actual = document.get(key)
        if isinstance(expected, dict):
            if "$exists" in expected and (key in document) != expected["$exists"]:
                return False
            if "$ne" in expected and actual == expected["$ne"]:
                return False
        elif actual != expected:
            return False
    return True


@lru_cache(maxsize=1)
def get_db() -> SQLiteDatabase:
    base = Path(__file__).resolve().parent.parent
    path = os.getenv("DATABASE_PATH", str(base / "data" / "cliently.sqlite3"))
    return SQLiteDatabase(path)
