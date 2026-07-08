"""Database query module with SQL injection protection - SECURE VERSION."""

import sqlite3
from typing import List, Dict, Any


class UserQueryExecutor:
    """Executes user queries against the database - SECURE WITH PARAMETERIZED QUERIES."""

    def __init__(self, db_path: str):
        """Initialize with database path.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        # Enable row factory to return dictionaries
        self.conn.row_factory = sqlite3.Row

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email - SECURE WITH PARAMETERIZED QUERY.

        Uses parameterized queries (?) to prevent SQL injection.
        Untrusted user input is separated from SQL code.

        Args:
            email: User email address (untrusted input)

        Returns:
            User data dictionary
        """
        # SECURE: Parameterized query with ? placeholder
        query = "SELECT * FROM users WHERE email = ?"
        cursor = self.conn.cursor()
        # Email is passed as a separate parameter, not in the SQL string
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return dict(result) if result else {}

    def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """Search users by name - SECURE WITH PARAMETERIZED QUERY.

        Uses parameterized query to prevent SQL injection.
        Pattern matching is safely applied to the parameter value.

        Args:
            search_term: Search term (untrusted input)

        Returns:
            List of matching user dictionaries
        """
        # SECURE: Parameterized query with pattern matching
        # The % wildcards are part of the parameter value, not the SQL query
        query = "SELECT * FROM users WHERE name LIKE ?"
        cursor = self.conn.cursor()
        # Search term is safely passed as parameter
        cursor.execute(query, (f"%{search_term}%",))
        results = cursor.fetchall()
        return [dict(row) for row in results]

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID - SECURE WITH PARAMETERIZED QUERY.

        Uses parameterized query to prevent SQL injection.
        User ID is properly typed as integer.

        Args:
            user_id: User ID (should be validated as integer before calling)

        Returns:
            True if user was deleted

        Raises:
            ValueError: If user_id is not a valid integer
        """
        # Validate input type
        if not isinstance(user_id, int):
            raise ValueError(f"user_id must be an integer, got {type(user_id)}")

        # SECURE: Parameterized query prevents SQL injection
        query = "DELETE FROM users WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user with arbitrary fields - SECURE WITH PARAMETERIZED QUERY.

        Uses parameterized queries for dynamic field updates.
        Carefully constructed to prevent SQL injection.

        Args:
            user_id: User ID (should be validated as integer)
            **kwargs: Field names and values to update

        Returns:
            True if user was updated

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate input type
        if not isinstance(user_id, int):
            raise ValueError(f"user_id must be an integer, got {type(user_id)}")

        # Validate field names to prevent SQL injection through field names
        allowed_fields = {"name", "email", "phone", "bio"}
        for field in kwargs.keys():
            if field not in allowed_fields:
                raise ValueError(f"Field '{field}' not allowed for update")

        if not kwargs:
            return False

        # Build query with parameterized fields
        set_clauses = [f"{field} = ?" for field in kwargs.keys()]
        set_string = ", ".join(set_clauses)
        query = f"UPDATE users SET {set_string} WHERE id = ?"

        # Prepare values with user_id at the end
        values = list(kwargs.values()) + [user_id]

        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.rowcount > 0

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.conn.close()


# Example usage with context manager (recommended):
# with UserQueryExecutor("database.db") as executor:
#     user = executor.get_user_by_email("user@example.com")
#     results = executor.search_users("john")
#     executor.delete_user(123)
