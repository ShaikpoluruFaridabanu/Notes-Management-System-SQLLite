import sqlite3

conn = sqlite3.connect("notes.db")

with open("schema.sql") as f:
    conn.executescript(f.read())

conn.close()

print("Database and tables created successfully!")