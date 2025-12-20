import os
import json
import requests
from typing import Optional

# Try to import optional LLM libraries
try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class LLMService:
    """
    Unified LLM service wrapper supporting multiple providers.
    Supports: Google (Gemini via REST), Groq (Llama/Mistral), Anthropic (Claude)
    """
    
    def __init__(self, provider: str = None):
        # Auto-detect provider based on available API keys if not specified
        if provider is None:
            provider = self._detect_provider()
        
        self.provider = provider
        self._init_client()
    
    def _detect_provider(self) -> str:
        """Auto-detect which LLM provider to use based on available API keys."""
        if os.getenv("GROQ_API_KEY"):
            return "groq"
        elif os.getenv("GOOGLE_API_KEY"):
            return "google"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        else:
            raise ValueError("No LLM API key found in environment variables")
    
    def _init_client(self):
        """Initialize the appropriate LLM client."""
        if self.provider == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            # Use REST API directly - more reliable
            self.model_name = "gemini-1.5-flash"
            
        elif self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found")
            if Groq is None:
                raise ValueError("groq package not installed")
            self.client = Groq(api_key=api_key)
            self.model_name = "llama-3.1-70b-versatile"
            
        elif self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            if Anthropic is None:
                raise ValueError("anthropic package not installed")
            self.client = Anthropic(api_key=api_key)
            self.model_name = "claude-3-sonnet-20240229"
            
        elif self.provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            self.client = OpenAI(api_key=api_key)
            self.model_name = "gpt-4o-mini"
        
        print(f"✅ LLM Service initialized with provider: {self.provider}")
    
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate a response from the LLM."""
        try:
            if self.provider == "google":
                # Use REST API directly for reliability
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
                
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": max_tokens,
                        "temperature": 0.7
                    }
                }
                
                response = requests.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            
            elif self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"❌ LLM Error ({self.provider}): {e}")
            raise
    
    def generate_json(self, prompt: str) -> dict:
        """Generate a response and parse it as JSON."""
        response = self.generate(prompt)
        
        try:
            # Try to extract JSON from response
            # Look for JSON object in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            pass
        
        # Return raw response if JSON parsing fails
        return {"error": "Failed to parse JSON", "raw_response": response}


# Singleton instance for easy import
_llm_instance: Optional[LLMService] = None

def get_llm_service(provider: str = None) -> LLMService:
    """Get or create LLM service instance."""
    global _llm_instance
    if _llm_instance is None or (provider and _llm_instance.provider != provider):
        _llm_instance = LLMService(provider=provider)
    return _llm_instance