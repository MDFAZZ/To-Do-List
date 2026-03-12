# Business logic layer for task operations
# All the CRUD stuff happens here, using raw SQL (no ORM)

import sqlite3
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from .database import get_db_connection

logger = logging.getLogger('tasks')


class TaskService:
    # Handles all task operations - create, read, update, delete
    # Everything uses raw SQL queries
    
    @staticmethod
    def create_task(title: str, description: str = None, 
                   due_date: str = None, status: str = 'pending') -> Dict:
        # Creates a new task in the database
        # Validates title and status before inserting
        if not title or not title.strip():
            logger.warning("Attempted to create task with empty title")
            raise ValueError("Task title is required")
        
        if status not in ['pending', 'completed']:
            logger.warning(f"Invalid status provided: {status}")
            raise ValueError("Status must be 'pending' or 'completed'")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert the new task
            insert_query = """
            INSERT INTO tasks (title, description, due_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """
            
            cursor.execute(insert_query, (title.strip(), description, due_date, status))
            task_id = cursor.lastrowid
            
            # Fetch it back to return the complete task with timestamps
            select_query = "SELECT * FROM tasks WHERE id = ?"
            cursor.execute(select_query, (task_id,))
            row = cursor.fetchone()
            
            conn.commit()
            conn.close()
            
            task = TaskService._row_to_dict(row)
            
            logger.info(f"Task created successfully with ID: {task_id}")
            return task
            
        except sqlite3.Error as e:
            logger.error(f"Database error while creating task: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating task: {str(e)}")
            raise
    
    @staticmethod
    def get_all_tasks() -> List[Dict]:
        # Gets all tasks, newest first
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Order by created_at DESC so newest tasks appear first
            select_query = """
            SELECT * FROM tasks 
            ORDER BY created_at DESC
            """
            
            cursor.execute(select_query)
            rows = cursor.fetchall()
            conn.close()
            
            tasks = [TaskService._row_to_dict(row) for row in rows]
            logger.debug(f"Retrieved {len(tasks)} tasks from database")
            return tasks
            
        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving tasks: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while retrieving tasks: {str(e)}")
            raise
    
    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Dict]:
        # Gets a single task by ID, returns None if not found
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            select_query = "SELECT * FROM tasks WHERE id = ?"
            cursor.execute(select_query, (task_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                task = TaskService._row_to_dict(row)
                logger.debug(f"Retrieved task with ID: {task_id}")
                return task
            else:
                logger.warning(f"Task with ID {task_id} not found")
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving task {task_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while retrieving task {task_id}: {str(e)}")
            raise
    
    @staticmethod
    def update_task(task_id: int, title: str = None, description: str = None,
                   due_date: str = None, status: str = None) -> Optional[Dict]:
        # Updates a task - only updates fields that are provided (partial updates)
        # Returns None if task doesn't exist
        if status and status not in ['pending', 'completed']:
            logger.warning(f"Invalid status provided: {status}")
            raise ValueError("Status must be 'pending' or 'completed'")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if task exists first
            select_query = "SELECT * FROM tasks WHERE id = ?"
            cursor.execute(select_query, (task_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                logger.warning(f"Attempted to update non-existent task with ID: {task_id}")
                return None
            
            # Build the UPDATE query dynamically based on what fields were provided
            update_fields = []
            update_values = []
            
            if title is not None:
                if not title.strip():
                    raise ValueError("Task title cannot be empty")
                update_fields.append("title = ?")
                update_values.append(title.strip())
            
            if description is not None:
                update_fields.append("description = ?")
                update_values.append(description)
            
            if due_date is not None:
                update_fields.append("due_date = ?")
                update_values.append(due_date)
            
            if status is not None:
                update_fields.append("status = ?")
                update_values.append(status)
            
            # If nothing to update, just return the existing task
            if not update_fields:
                conn.close()
                logger.warning(f"No fields provided for update on task {task_id}")
                return TaskService._row_to_dict(row)
            
            # Always bump the updated_at timestamp
            update_fields.append("updated_at = datetime('now')")
            update_values.append(task_id)
            
            update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(update_query, update_values)
            
            conn.commit()
            conn.close()
            
            # Fetch the updated task to return
            updated_task = TaskService.get_task_by_id(task_id)
            logger.info(f"Task {task_id} updated successfully")
            return updated_task
            
        except sqlite3.Error as e:
            logger.error(f"Database error while updating task {task_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while updating task {task_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_task(task_id: int) -> bool:
        # Deletes a task, returns False if it doesn't exist
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if it exists first
            select_query = "SELECT * FROM tasks WHERE id = ?"
            cursor.execute(select_query, (task_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                logger.warning(f"Attempted to delete non-existent task with ID: {task_id}")
                return False
            
            delete_query = "DELETE FROM tasks WHERE id = ?"
            cursor.execute(delete_query, (task_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Task {task_id} deleted successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Database error while deleting task {task_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while deleting task {task_id}: {str(e)}")
            raise
    
    
    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict:
        # Helper to convert SQLite row objects to plain dictionaries
        # Makes it easier to work with the data
        if row is None:
            return None
        
        return {
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'due_date': row['due_date'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
