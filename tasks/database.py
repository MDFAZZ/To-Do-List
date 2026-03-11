"""
Database utility module for task management.

This module provides functions for database initialization and raw SQL operations.
Following the requirement to not use Django ORM, all database operations are
performed using raw SQL queries.
"""

import sqlite3
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger('tasks')


def get_db_connection():
    """
    Create and return a database connection.
    
    Returns:
        sqlite3.Connection: Database connection object
        
    Raises:
        sqlite3.Error: If connection cannot be established
    """
    try:
        db_path = settings.DATABASES['default']['NAME']
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        logger.debug(f"Database connection established: {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise


def initialize_database():
    """
    Initialize the database by creating the tasks table if it doesn't exist.
    
    This function creates a table with the following fields:
    - id: Primary key (auto-increment)
    - title: Task title (required)
    - description: Task description (optional)
    - due_date: Due date in ISO format (optional)
    - status: Task status (pending/completed, default: pending)
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create tasks table with all required fields
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
        
        # Create index on status for better query performance
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
