from flask import Blueprint, request, jsonify
from app.services.prompt_editor import get_prompt_editor

generate_bp = Blueprint('generate', __name__)


def format_history_from_request(chat_history: list) -> str:
    """Convert API chat history format to string format for prompts."""
    if not chat_history:
        return "No previous messages."
    
    formatted = []
    for msg in chat_history:
        role = msg.get('role', 'unknown').upper()
        message = msg.get('message', '')
        formatted.append(f"[{role}]: {message}")
    
    return "\n".join(formatted)


@generate_bp.route('/generate-reply', methods=['POST'])
def generate_reply():
    """
    Generate an AI response based on conversation context.
    
    Request Body:
    {
        "clientSequence": "I'm American and currently in Bali. Can I apply from Indonesia?",
        "chatHistory": [
            {"role": "consultant", "message": "Hi there! Thank you for reaching out..."},
            {"role": "client", "message": "Hello, I'm interested in the DTV visa..."}
        ]
    }
    
    Response:
    {
        "aiReply": "Great news! As a US citizen, you can apply..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        client_sequence = data.get('clientSequence', '')
        chat_history = data.get('chatHistory', [])
        
        if not client_sequence:
            return jsonify({"error": "clientSequence is required"}), 400
        
        # Format chat history
        history_text = format_history_from_request(chat_history)
        
        # Generate reply using prompt editor service
        editor = get_prompt_editor()
        ai_reply = editor.generate_reply(
            client_message=client_sequence,
            chat_history=history_text
        )
        
        return jsonify({"aiReply": ai_reply})
    
    except Exception as e:
        print(f"❌ Error in /generate-reply: {e}")
        return jsonify({"error": str(e)}), 500
