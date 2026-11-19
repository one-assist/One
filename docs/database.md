# Database Management

This document describes the SQLite persistence layer implemented in [db.py](../database/db.py). The module stores task and command-history data while keeping database work off the UI and audio-processing threads.

## Database Manager and Background Thread

`DatabaseManager` owns a single SQLite connection and runs all SQL statements on a dedicated daemon thread. Each manager is initialized with a database path:

```python
manager = DatabaseManager("database/one.db")
```

The manager exposes a thread-safe **`requests`** queue. Each request contains the SQL statement, its parameters, and a `concurrent.futures.Future` belonging to the caller.

The public `execute()` method places that request in the queue and waits for its own `Future`. This means callers use a simple synchronous API even though SQLite work is performed on another thread:

```python
result = manager.execute(
    "SELECT * FROM task WHERE name = ?",
    ("make a cake",),
)
```

`SELECT` statements return `cursor.fetchall()` results. Write statements such as `CREATE`, `INSERT`, `UPDATE`, and `DELETE` are committed and return `True`.

SQLite errors are rolled back by the worker and propagated to the original caller as `DatabaseError`; they are not represented as a successful-looking `False` result. If the worker cannot start, a request exceeds the waiting limit, or shutdown does not finish in time, the manager raises `DatabaseTimeoutError`. If the worker fails unexpectedly, pending requests are completed with the same `DatabaseError` so callers are not left waiting indefinitely.

## Default and Test Instances

The module creates a default application manager:

```python
db_default = get_db_manager()
```

Domain helper functions use this instance unless another manager is explicitly supplied. For example:

```python
create_task("make a cake", deadline)
```

uses `db_default`, while tests should create and pass their own isolated manager:

```python
test_db = get_db_manager("tests/db/test_database.db")
create_table(test_db)
create_task("make a cake", None, db=test_db)
```

Using a separate database file prevents tests from creating, updating, or deleting data in `database/one.db`.

## Connection Lifecycle

The worker owns the SQLite connection, so it is also responsible for opening and closing it. `DatabaseManager` waits for a startup `Future` before accepting normal work, ensuring that initialization failures are reported early. Calling:

```python
manager.close()
```

places a shutdown signal (`None`) in the request queue and waits for the worker thread to finish. The worker then closes its SQLite connection in a `finally` block.

The default manager is additionally registered with `atexit`:

```python
atexit.register(db_default.close)
```

This closes the default connection during a normal Python shutdown. Test managers should still be closed explicitly, usually in `unittest.TestCase.tearDown()`:

```python
def tearDown(self) -> None:
    if self.db is not None:
        self.db.close()
```

## Schema Initialization

`create_table()` creates the required tables for the selected manager. Call it after creating a custom manager, especially in tests.

### `history`

| Column | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Auto-incremented primary key. |
| `intent` | `TEXT` | Intent that was executed. |
| `target` | `TEXT` | Target associated with the command. |

### `task`

| Column | Type | Description |
| --- | --- | --- |
| `id` | `INTEGER` | Auto-incremented primary key. |
| `name` | `TEXT` | Task title. |
| `time_remaining` | `TEXT` | Optional deadline stored in ISO-like `YYYY-MM-DD HH:MM` format. |
| `status` | `TEXT` | Task lifecycle state. Defaults to `pending`. |
| `description` | `TEXT` | Optional task details. |

The schema limits task statuses to the following values:

```text
pending
finished
in progress
```

## Task Operations

The module provides helpers for common task operations:

| Function | Purpose |
| --- | --- |
| `create_task()` | Inserts a task. |
| `delete_task()` | Deletes a task only when `verify_task()` confirms it exists. |
| `verify_task()` | Returns whether a task with the supplied name exists. |
| `view_tasks()` | Prints every task row in the selected database. |
| `view_single_task()` | Prints one task, or reports that it was not found. |
| `update_task_name()` | Changes a task name. |
| `update_task_time()` | Changes a task deadline. |
| `update_task_status()` | Changes a task status. |
| `update_task_description()` | Changes a task description. |

`create_task()` and `update_task_time()` accept a Python `datetime` value or `None`. When a deadline exists, it is normalized before persistence:

```python
deadline.strftime("%Y-%m-%d %H:%M")
```

This preserves the date and minute while intentionally omitting seconds.

## Error Handling

Callers that execute database operations should allow database failures to propagate or catch the relevant domain error when they can provide useful recovery feedback:

| Error | Meaning |
| --- | --- |
| `DatabaseError` | The SQLite request failed, the manager was closed, or the worker is unavailable. |
| `DatabaseTimeoutError` | The worker did not start, complete a request, or stop within its timeout. |
| `TaskNotFoundError` | `view_single_task()` was requested for a task that does not exist. |
| `HistoryQueryError` | A history query could not be completed. |

The worker rolls back a failed SQLite operation before returning the error, preserving the connection for later requests whenever possible.

## History Operations

Executed commands can be stored with:

```python
history_insert(intent, target)
```

Use `history_query()` to print all saved history rows. Both functions accept an optional `db` argument, allowing tests to use an isolated manager instead of the default database.

## Testing Notes

Database tests should be independent. Do not rely on a task created in one test method being available in another, because a typical `setUp()` creates a clean database for every test.

For a delete test, create the task inside the same test, verify that it exists, delete it, and then verify that it no longer exists:

```python
create_task("make a coffee", None, db=test_db)
assert verify_task("make a coffee", test_db)

delete_task("make a coffee", test_db)
assert not verify_task("make a coffee", test_db)
```
