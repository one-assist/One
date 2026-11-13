"""Database functions and their isolated background worker."""

import atexit
import queue
import sqlite3
import threading
import logging

from typing import Any
from datetime import datetime
from src.audio.speech import speech
from database.errors.err_db import *
from concurrent.futures import Future

logger = logging.getLogger(__name__)

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

                    except sqlite3.Error as error:
                        # If an error occurs, rollback the transaction and log the error
                        connection.rollback()

                        logger.exception("Database error: %s", error)

                        future.set_exception(
                            DatabaseError(f"Database error: {error}")
                        )
                    
                    else:
                        # If the query was successful, set the result of the future
                        future.set_result(result)

                finally:
                    self.requests.task_done()

        except DatabaseError as error:
            logger.error("[%s] %s", error.code, error.user_message)

            # If an error occurs, set the exception of the future
            if not self._ready.done():
                self._ready.set_exception(error)

            # If the thread is shutting down, set the exception of all pending requests
            while True:
                try:
                    # Get all pending requests and set their exceptions
                    pending = self.requests.get_nowait()

                except queue.Empty:
                    break

                if pending is not None:
                    _, _, future = pending
                    future.set_exception(error)

                self.requests.task_done()
        finally:
            if connection is not None:
                connection.close()
                            
    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> QueryResult:

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

        except TimeoutError as error:
            raise TimeoutError(
                logger.error("[%s] %s", error.code, error.user_message)
            )from error

    def close(self) -> None:

        with self._lock:
            if self._closed:
                return

            self._closed = True
            self.requests.put(None)

        self.thread.join(timeout = 5)

        if self.thread.is_alive():
            raise TimeoutError(
                "Database worker did not stop"
            )
 

# Initialize the DatabaseManager with the default path or a defined path (for tests)
def get_db_manager(path: str = "database/one.db") -> DatabaseManager:
    database = DatabaseManager(path)
    return database
    
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
        raise Exception(f"Task '{name}' does not exist.")

    result = db.execute(
        "SELECT * FROM task WHERE name = ?", 
        (name,),
    )

    return result
    
def view_tasks(db: DatabaseManager = db_default):
    result = db.execute("SELECT * FROM task")
    return result

def history_insert(intent: str, target: str | None = None, db: DatabaseManager = db_default):
    _ = db.execute(
        "INSERT INTO history(intent, target) VALUES(?, ?)",
        (intent, target),
    )

def history_query(
    db: DatabaseManager = db_default,
):
    try:
        result = db.execute("SELECT * FROM history")
        
        if isinstance(result, bool):
            logger.error("History query did not return rows.")
            return []
    
        for row in result:
            print(row)
            
    except DatabaseError as error:
        logger.error("[%s] %s", error.code, error.user_message)
        return 
        

