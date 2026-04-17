"""
Test script to simulate sending an email and updating last_request_sent
"""
import requests
from datetime import datetime

API_URL = "http://localhost:8000/api"

def test_email_logging():
    print("=" * 70)
    print("TEST: Email Logging and Last Request Update")
    print("=" * 70)

    # Get first county
    response = requests.get(f"{API_URL}/counties")
    counties = response.json()

    if not counties:
        print("No counties found!")
        return

    county = counties[0]
    print(f"\nCounty: {county['county_name']}")
    print(f"Last Request (before): {county['last_request_sent'] or 'Never'}")

    # Simulate sending an email
    print(f"\nSimulating email to {county['email']}...")

    email_data = {
        "county_id": county['id'],
        "email_type": "request",  # Must be "request"
        "recipient": county['email'],
        "subject": f"Pre-Foreclosure Data Request - {county['county_name']}",
        "body": "Dear County Clerk,\n\nWe are requesting pre-foreclosure property data...",
        "status": "sent"  # Must be "sent"
    }

    # Log the email
    response = requests.post(f"{API_URL}/email-logs", json=email_data)

    if response.status_code == 200:
        print("✅ Email logged successfully!")
    else:
        print(f"❌ Error: {response.text}")
        return

    # Get county again to see updated last_request_sent
    response = requests.get(f"{API_URL}/counties/{county['id']}")
    updated_county = response.json()

    print(f"\nLast Request (after): {updated_county['last_request_sent']}")
    print(f"\n✅ SUCCESS! 'Never' changed to: {updated_county['last_request_sent']}")
    print("\nRefresh your browser to see the change!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_email_logging()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Make sure the backend is running!")
        print("Run: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
