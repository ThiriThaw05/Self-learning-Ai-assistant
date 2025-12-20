import os
from typing import Optional

# Use requests directly to avoid Supabase SDK version issues
import requests


class DatabaseService:
    """
    Database service for managing prompts in Supabase.
    Uses REST API directly for maximum compatibility.
    """
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
        
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.rest_url = f"{self.url}/rest/v1"
        print("✅ Database service initialized")
    
    def get_prompt(self, name: str = "chatbot_prompt") -> Optional[str]:
        """Retrieve a prompt from the database by name."""
        try:
            url = f"{self.rest_url}/prompts?name=eq.{name}&select=content"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return data[0].get("content")
            return None
            
        except Exception as e:
            print(f"❌ DB Error getting prompt '{name}': {e}")
            return None
    
    def update_prompt(self, name: str, content: str) -> bool:
        """Update an existing prompt in the database."""
        try:
            url = f"{self.rest_url}/prompts?name=eq.{name}"
            payload = {"content": content}
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            print(f"✅ Prompt '{name}' updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ DB Error updating prompt '{name}': {e}")
            return False
    
    def create_prompt(self, name: str, content: str) -> bool:
        """Create a new prompt in the database."""
        try:
            url = f"{self.rest_url}/prompts"
            payload = {"name": name, "content": content}
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            print(f"✅ Prompt '{name}' created successfully")
            return True
            
        except Exception as e:
            print(f"❌ DB Error creating prompt '{name}': {e}")
            return False
    
    def get_or_create_prompt(self, name: str, default_content: str) -> str:
        """Get a prompt, or create it with default content if it doesn't exist."""
        existing = self.get_prompt(name)
        if existing:
            return existing
        
        self.create_prompt(name, default_content)
        return default_content


# Singleton instance
_db_instance: Optional[DatabaseService] = None

def get_db_service() -> DatabaseService:
    """Get or create database service instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseService()
    return _db_instance
