"""
Quick script to check which database is currently in use
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pre_foreclosure.db")

print("=" * 60)
print("CURRENT DATABASE CONFIGURATION")
print("=" * 60)
print(f"\nDATABASE_URL: {DATABASE_URL}")

if DATABASE_URL.startswith("sqlite"):
    print("\nDatabase Type: SQLite")
    print("Storage: Local file")
    print("File location: pre_foreclosure.db")
    print("Status: DEVELOPMENT MODE")
elif DATABASE_URL.startswith("postgres"):
    print("\nDatabase Type: PostgreSQL")
    print("Storage: Cloud database")
    print("Status: PRODUCTION MODE")
else:
    print("\nDatabase Type: Unknown")

print("\n" + "=" * 60)
