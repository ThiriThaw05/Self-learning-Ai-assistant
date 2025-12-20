import os
from typing import Optional
from supabase import create_client, Client


class DatabaseService:
    """
    Database service for managing prompts in Supabase.
    """
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
        
        self.client: Client = create_client(url, key)
        print("✅ Database service initialized")
    
    def get_prompt(self, name: str = "chatbot_prompt") -> Optional[str]:
        """Retrieve a prompt from the database by name."""
        try:
            response = self.client.table("prompts") \
                .select("content") \
                .eq("name", name) \
                .single() \
                .execute()
            
            if response.data:
                return response.data.get("content")
            return None
            
        except Exception as e:
            print(f"❌ DB Error getting prompt '{name}': {e}")
            return None
    
    def update_prompt(self, name: str, content: str) -> bool:
        """Update an existing prompt in the database."""
        try:
            self.client.table("prompts") \
                .update({
                    "content": content,
                    "updated_at": "now()"
                }) \
                .eq("name", name) \
                .execute()
            
            print(f"✅ Prompt '{name}' updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ DB Error updating prompt '{name}': {e}")
            return False
    
    def create_prompt(self, name: str, content: str) -> bool:
        """Create a new prompt in the database."""
        try:
            self.client.table("prompts") \
                .insert({
                    "name": name,
                    "content": content
                }) \
                .execute()
            
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
