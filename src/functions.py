import secrets
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# Connect to MongoDB
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def generate_api_key(user_email, role):
    # creating an API key for user.
    api_key = secrets.token_urlsafe(16)
    # expiry is 3 months from the time they develop the API
    exp = int(datetime.now(timezone.utc) + relativedelta(months=3).timestamp())

    auth_object = {
        "email": user_email,
        "key": api_key,
        "role": role,
        "allowed": ["retrieval", "analytical"],
        "exp": exp
    }
    if save_api_key(auth_object):
        return api_key
    return None


def save_api_key(auth_object):
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        db = client['auth_db']
        collection = db['auth_objects']
        collection.insert_many(auth_object)
        return True
    except Exception as e:
        print(f"Error in saving the API key {e}")
        return False
    finally:
        client.close()
        
def validate_api_key(api_key):
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    db = client['auth_db']
    api_keys_collection = db['auth_objects']
    key_data = api_keys_collection.find_one({"api_key": api_key})

    if not key_data:
        return {"valid": False, "message": "Invalid API key"}

    if datetime.now(timezone.utc) > datetime.fromisoformat(key_data["expires_at"]):
        return {"valid": False, "message": "API key expired"}

    return {"valid": True, "email": key_data["email"], "allowed_apis": key_data["allowed_apis"]}

# auth_obj = generate_api_key("user@gmail.com", "user")
# save_api_key(auth_obj)