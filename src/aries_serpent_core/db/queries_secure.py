"""
Secure database query module with SQL injection protection.

This module demonstrates proper SQL parameterization techniques to prevent
SQL injection vulnerabilities (CWE-89).
"""

import sqlite3
from typing import Any, Dict, List


class SecureUserQueryExecutor:
    """
    Executes user queries against database with SQL injection prevention.
    
    SECURITY: Uses parameterized queries (prepared statements) to ensure
    untrusted user input cannot modify the SQL command structure.
    """

    def __init__(self, db_path: str):
        """Initialize with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """
        Get user by ID - SECURE WITH PARAMETERIZED QUERY.
        
        ✅ VULNERABILITY FIXED: CWE-89 SQL Injection
        
        Previous vulnerable code:
            query = f"SELECT * FROM users WHERE id = {user_id}"
            cursor.execute(query)  # ❌ UNSAFE
        
        Secure implementation:
            query = "SELECT * FROM users WHERE id = ?"
            cursor.execute(query, (user_id,))  # ✅ SAFE
        
        The key is separating SQL structure from data:
        - SQL code: "SELECT * FROM users WHERE id = ?"
        - Data parameter: (user_id,)
        - Database driver handles escaping automatically
        
        Args:
            user_id: User ID (integer, validated)
            
        Returns:
            Dictionary with user data or empty dict if not found
            
        Raises:
            TypeError: If user_id is not an integer
            sqlite3.Error: On database errors
        """
        if not isinstance(user_id, int):
            raise TypeError(f"user_id must be int, got {type(user_id).__name__}")
        
        # SECURE: Parameterized query prevents SQL injection
        query = "SELECT * FROM users WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))  # Parameters passed separately
        result = cursor.fetchone()
        return dict(result) if result else {}

    def search_users_by_email(self, email_pattern: str) -> List[Dict[str, Any]]:
        """
        Search users by email pattern - SECURE WITH PARAMETERIZED QUERY.
        
        ✅ VULNERABILITY FIXED: CWE-89 SQL Injection
        
        Args:
            email_pattern: Email search pattern (e.g., "%.com")
            
        Returns:
            List of matching user dictionaries
        """
        # SECURE: Parameterized query with LIKE clause
        query = "SELECT * FROM users WHERE email LIKE ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (email_pattern,))  # Pattern passed as parameter
        results = cursor.fetchall()
        return [dict(row) for row in results]

    def update_user_email(self, user_id: int, new_email: str) -> bool:
        """
        Update user email - SECURE WITH PARAMETERIZED QUERY.
        
        ✅ VULNERABILITY FIXED: CWE-89 SQL Injection
        
        Args:
            user_id: User ID (integer)
            new_email: New email address
            
        Returns:
            True if user was updated
            
        Raises:
            TypeError: If user_id is not an integer
        """
        if not isinstance(user_id, int):
            raise TypeError(f"user_id must be int, got {type(user_id).__name__}")
        
        # SECURE: Both fields are parameterized
        query = "UPDATE users SET email = ? WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (new_email, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        """
        Delete user by ID - SECURE WITH PARAMETERIZED QUERY.
        
        ✅ VULNERABILITY FIXED: CWE-89 SQL Injection
        
        Args:
            user_id: User ID (integer)
            
        Returns:
            True if user was deleted
            
        Raises:
            TypeError: If user_id is not an integer
        """
        if not isinstance(user_id, int):
            raise TypeError(f"user_id must be int, got {type(user_id).__name__}")
        
        # SECURE: Parameterized query prevents injection
        query = "DELETE FROM users WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.conn.close()


# ============================================================================
# VULNERABILITY ANALYSIS: CWE-89 SQL Injection
# ============================================================================

# VULNERABLE PATTERN (❌ DO NOT USE):
# ----
# user_input = "1; DROP TABLE users;--"
# query = f"SELECT * FROM users WHERE id = {user_input}"
# cursor.execute(query)
#
# Result: The DROP TABLE command executes because it's part of the SQL string!

# SECURE PATTERN (✅ USE THIS):
# ----
# user_input = "1; DROP TABLE users;--"
# query = "SELECT * FROM users WHERE id = ?"
# cursor.execute(query, (user_input,))
#
# Result: user_input is treated as DATA, not SQL code
# The semicolon and DROP are escaped as literal characters

# KEY PRINCIPLES:
# 1. Never use string formatting for SQL queries
# 2. Always use parameterized queries (? or :name placeholders)
# 3. Pass data as separate parameters to execute()
# 4. Validate input types before execution
# 5. Use ORM libraries (SQLAlchemy) when possible
