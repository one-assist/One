"""Database functions and their isolated background worker."""

import atexit
import queue
import sqlite3
import threading
import logging

from typing import Any
from datetime import datetime
from src.audio.speech import speech
from concurrent.futures import Future, TimeoutError as FutureTimeoutError

from database.errors.err_db import DatabaseError, DatabaseTimeoutError
from src.commands.errors.err_actions import HistoryQueryError, TaskNotFoundError

logger = logging.getLogger(__name__)

# A SELECT returns rows; a successful write operation returns True.
type QueryResult = list[tuple[Any, ...]] | bool
# Every queued request carries its Future so the calling thread can await its own result.
type Request = tuple[
    str,
    tuple[Any, ...],
    Future[QueryResult],
]


class DatabaseManager:
    """Serialize SQLite access through one worker-owned connection."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.requests: queue.Queue[Request | None] = queue.Queue()
        self._ready: Future[None] = Future()
        self._lock = threading.Lock()
        self._closed = False
        # The worker owns the SQLite connection; callers communicate only through requests.
        self.thread: threading.Thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

        # Do not accept requests until the worker has opened its connection.
        try:
            self._ready.result(timeout=10)
        except FutureTimeoutError as cause:
            raise DatabaseTimeoutError("Database worker did not start") from cause

    def _run(self) -> None:
        connection = None

        try:
            # A SQLite connection must remain in the thread that created it.
            connection = sqlite3.connect(self.path, timeout=5)
            cursor = connection.cursor()
            self._ready.set_result(None)

            while True:
                request = self.requests.get()
                
                try:
                    
                    # None is the shutdown sentinel enqueued by close().
                    if request is None:
                        break
    
                    sql, params, future = request
                    try:
                        cursor.execute(sql, params)
                        
                        # cursor.description is populated for SELECT-like statements.
                        if cursor.description is not None:
                            result = cursor.fetchall()
                        else:
                            connection.commit()
                            result = True 

                    except sqlite3.Error as error:
                        # Keep the connection reusable after a failed write request.
                        connection.rollback()

                        logger.exception("Database request failed")

                        future.set_exception(
                            DatabaseError(f"Database error: {error}")
                        )
                    
                    else:
                        # Unblock only the caller that submitted this request.
                        future.set_result(result)

                finally:
                    self.requests.task_done()

        except Exception as cause:
            error = DatabaseError(f"Database worker failed: {cause}")
            logger.exception("Database worker failed")

            if not self._ready.done():
                self._ready.set_exception(error)

            while True:
                try:
                    pending = self.requests.get_nowait()
                except queue.Empty:
                    break

                if pending is not None:
                    # A dead worker must not leave callers blocked on pending Futures.
                    _, _, future = pending
                    future.set_exception(error)

                self.requests.task_done()
        finally:
            if connection is not None:
                connection.close()
                            
    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> QueryResult:
        """Queue one statement and wait for the worker-owned connection to finish it."""
        future: Future[QueryResult] = Future()

        with self._lock:
            if self._closed:
                raise DatabaseError("DatabaseManager is closed.")

            if not self.thread.is_alive():
                raise DatabaseError(
                    "Database worker is not running"
                )
                
            self.requests.put((sql, params, future))

        try:
            return future.result(timeout = 10)

        except FutureTimeoutError as cause:
            error = DatabaseTimeoutError()
            logger.error("[%s] %s", error.code, error.user_message)
            raise error from cause

    def close(self) -> None:
        """Stop the worker after queued requests and release its SQLite connection."""
        with self._lock:
            if self._closed:
                return

            self._closed = True
            self.requests.put(None)

        self.thread.join(timeout = 5)

        if self.thread.is_alive():
            raise DatabaseTimeoutError("Database worker did not stop")
 

# Tests pass a temporary path; application code uses the default persistent database.
def get_db_manager(path: str = "database/one.db") -> DatabaseManager:
    return DatabaseManager(path)
    
db_default = get_db_manager()
atexit.register(db_default.close)

def create_table(db: DatabaseManager = db_default):
    _ = db.execute(
        """CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        intent TEXT, 
        target TEXT)""",
    )
    _ = db.execute(
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
        
    _ = db.execute(
        "INSERT INTO task(name, time_remaining, status, description) VALUES(?, ?, ?, ?)",
        (name, clean_time, status, description),
    )

def delete_task(name: str, db: DatabaseManager = db_default):
    if verify_task(name, db):
        _ = db.execute(
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
    _ = db.execute(
        "UPDATE task SET status = ? WHERE name = ?",
        (status, old_name)
    )

def update_task_description(old_name:str, new_description: str, db: DatabaseManager = db_default):
    _ = db.execute(
        "UPDATE task SET description = ? WHERE name = ?",
        (new_description, old_name)
    )
    
def update_task_name(old_name:str, new_name: str, db: DatabaseManager = db_default):
    _ =db.execute(
        "UPDATE task SET name = ? WHERE name = ?", (new_name, old_name)
    )

def update_task_time(name: str, new_date: datetime, db: DatabaseManager = db_default):
    clean_time = None
    
    if new_date:
        clean_time = new_date.strftime("%Y-%m-%d %H:%M")
    
    _ =db.execute(
        "UPDATE task SET time_remaining = ? WHERE name = ?", (clean_time, name)
    )
def view_single_task(name: str, db: DatabaseManager = db_default):
    if not verify_task(name, db):
        raise TaskNotFoundError(f"Task '{name}' does not exist.")

    result = db.execute(
        "SELECT * FROM task WHERE name = ?", 
        (name,),
    )
    
    if isinstance(result, bool):
        logger.error("view_single_task() did not return rows.")
        return

    return result
    
def view_tasks(db: DatabaseManager = db_default):
    result = db.execute("SELECT * FROM task")

    if isinstance(result, bool):
        logger.error("view_tasks() did not return rows.")
        return
        
    return result

def history_insert(intent: str, target: str | None = None, db: DatabaseManager = db_default):
    _ = db.execute(
        "INSERT INTO history(intent, target) VALUES(?, ?)",
        (intent, target),
    )

def history_query(
    db: DatabaseManager = db_default,
) -> list[tuple[Any, ...]]:
    try:
        result = db.execute("SELECT * FROM history")
    except DatabaseError as cause:
        raise HistoryQueryError() from cause

    if isinstance(result, bool):
        raise HistoryQueryError("History query did not return rows.")

    return result
        

