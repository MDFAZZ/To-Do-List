"""
Task service module for business logic and database operations.

This module contains all the business logic for task CRUD operations.
All database operations use raw SQL queries as per requirements (no ORM).
"""

import sqlite3
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from .database import get_db_connection

logger = logging.getLogger('tasks')


class TaskService:
    """
    Service class for managing task operations.
    
    This class provides methods for all CRUD operations on tasks,
    using raw SQL queries instead of Django ORM.
    """
    
    @staticmethod
    def create_task(title: str, description: str = None, 
                   due_date: str = None, status: str = 'pending') -> Dict:
        """
        Create a new task in the database.
        
        Args:
            title (str): Task title (required)
            description (str, optional): Task description
            due_date (str, optional): Due date in ISO format (YYYY-MM-DD)
            status (str): Task status, defaults to 'pending'
            
        Returns:
            dict: Created task data with generated ID and timestamps
            
        Raises:
            ValueError: If title is empty or status is invalid
            sqlite3.Error: If database operation fails
        """
        if not title or not title.strip():
            logger.warning("Attempted to create task with empty title")
            raise ValueError("Task title is required")
        
        if status not in ['pending', 'completed']:
            logger.warning(f"Invalid status provided: {status}")
            raise ValueError("Status must be 'pending' or 'completed'")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert new task
            insert_query = """
            INSERT INTO tasks (title, description, due_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """
            
            cursor.execute(insert_query, (title.strip(), description, due_date, status))
            task_id = cursor.lastrowid
            
            # Retrieve the created task
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
        """
        Retrieve all tasks from the database.
        
        Returns:
            list: List of task dictionaries, ordered by creation date (newest first)
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Retrieve all tasks ordered by creation date
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
        """
        Retrieve a specific task by its ID.
        
        Args:
            task_id (int): The ID of the task to retrieve
            
        Returns:
            dict: Task data if found, None otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
        """
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
        """
        Update an existing task in the database.
        
        Args:
            task_id (int): The ID of the task to update
            title (str, optional): New task title
            description (str, optional): New task description
            due_date (str, optional): New due date in ISO format
            status (str, optional): New task status
            
        Returns:
            dict: Updated task data if found, None otherwise
            
        Raises:
            ValueError: If status is invalid
            sqlite3.Error: If database operation fails
        """
        if status and status not in ['pending', 'completed']:
            logger.warning(f"Invalid status provided: {status}")
            raise ValueError("Status must be 'pending' or 'completed'")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if task exists (direct query to avoid cache issues)
            select_query = "SELECT * FROM tasks WHERE id = ?"
            cursor.execute(select_query, (task_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                logger.warning(f"Attempted to update non-existent task with ID: {task_id}")
                return None
            
            # Build dynamic update query based on provided fields
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
            
            if not update_fields:
                conn.close()
                logger.warning(f"No fields provided for update on task {task_id}")
                # Return existing task data
                return TaskService._row_to_dict(row)
            
            # Always update the updated_at timestamp
            update_fields.append("updated_at = datetime('now')")
            update_values.append(task_id)
            
            update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(update_query, update_values)
            
            conn.commit()
            conn.close()
            
            # Retrieve updated task
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
        """
        Delete a task from the database.
        
        Args:
            task_id (int): The ID of the task to delete
            
        Returns:
            bool: True if task was deleted, False if task not found
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if task exists (direct query to avoid cache issues)
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
        """
        Convert a database row to a dictionary.
        
        Args:
            row (sqlite3.Row): Database row object
            
        Returns:
            dict: Dictionary representation of the row
        """
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
