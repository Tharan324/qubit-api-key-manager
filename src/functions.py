import secrets
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/api_db")
client = MongoClient(MONGO_URI)
db = client.api_db  # Database name
api_keys_collection = db.api_keys  # Collection name

def generate_api_key():
    # STUB CODE, REPLACE WITH ACTUAL KEY GENERATION LOGIC
    """Generates a secure API key."""
    return secrets.token_hex(32)

def save_api_key(email):
    # STUB CODE, REPLACE WITH ACTUAL SAVING LOGIC
    """Generates and stores an API key for a given email."""
    api_key = generate_api_key()
    expires_at = datetime.utcnow() + timedelta(days=30)  # 30-day expiration

    key_data = {
        "email": email,
        "api_key": api_key,
        "allowed_apis": [],  # Empty list, can be updated later
        "expires_at": expires_at.isoformat()
    }

    api_keys_collection.insert_one(key_data)  # Save to MongoDB
    return key_data

def validate_api_key(api_key):
    # STUB CODE, REPLACE WITH ACTUAL VALIDATION LOGIC
    """Checks if an API key is valid and not expired."""
    key_data = api_keys_collection.find_one({"api_key": api_key})

    if not key_data:
        return {"valid": False, "message": "Invalid API key"}

    if datetime.utcnow() > datetime.fromisoformat(key_data["expires_at"]):
        return {"valid": False, "message": "API key expired"}

    return {"valid": True, "email": key_data["email"], "allowed_apis": key_data["allowed_apis"]}

