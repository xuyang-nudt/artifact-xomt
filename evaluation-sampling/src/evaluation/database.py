import commands
import sqlite3
from filelock import Timeout, FileLock



def connect_database(db_file, db_lock=None):
    if db_lock is not None:
        lock = FileLock(db_lock)
        lock.acquire()
    # print("[add by yx] connecting database")
    conn = sqlite3.connect(db_file)
    # print("[add by yx] connected to database")
    if db_lock is not None:
        lock.release()
    return conn

def create_tables(db_file, db_lock=None):
    if db_lock is not None:
        lock = FileLock(db_lock)
        lock.acquire()

    conn = connect_database(db_file, db_lock=None)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `command` (
            `tag` TEXT NOT NULL,
            `id` INT NOT NULL,
            `file` TEXT NOT NULL,
            `sort` TEXT NOT NULL,
            `time_taken` INT NOT NULL,
            `returncode` INT NOT NULL,
            `cmd` TEXT NOT NULL,
            `stdout` TEXT NOT NULL,
            `stderr` TEXT NOT NULL,
            PRIMARY KEY (`tag`,`id`,`file`,`sort`)
        );
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `solving` (
            `tag` TEXT NOT NULL,
            `id` INT NOT NULL,
            `file` TEXT NOT NULL,
            `sort` TEXT NOT NULL,
            `status` TEXT NOT NULL,
            `obj_sign` INT,
            `obj_v` TEXT,
            `solving_time` REAL,
            PRIMARY KEY (`tag`,`id`,`file`,`sort`)
        );     
                   ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `extra_metrics` (
            `tag` TEXT NOT NULL,
            `id` INT NOT NULL,
            `file` TEXT NOT NULL,
            `sort` TEXT NOT NULL,
            `metric_key`,
            `metric_value`
        );
    ''')
    conn.commit()
    conn.close()
    if db_lock is not None:
        lock.release()

def save_command(db_file, command, tag, id, file, sort, db_lock=None):
    if db_lock is not None:
        lock = FileLock(db_lock)
        lock.acquire()
    conn = connect_database(db_file, db_lock=None)
    row = (tag, id, file, sort, command.get_time(), command.get_return_code(), command.get_command(), command.get_stdout(), command.get_stderr())
    conn.execute("""
            INSERT INTO command (tag, id, file, sort, time_taken, returncode, cmd, stdout, stderr)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                row)
    conn.commit()
    conn.close()
    if db_lock is not None:
        lock.release()

def save_metric(db_file, tag, id, file, sort, metric_key, metric_value, db_lock=None):
    if db_lock is not None:
        lock = FileLock(db_lock)
        lock.acquire()
    # print("[add by yx] save_metric: ", tag, id, file, sort, metric_key, metric_value)
    conn = connect_database(db_file, db_lock=None)
    row = (tag, id, file, sort, metric_key, metric_value)
    conn.execute("""
            INSERT INTO extra_metrics (tag, id, file, sort, metric_key, metric_value)
                 VALUES (?, ?, ?, ?, ?, ?);""",
                row)
    conn.commit()
    conn.close()
    if db_lock is not None:
        lock.release()

def save_solving(db_file, tag, id, file_path, tool, status, obj_sign, obj_v, solving_time, db_lock):
    if db_lock is not None:
        lock = FileLock(db_lock)
        lock.acquire()

    print("[add by yx] save_solving: ", tag, id, file_path, tool, status, obj_sign, obj_v, solving_time)
    conn = connect_database(db_file, db_lock=None)
    row = (tag, id, file_path, tool, status, obj_sign, obj_v, solving_time)
    conn.execute("""
            INSERT INTO solving (tag, id, file, sort, status, obj_sign, obj_v, solving_time)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                row)
    conn.commit()
    conn.close()
    if db_lock is not None:
        lock.release()