import json
from typing import List, Dict, Tuple


def load_conversations(filepath: str) -> List[Dict]:
    """Load conversations from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_conversation_pairs(conversations: List[Dict]) -> List[Dict]:
    """
    Parse conversations into training pairs.
    
    Each pair contains:
    - client_sequence: List of consecutive client messages
    - consultant_reply: List of consecutive consultant messages
    - chat_history: All messages before this exchange
    - scenario: The conversation scenario/context
    
    Returns:
        List of training pair dictionaries
    """
    training_pairs = []
    
    for conv in conversations:
        messages = conv.get('conversation', [])
        scenario = conv.get('scenario', 'Unknown')
        contact_id = conv.get('contact_id', '')
        
        i = 0
        while i < len(messages):
            # Collect client sequence (consecutive "in" messages)
            client_sequence = []
            client_start = i
            
            while i < len(messages) and messages[i].get('direction') == 'in':
                client_sequence.append(messages[i].get('text', ''))
                i += 1
            
            # Collect consultant reply (consecutive "out" messages)
            consultant_reply = []
            while i < len(messages) and messages[i].get('direction') == 'out':
                consultant_reply.append(messages[i].get('text', ''))
                i += 1
            
            # Only add if we have both client message and consultant reply
            if client_sequence and consultant_reply:
                # Build chat history from messages before this exchange
                chat_history = []
                for msg in messages[:client_start]:
                    role = "client" if msg.get('direction') == 'in' else "consultant"
                    chat_history.append({
                        "role": role,
                        "message": msg.get('text', '')
                    })
                
                training_pairs.append({
                    "client_sequence": client_sequence,
                    "consultant_reply": consultant_reply,
                    "chat_history": chat_history,
                    "scenario": scenario,
                    "contact_id": contact_id
                })
    
    return training_pairs


def format_client_sequence(sequence: List[str]) -> str:
    """Format list of client messages into a single string."""
    if len(sequence) == 1:
        return sequence[0]
    return "\n".join(sequence)


def format_chat_history(history: List[Dict]) -> str:
    """Format chat history for inclusion in prompts."""
    if not history:
        return "No previous messages."
    
    formatted = []
    for msg in history:
        role = msg['role'].upper()
        formatted.append(f"[{role}]: {msg['message']}")
    
    return "\n".join(formatted)


def format_chat_history_for_api(history: List[Dict]) -> List[Dict]:
    """Format chat history for API request/response format."""
    return [
        {"role": msg["role"], "message": msg["message"]}
        for msg in history
    ]


def get_sample_training_data(filepath: str = "conversations.json", limit: int = 5) -> List[Dict]:
    """Get sample training data for testing."""
    conversations = load_conversations(filepath)
    pairs = parse_conversation_pairs(conversations)
    return pairs[:limit]


if __name__ == "__main__":
    # Test the parser
    pairs = get_sample_training_data(limit=3)
    
    print(f"Total training pairs: {len(pairs)}\n")
    
    for i, pair in enumerate(pairs):
        print(f"=== Sample {i+1} ({pair['scenario']}) ===")
        print(f"\nClient Message(s):")
        print(format_client_sequence(pair['client_sequence']))
        print(f"\nConsultant Reply:")
        print("\n".join(pair['consultant_reply']))
        print(f"\nChat History:")
        print(format_chat_history(pair['chat_history']))
        print("\n" + "="*50 + "\n")
