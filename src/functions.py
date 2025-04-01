import secrets
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import time
import json
from dotenv import load_dotenv

# Connect to MongoDB
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def generate_api_key(user_email, role):
    # STUB CODE, REPLACE WITH ACTUAL KEY GENERATION LOGIC
    try:
        #auth_data = {}
        #auth_data['email'] = user_email

        api_key = secrets.token_urlsafe(16)
        #auth_data['key'] = api_key

        #auth_data['role'] = role
        #auth_data['allowed'] = ['retrieval', 'analytical']

        exp = int(time.time())
        #auth_data['exp'] = exp

        auth_object = {
            "email": user_email,
            "key": api_key,
            "role": role,
            "allowed": ["retrieval", "analytical"],
            "exp": exp
        }

        #auth_object = json.dumps(auth_data)
        save_api_key(auth_object)

        return True

    except:
        return False

def save_api_key(auth_object):
    # STUB CODE, REPLACE WITH ACTUAL SAVING LOGIC
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    db = client['auth_db']
    collection = db['auth_objects']

    collection.insert_many(auth_object)

    client.close()

    return True


""" def validate_api_key(api_key):
    # STUB CODE, REPLACE WITH ACTUAL VALIDATION LOGIC
    
    key_data = api_keys_collection.find_one({"api_key": api_key})

    if not key_data:
        return {"valid": False, "message": "Invalid API key"}

    if datetime.utcnow() > datetime.fromisoformat(key_data["expires_at"]):
        return {"valid": False, "message": "API key expired"}

    return {"valid": True, "email": key_data["email"], "allowed_apis": key_data["allowed_apis"]}
 """

auth_obj = generate_api_key("user@gmail.com", "user")
save_api_key(auth_obj)