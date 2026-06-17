"""API contract and validation tests - Phase 7A Lane 2.3"""

import pytest
from pydantic import BaseModel, ValidationError
from typing import Optional, List


class UserModel(BaseModel):
    """User data model"""
    id: int
    name: str
    email: str
    active: bool = True


class TestAPIContracts:
    """API contract tests"""
    
    def test_user_model_valid(self):
        """Test user model with valid data"""
        user = UserModel(id=1, name="John", email="john@example.com")
        assert user.id == 1
        assert user.name == "John"
    
    def test_user_model_with_defaults(self):
        """Test user model uses defaults"""
        user = UserModel(id=1, name="John", email="john@example.com")
        assert user.active is True
