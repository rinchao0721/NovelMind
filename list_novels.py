import sqlite3
import os

db_path = os.path.expanduser("~/.novelmind/novelmind.db")
print(f"Checking database at: {db_path}")

if not os.path.exists(db_path):
    print("Database file not found!")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='novels';")
    if not cursor.fetchone():
        print("Table 'novels' does not exist.")
        exit(0)

    cursor.execute("SELECT id, title FROM novels")
    novels = cursor.fetchall()
    
    if not novels:
        print("No novels found in the database.")
    else:
        print(f"Found {len(novels)} novels:")
        for novel_id, title in novels:
            print(f"ID: {novel_id}, Title: {title}")
            
    conn.close()

except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
