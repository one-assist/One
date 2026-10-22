"""Database functions and their isolated background worker."""

from datetime import datetime
import queue
import sqlite3
import threading
from typing import Any
from src.audio.speech import speech

class DatabaseManager:
    def __init__(self, path: str) -> None:
        self.path = path
        self.requests: queue.Queue[tuple[str, tuple[Any, ...]] | None] = queue.Queue()
        self.results: queue.Queue[Any] = queue.Queue()
        self.thread: threading.Thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self) -> None:
        db_file = sqlite3.connect(self.path)
        cursor = db_file.cursor()

        while True:
            request = self.requests.get()
            if request is None:
                break

            sql, params = request
            try:
                cursor.execute(sql, params)
                if sql.strip().upper().startswith("SELECT"):
                    self.results.put(cursor.fetchall())
                else:
                    db_file.commit()
                    self.results.put(True)
            except Exception:
                self.results.put(False)
            finally:
                self.requests.task_done()

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        self.requests.put((sql, params))
        return self.results.get()

    def close(self) -> None:
        self.requests.put(None)
        self.thread.join(timeout=1.0)


# Initialize the DatabaseManager with the default path or a defined path (for tests)
def get_db_manager(path: str = "database/one.db") -> DatabaseManager:
    database = DatabaseManager(path)
    return database
    
db_default = get_db_manager()

def create_table(db: DatabaseManager = db_default):
    db.execute(
        """CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        intent TEXT, 
        target TEXT)""",
    )
    db.execute(
        """CREATE TABLE IF NOT EXISTS task(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        time_remaining TEXT, 
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'finished', 'in progress')), 
        description TEXT)""",
    )

def create_task(
    name: str, 
    time_remaining: datetime | None, 
    status: str | None = "pending", 
    description: str | None = None,
    db: DatabaseManager = db_default):
        
    db.execute(
        "INSERT INTO task(name, time_remaining, status, description) VALUES(?, ?, ?, ?)",
        (name, time_remaining, status, description),
    )

def delete_task(name: str, db: DatabaseManager = db_default):
    if verify_task(name, db):
        db.execute(
            "DELETE FROM task WHERE name = ?",
            (name,),
        )

def verify_task(name: str, db: DatabaseManager = db_default) -> bool: 
    result = db.execute(
        "SELECT name FROM task WHERE name = ?",
        (name,),
    )
    
    return bool(result)  # Returns True if the task exists, False otherwise

def update_task_status(old_name: str, status:str, db: DatabaseManager = db_default):
    db.execute(
        "UPDATE status SET status = ? WHERE name = ?"
    )
    
def update_task_name(old_name:str, new_name: str, db: DatabaseManager = db_default):
    db.execute(
        "UPDATE task SET name = ? WHERE name = ?", (new_name, old_name)
    )

def update_task_time(name: str, new_date: datetime, db: DatabaseManager = db_default):
    db.execute(
        "UPDATE task SET time_remaining = ? WHERE name = ?", (new_date, name)
    )
def view_single_task(name: str, db: DatabaseManager = db_default):
    if not verify_task(name, db):
        speech("Task not found!")
        return

    result = db.execute(
        "SELECT * FROM task WHERE name = ?", 
        (name,),
    )
    
    if isinstance(result, Exception):
        speech(f"Error in {result}")
        return

    for row in result:
        print(row)
    
def view_tasks(db: DatabaseManager = db_default):
    result = db.execute("SELECT * FROM task")
    
    if isinstance(result, Exception):
        speech(f"Error in {result}")
        return

    for row in result:
        print(row)


def history_insert(intent: str, target: str, db: DatabaseManager = db_default):
    db.execute(
        "INSERT INTO history(intent, target) VALUES(?, ?)",
        (intent, target),
    )


def history_query(db: DatabaseManager = db_default):
    result = db.execute("SELECT * FROM history")
    if isinstance(result, Exception):
        speech(f"Error in {result}")
        return

    for row in result:
        print(row)


