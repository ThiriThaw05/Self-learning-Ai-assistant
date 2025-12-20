"""
Script to parse conversations.json and display sample training pairs.
Run this to verify the conversation parser is working correctly.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.conversation_parser import (
    load_conversations,
    parse_conversation_pairs,
    format_client_sequence,
    format_chat_history
)


def main():
    # Path to conversations file
    conversations_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'conversations.json'
    )
    
    print(f"Loading conversations from: {conversations_path}\n")
    
    conversations = load_conversations(conversations_path)
    pairs = parse_conversation_pairs(conversations)
    
    print(f"✅ Total conversations loaded: {len(conversations)}")
    print(f"✅ Total training pairs extracted: {len(pairs)}\n")
    
    # Print first 3 samples
    num_samples = min(3, len(pairs))
    print(f"Showing {num_samples} sample training pairs:\n")
    print("=" * 60)
    
    for i, pair in enumerate(pairs[:num_samples]):
        print(f"\n=== Sample {i+1} ===")
        print(f"Scenario: {pair['scenario']}")
        print(f"Contact ID: {pair.get('contact_id', 'N/A')}")
        
        print(f"\n📥 CLIENT MESSAGE(S):")
        print("-" * 40)
        print(format_client_sequence(pair['client_sequence']))
        
        print(f"\n📤 CONSULTANT REPLY:")
        print("-" * 40)
        print("\n".join(pair['consultant_reply']))
        
        print(f"\n📜 CHAT HISTORY:")
        print("-" * 40)
        print(format_chat_history(pair['chat_history']))
        
        print("\n" + "=" * 60)
    
    # Summary statistics
    print("\n📊 SUMMARY STATISTICS:")
    print("-" * 40)
    
    scenarios = set(pair['scenario'] for pair in pairs)
    print(f"Unique scenarios: {len(scenarios)}")
    
    for scenario in list(scenarios)[:5]:
        count = sum(1 for p in pairs if p['scenario'] == scenario)
        print(f"  - {scenario[:50]}... : {count} pairs")
    
    if len(scenarios) > 5:
        print(f"  ... and {len(scenarios) - 5} more scenarios")


if __name__ == "__main__":
    main()
