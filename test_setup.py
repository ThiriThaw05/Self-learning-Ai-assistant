import os
from dotenv import load_dotenv

load_dotenv()

print("Checking environment variables...")

# Check LLM keys
llm_keys = {
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
}

for name, key in llm_keys.items():
    status = "✅ Set" if key else "❌ Not set"
    print(f"  {name}: {status}")

# Check DB
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
print(f"  SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Not set'}")
print(f"  SUPABASE_KEY: {'✅ Set' if supabase_key else '❌ Not set'}")

print("\nAt least one LLM key is required!")