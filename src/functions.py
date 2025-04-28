import secrets
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import re

# Connect to MongoDB
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def generate_api_key(user_email, role):
    # creating an API key for user.
    api_key = secrets.token_urlsafe(16)
    # expiry is 3 months from the time they develop the API
    expiry_date = datetime.now(timezone.utc) + relativedelta(months=3)

    if role not in ["user", "admin"]:
        return False
    
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user_email):
        return False
    
    auth_object = {
        "email": user_email,
        "key": api_key,
        "role": role,
        "allowed": ["retrieval", "analytical"],
        "exp": expiry_date.isoformat()
    }
    if save_api_key(auth_object):
        return auth_object
    return None


def save_api_key(auth_object):
    client = None
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        db = client['auth_db']
        collection = db['auth_objects']
        collection.insert_one(auth_object)
        return True
    except Exception as e:
        print(f"Error in saving the API key {e}")
        return False
    finally:
        if client:
            client.close()
        
def validate_api_key(api_key):
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    db = client['auth_db']
    api_keys_collection = db['auth_objects']
    key_data = api_keys_collection.find_one({"key": api_key})

    if not key_data:
        return {"valid": False, "message": "Invalid API key"}

    if datetime.now(timezone.utc) > datetime.fromisoformat(key_data["exp"]):
        return {"valid": False, "message": "API key expired"}

    return {"valid": True, "email": key_data["email"], "role": key_data["role"], "allowed": key_data["allowed"]}
# OAuth session management functions
def save_user_session(user_data):
    client = None
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        db = client['auth_db']
        
        # Store user in users collection with investments list
        users_collection = db['users']
        users_collection.update_one(
            {"_id": user_data['email']},  # using email as the key
            {
                "$set": {
                    "email": user_data['email'],
                    "investments": []  # list to store company investments
                    # Each investment will be an object with:
                    # {
                    #    "company_name": str,
                    #    "company_ticker": str,
                    #    "num_units": int
                    # }
                }
            },
            upsert=True  # create if doesn't exist
        )
        
        # Handle session as before
        sessions_collection = db['user_sessions']
        session_token = secrets.token_urlsafe(32)
        expiry = datetime.now(timezone.utc) + relativedelta(days=1)
        
        session_data = {
            "session_token": session_token,
            "user_data": user_data,
            "exp": expiry.isoformat()
        }
        
        sessions_collection.insert_one(session_data)
        return session_token
    except Exception as e:
        print(f"Error saving user session: {e}")
        return None
    finally:
        if client:
            client.close()

def get_user_session(session_token):
    client = None
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        db = client['auth_db']
        collection = db['user_sessions']
        
        session = collection.find_one({"session_token": session_token})
        if not session:
            return None
            
        if datetime.now(timezone.utc) > datetime.fromisoformat(session["exp"]):
            collection.delete_one({"session_token": session_token})
            return None
            
        return session["user_data"]
    except Exception as e:
        print(f"Error getting user session: {e}")
        return None
    finally:
        if client:
            client.close()

def delete_user_session(session_token):
    client = None
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        db = client['auth_db']
        collection = db['user_sessions']
        collection.delete_one({"session_token": session_token})
        return True
    except Exception as e:
        print(f"Error deleting user session: {e}")
        return False
    finally:
        if client:
            client.close()