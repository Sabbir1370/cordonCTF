#!/usr/bin/env python3
"""One-time script to create the initial admin user."""
import getpass
import sys
import os

# Add the project root (parent directory of scripts/) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.auth import hash_password
from backend.database import get_connection

def main():
    print("CordonCTF – First Admin Setup")
    print("-----------------------------")

    conn = get_connection()
    cursor = conn.cursor()

    # Check if any admin already exists
    cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'admin'")
    if cursor.fetchone()["cnt"] > 0:
        print("An admin already exists. This script is intended for initial setup only.")
        conn.close()
        sys.exit(1)

    username = input("Enter admin username: ").strip()
    if not username:
        print("Username cannot be empty.")
        conn.close()
        sys.exit(1)

    password = getpass.getpass("Enter admin password: ")
    if not password:
        print("Password cannot be empty.")
        conn.close()
        sys.exit(1)

    password_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'admin')",
        (username, password_hash)
    )
    conn.commit()
    print(f"Admin user '{username}' created successfully.")
    conn.close()

if __name__ == "__main__":
    main()