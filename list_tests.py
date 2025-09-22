#!/usr/bin/env python3
import requests
import json

BACKEND_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

session = requests.Session()

# Login
response = session.post(f"{BACKEND_URL}/auth/login", json={
    "username_or_email": ADMIN_EMAIL,
    "password": ADMIN_PASSWORD
})

token = response.json()["access_token"]
session.headers.update({"Authorization": f"Bearer {token}"})

# Get all final tests
response = session.get(f"{BACKEND_URL}/final-tests")
tests = response.json()

print(f"Found {len(tests)} final tests:")
for test in tests:
    print(f"- {test['title']} (ID: {test['id']})")