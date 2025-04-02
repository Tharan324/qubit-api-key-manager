import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from functions import generate_api_key, save_api_key, validate_api_key

class TestAPIKeyManagement(unittest.TestCase):

    @patch("functions.MongoClient")
    def test_generate_valid_api_key(self, mock_mongo):
        """Test generating a valid API key with correct inputs."""
        mock_db = mock_mongo.return_value["auth_db"]
        mock_collection = mock_db["auth_objects"]
        mock_collection.insert_one.return_value = MagicMock()

        auth_obj = generate_api_key("validuser@gmail.com", "user")
        
        self.assertIsNotNone(auth_obj)
        self.assertIn("key", auth_obj)
        self.assertIn("email", auth_obj)
        self.assertEqual(auth_obj["role"], "user")
        self.assertEqual(auth_obj["email"], "validuser@gmail.com")
        self.assertTrue(datetime.fromisoformat(auth_obj["exp"]) > datetime.now(timezone.utc))

    @patch("functions.MongoClient")
    def test_invalid_email(self, mock_mongo):
        """Test API key generation with an invalid email."""
        invalid_emails = ["user@", "user.com", "user@gmail", "user@gmailcom", "@gmail.com"]
        for email in invalid_emails:
            auth_obj = generate_api_key(email, "user")
            self.assertFalse(auth_obj)

    @patch("functions.MongoClient")
    def test_invalid_role(self, mock_mongo):
        """Test API key generation with invalid roles."""
        invalid_roles = ["guest", "superuser", "viewer", "root", "admin123"]
        for role in invalid_roles:
            auth_obj = generate_api_key("validuser@gmail.com", role)
            self.assertFalse(auth_obj)

    @patch("functions.MongoClient")
    def test_save_api_key(self, mock_mongo):
        """Test saving a valid API key to the mock database."""
        mock_db = mock_mongo.return_value["auth_db"]
        mock_collection = mock_db["auth_objects"]
        mock_collection.insert_one.return_value = MagicMock()

        auth_obj = {
            "email": "validuser@gmail.com",
            "key": "random_generated_key",
            "role": "user",
            "allowed": ["retrieval", "analytical"],
            "exp": datetime.now(timezone.utc).isoformat()
        }
        
        result = save_api_key(auth_obj)
        self.assertTrue(result)

    @patch("functions.MongoClient")
    def test_expired_api_key(self, mock_mongo):
        """Test when the API key has expired."""
        mock_db = mock_mongo.return_value["auth_db"]
        mock_collection = mock_db["auth_objects"]
        mock_collection.find_one.return_value = {
            "email": "user@gmail.com",
            "key": "expired_key",
            "allowed": ["retrieval", "analytical"],
            "exp": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()  # Expired
        }

        result = validate_api_key("expired_key")
        self.assertFalse(result["valid"])
        self.assertEqual(result["message"], "API key expired")

    @patch("functions.MongoClient")
    def test_valid_api_key(self, mock_mongo):
        """Test when the API key has expired."""
        mock_db = mock_mongo.return_value["auth_db"]
        mock_collection = mock_db["auth_objects"]
        expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        mock_collection.find_one.return_value = {
            "email": "user@gmail.com",
            "key": "asdfghjkIUYTampo",
            "role": "user",
            "allowed": ["retrieval", "analytical"],
            "exp": expiry 
        }

        result = validate_api_key("asdfghjkIUYTampo")
        self.assertTrue(result["valid"])
        self.assertEqual(result["email"], "user@gmail.com")
        self.assertEqual(result["role"], "user")
        self.assertEqual(result["allowed"], ["retrieval", "analytical"])

if __name__ == "__main__":
    unittest.main()
