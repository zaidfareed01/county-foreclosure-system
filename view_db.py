"""
Quick script to view database contents
Run: python view_db.py
"""

import sqlite3
import json
from datetime import datetime

def view_database():
    # Connect to database
    conn = sqlite3.connect('pre_foreclosure.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    print("=" * 80)
    print("COUNTY PRE-FORECLOSURE DATABASE CONTENTS")
    print("=" * 80)

    # Get all counties
    cursor.execute("SELECT * FROM counties ORDER BY created_at DESC")
    counties = cursor.fetchall()

    print(f"\nTOTAL COUNTIES: {len(counties)}")
    print("-" * 80)

    if counties:
        for county in counties:
            print(f"\n[ID: {county['id']}]")
            print(f"   County: {county['county_name']}")
            print(f"   State: {county['state']}")
            print(f"   Contact: {county['contact_person'] or 'N/A'}")
            print(f"   Phone: {county['phone'] or 'N/A'}")
            print(f"   Email: {county['email'] or 'N/A'}")
            print(f"   Status: {county['status']}")
            print(f"   Last Request: {county['last_request_sent'] or 'Never'}")
            print(f"   Created: {county['created_at']}")
            if county['notes']:
                print(f"   Notes: {county['notes']}")
    else:
        print("\n   No counties in database yet.")

    # Count other tables
    print("\n" + "=" * 80)
    print("OTHER TABLES:")
    print("-" * 80)

    tables = ['payment_info', 'addresses', 'email_log', 'received_files']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        print(f"   {table}: {count} records")

    print("\n" + "=" * 80)

    conn.close()

if __name__ == "__main__":
    try:
        view_database()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure 'pre_foreclosure.db' exists in the current directory.")
        print("Run 'python main.py' first to create the database.")
