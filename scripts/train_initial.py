"""
Initial Training Script for the Self-Learning AI Assistant.

This script trains the AI on all conversation samples from conversations.json.
It iteratively improves the prompt using the self-learning loop by comparing
AI predictions with real consultant replies.

Usage:
    python scripts/train_initial.py

Make sure your .env file has:
    - GOOGLE_API_KEY (or other LLM provider key)
    - SUPABASE_URL
    - SUPABASE_KEY
"""
import os
import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.utils.conversation_parser import (
    load_conversations,
    parse_conversation_pairs,
    format_client_sequence,
    format_chat_history
)
from app.services.db_service import get_db_service
from app.services.prompt_editor import get_prompt_editor
from app.prompts.base_prompts import CHATBOT_PROMPT


def initialize_prompt():
    """Initialize the chatbot prompt in database if it doesn't exist."""
    db = get_db_service()
    existing = db.get_prompt("chatbot_prompt")
    
    if not existing:
        print("📝 Initializing base prompt in database...")
        db.create_prompt("chatbot_prompt", CHATBOT_PROMPT)
        print("✅ Base prompt created!\n")
        return True
    else:
        print("✅ Prompt already exists in database\n")
        return False


def train_on_conversations(limit: int = None, delay: float = 1.0):
    """
    Train the AI on conversation samples.
    
    Args:
        limit: Maximum number of training pairs to process (None = all)
        delay: Seconds to wait between API calls (to avoid rate limits)
    """
    # Load conversations
    conversations_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'conversations.json'
    )
    
    print(f"📂 Loading conversations from: {conversations_path}")
    conversations = load_conversations(conversations_path)
    pairs = parse_conversation_pairs(conversations)
    
    if limit:
        pairs = pairs[:limit]
    
    print(f"📊 Training on {len(pairs)} conversation pairs...\n")
    print("=" * 60)
    
    # Get services
    editor = get_prompt_editor()
    
    success_count = 0
    fail_count = 0
    
    for i, pair in enumerate(pairs):
        print(f"\n[{i+1}/{len(pairs)}] 🎯 Training on: {pair['scenario'][:50]}...")
        
        # Format the data
        client_msg = format_client_sequence(pair['client_sequence'])
        history = format_chat_history(pair['chat_history'])
        consultant_reply = "\n".join(pair['consultant_reply'])
        
        try:
            # First generate a prediction
            predicted_reply = editor.generate_reply(
                client_message=client_msg,
                chat_history=history
            )
            
            print(f"   📤 Predicted: {predicted_reply[:80]}...")
            print(f"   ✓ Actual: {consultant_reply[:80]}...")
            
            # Now improve based on comparison
            result = editor.improve_from_example(
                client_message=client_msg,
                chat_history=history,
                consultant_reply=consultant_reply,
                predicted_reply=predicted_reply
            )
            
            if result.get("success"):
                changes = result.get('changes_made', 'No description')
                print(f"   ✅ Prompt improved: {changes[:100]}")
                success_count += 1
            else:
                print(f"   ⚠️ No changes made: {result.get('error', 'Unknown')[:50]}")
                fail_count += 1
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            fail_count += 1
        
        # Rate limiting delay
        if delay > 0 and i < len(pairs) - 1:
            time.sleep(delay)
    
    print("\n" + "=" * 60)
    print("\n🎉 TRAINING COMPLETE!")
    print(f"   ✅ Successful improvements: {success_count}")
    print(f"   ❌ Failed/skipped: {fail_count}")
    print(f"   📝 Final prompt saved to database")


def main():
    print("=" * 60)
    print("🤖 SELF-LEARNING AI ASSISTANT - INITIAL TRAINING")
    print("=" * 60 + "\n")
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    llm_vars = ["GOOGLE_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
    
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print(f"❌ Missing required environment variables: {missing}")
        print("Please check your .env file")
        sys.exit(1)
    
    has_llm = any(os.getenv(v) for v in llm_vars)
    if not has_llm:
        print(f"❌ No LLM API key found. Need one of: {llm_vars}")
        print("Please check your .env file")
        sys.exit(1)
    
    print("✅ Environment variables OK\n")
    
    # Initialize prompt
    initialize_prompt()
    
    # Ask user for training options
    print("Training options:")
    print("  1. Train on ALL conversation pairs (may take a while)")
    print("  2. Train on first 5 pairs (quick test)")
    print("  3. Train on first 10 pairs (medium test)")
    print("  4. Cancel")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        train_on_conversations(limit=None, delay=1.0)
    elif choice == "2":
        train_on_conversations(limit=5, delay=1.0)
    elif choice == "3":
        train_on_conversations(limit=10, delay=1.0)
    else:
        print("Training cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
