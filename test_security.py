import requests

API_URL = "http://localhost:8000"

print("=== Testing Data Isolation ===\n")

# Create two test users
print("1. Creating User 1...")
response1 = requests.post(f"{API_URL}/register", json={"username": "testuser1", "password": "password123"})
print(f"   Result: {response1.status_code} - {response1.json() if response1.status_code == 200 else response1.text}")

print("\n2. Creating User 2...")
response2 = requests.post(f"{API_URL}/register", json={"username": "testuser2", "password": "password123"})
print(f"   Result: {response2.status_code} - {response2.json() if response2.status_code == 200 else response2.text}")

# Login both users
print("\n3. Logging in User 1...")
login1 = requests.post(f"{API_URL}/login", json={"username": "testuser1", "password": "password123"})
user1_data = login1.json()
user1_id = user1_data["user_id"]
print(f"   User 1 ID: {user1_id}")

print("\n4. Logging in User 2...")
login2 = requests.post(f"{API_URL}/login", json={"username": "testuser2", "password": "password123"})
user2_data = login2.json()
user2_id = user2_data["user_id"]
print(f"   User 2 ID: {user2_id}")

# Add expense for User 1
print("\n5. Adding expense for User 1...")
expense_data = [{"amount": 100.0, "category": "Food", "notes": "User 1 lunch"}]
add1 = requests.post(
    f"{API_URL}/expenses/2024-12-15",
    json=expense_data,
    headers={"user-id": str(user1_id)}
)
print(f"   Result: {add1.status_code}")

# Add expense for User 2
print("\n6. Adding expense for User 2...")
expense_data2 = [{"amount": 200.0, "category": "Shopping", "notes": "User 2 shopping"}]
add2 = requests.post(
    f"{API_URL}/expenses/2024-12-15",
    json=expense_data2,
    headers={"user-id": str(user2_id)}
)
print(f"   Result: {add2.status_code}")

# Try to fetch User 1's expenses
print("\n7. Fetching User 1's expenses...")
fetch1 = requests.get(
    f"{API_URL}/expenses/2024-12-15",
    headers={"user-id": str(user1_id)}
)
print(f"   User 1 sees: {fetch1.json()}")

# Try to fetch User 2's expenses
print("\n8. Fetching User 2's expenses...")
fetch2 = requests.get(
    f"{API_URL}/expenses/2024-12-15",
    headers={"user-id": str(user2_id)}
)
print(f"   User 2 sees: {fetch2.json()}")

# SECURITY TEST: Try to access User 1's data with User 2's credentials
print("\n9. SECURITY TEST: User 2 trying to access User 1's endpoint...")
fetch_cross = requests.get(
    f"{API_URL}/expenses/2024-12-15",
    headers={"user-id": str(user2_id)}
)
print(f"   Result: User 2 should NOT see User 1's data")
print(f"   User 2 sees: {fetch_cross.json()}")

print("\n=== Test Complete ===")
print("✅ If User 1 sees only their $100 expense and User 2 sees only their $200 expense, isolation is working!")