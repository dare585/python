import sqlite3
from datetime import datetime

from flask import current_app


DB_CONN = None

def get_db():
    """
    Returns a database connection
    """
    global DB_CONN
    if DB_CONN is None:
        DB_CONN = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False
        )
        DB_CONN.row_factory = sqlite3.Row

    return DB_CONN


def init_db():
    """
    Initialize the database, i.e
    creates the database and table from schema.sql
    """
    db = get_db()

    with current_app.open_resource('db/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        db.commit()


# tells Python how to interpret timestamp values in the database
# We convert the value to a datetime.datetime.
sqlite3.register_converter(
    "timestamp", lambda v: datetime.strptime(v.decode(), '%Y-%m-%dT%H:%M:%SZ')
)
