"""Database functions and their isolated background worker."""

import atexit
import queue
import sqlite3
import threading

from typing import Any
from datetime import datetime
from src.audio.speech import speech
from database.errors.err_db import *
from concurrent.futures import Future

#type alias for the result and request of a database query
type QueryResult = list[tuple[Any, ...]] | bool 
type Request  = tuple[
    str, 
    tuple[Any, ...],
    Future[QueryResult]
]
    
class DatabaseManager:
    def __init__(self, path: str) -> None:
        self.path = path
        self.requests: queue.Queue[Request | None] = queue.Queue()
        self._ready: Future[None] = Future()
        self._lock = threading.Lock()
        self._closed = False
        self.thread: threading.Thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self._ready.result(timeout = 10)  # Wait for the thread to be ready

    def _run(self) -> None:
        connection = None

        try:
            connection = sqlite3.connect(self.path, timeout=5)
            cursor = connection.cursor()
            self._ready.set_result(None)  # Signal that the thread is ready

            while True:
                request = self.requests.get()
                
                try:
                    
                    if request is None:
                        break
    
                    sql, params, future = request
                    try:
                        cursor.execute(sql, params)
                        
                        if cursor.description is not None:  # If the query returns rows
                            result = cursor.fetchall()
                        else:
                            connection.commit()
                            result = True 
                            
                    except Exception:
                        self.results.put(False)
                    finally:
                        self.requests.task_done()
                finally:
                    db_file.close()

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        self.requests.put((sql, params))
        return self.results.get()

    def close(self) -> None:
        if self.thread.is_alive():
            self.requests.put(None)
            self.thread.join(timeout=1.0)


# Initialize the DatabaseManager with the default path or a defined path (for tests)
def get_db_manager(path: str = "database/one.db") -> DatabaseManager:
    database = DatabaseManager(path)
    return database
    
db_default = get_db_manager()
atexit.register(db_default.close)

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

    if time_remaining:
        clean_time = time_remaining.strftime("%Y-%m-%d %H:%M")
    else:
        clean_time = time_remaining
        
    db.execute(
        "INSERT INTO task(name, time_remaining, status, description) VALUES(?, ?, ?, ?)",
        (name, clean_time, status, description),
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
        "UPDATE task SET status = ? WHERE name = ?",
        (status, old_name)
    )

def update_task_description(old_name:str, new_description: str, db: DatabaseManager = db_default):
    db.execute(
        "UPDATE task SET description = ? WHERE name = ?",
        (new_description, old_name)
    )
    
def update_task_name(old_name:str, new_name: str, db: DatabaseManager = db_default):
    db.execute(
        "UPDATE task SET name = ? WHERE name = ?", (new_name, old_name)
    )

def update_task_time(name: str, new_date: datetime, db: DatabaseManager = db_default):
    clean_time = None
    
    if new_date:
        clean_time = new_date.strftime("%Y-%m-%d %H:%M")
    
    db.execute(
        "UPDATE task SET time_remaining = ? WHERE name = ?", (clean_time, name)
    )
def view_single_task(name: str, db: DatabaseManager = db_default):
    if not verify_task(name, db):
        raise Exception(f"Task '{name}' does not exist.")

    result = db.execute(
        "SELECT * FROM task WHERE name = ?", 
        (name,),
    )

    return result
    
def view_tasks(db: DatabaseManager = db_default):
    result = db.execute("SELECT * FROM task")
    
    if isinstance(result, Exception):
        speech(f"Error in {result}")
        return

    for row in result:
        print(row)


def history_insert(intent: str, target: str | None = None, db: DatabaseManager = db_default):
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


