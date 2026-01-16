#!/usr/bin/env python3
"""
Script to create an initial admin user for Hublievents.
Run this script to create the first admin user in the database.
"""

import sys
import os

# Add the current directory and backend directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.insert(0, current_dir)
sys.path.insert(0, backend_dir)

from database import get_db, create_tables
from models.user import User, UserRole
from auth.password import get_password_hash

def create_admin_user():
    """Create an initial admin user."""
    # Create tables first
    create_tables()

    db = next(get_db())

    try:
        # Create new admin user
        admin_user = User(
            email="admin@hublievents.com",
            full_name="System Administrator",
            phone="+91-9876543210",
            role=UserRole.SUPER_ADMIN
        )

        # Set password
        admin_user.set_password("admin123")

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("SUCCESS: Admin user created successfully!")
        print(f"Email: {admin_user.email}")
        print("Password: admin123")
        print("Role: Super Admin")
        print("\nWARNING: Please change the default password after first login!")

    except Exception as e:
        db.rollback()
        print(f"ERROR: Error creating admin user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
