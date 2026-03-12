# Database utilities - handling all the raw SQL stuff
# Not using Django ORM as per requirements, so everything is manual SQL queries

import sqlite3
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger('tasks')


def get_db_connection():
    # Get a connection to the SQLite database
    # Using row_factory so we can access columns by name instead of index
    try:
        db_path = settings.DATABASES['default']['NAME']
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Makes life easier when reading results
        logger.debug(f"Database connection established: {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise


def initialize_database():
    # Creates the tasks table if it doesn't exist
    # Also adds an index on status field for faster queries
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Main table structure
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        logger.info("Database table 'tasks' initialized successfully")
        
        # Index on status helps when filtering by pending/completed
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_status 
        ON tasks(status)
        """)
        
        conn.commit()
        conn.close()
        logger.debug("Database initialization completed")
        
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise
