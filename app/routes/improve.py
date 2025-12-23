from flask import Blueprint, request, jsonify
from app.services.prompt_editor import get_prompt_editor

improve_bp = Blueprint('improve', __name__)


def format_history_from_request(chat_history: list) -> str:
    """Convert API chat history format to string format for prompts."""
    if not chat_history:
        return "No previous messages."
    
    formatted = []
    for msg in chat_history:
        role = msg.get('role', 'unknown').upper()
        # Accept both {message: "..."} and {content: "..."}
        message = msg.get('message') if msg.get('message') is not None else msg.get('content', '')
        formatted.append(f"[{role}]: {message}")
    
    return "\n".join(formatted)


@improve_bp.route('/improve-ai', methods=['POST'])
def improve_ai():
    """
    Auto-improve the AI prompt by comparing predicted vs actual consultant reply.
    
    Request Body:
    {
        "clientSequence": "I'm American and currently in Bali. Can I apply from Indonesia?",
        "chatHistory": [
            {"role": "consultant", "message": "Hi there!..."},
            {"role": "client", "message": "Hello, I'm interested..."}
        ],
        "consultantReply": "Yes, absolutely! You can apply at the Thai Embassy in Jakarta..."
    }
    
    Response:
    {
        "predictedReply": "Great news! As a US citizen...",
        "updatedPrompt": "You are a visa consultant specializing in Thai DTV visas...",
        "changesMade": "Adjusted tone to be more casual..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Accept both camelCase and snake_case keys
        client_sequence = data.get('clientSequence') or data.get('client_message') or data.get('message', '')
        chat_history = data.get('chatHistory') or data.get('chat_history', [])
        consultant_reply = data.get('consultantReply') or data.get('consultant_reply', '')
        
        if not client_sequence:
            return jsonify({"error": "clientSequence is required"}), 400
        if not consultant_reply:
            return jsonify({"error": "consultantReply is required"}), 400
        
        # Format chat history
        history_text = format_history_from_request(chat_history)
        
        # Get prompt editor service
        editor = get_prompt_editor()
        
        # First, generate a prediction with current prompt
        predicted_reply = editor.generate_reply(
            client_message=client_sequence,
            chat_history=history_text
        )
        
        # Now improve the prompt based on the comparison
        result = editor.improve_from_example(
            client_message=client_sequence,
            chat_history=history_text,
            consultant_reply=consultant_reply,
            predicted_reply=predicted_reply
        )
        
        if result.get("success"):
            return jsonify({
                "predictedReply": predicted_reply,
                "updatedPrompt": result.get("updated_prompt", ""),
                "changesMade": result.get("changes_made", "")
            })
        else:
            return jsonify({
                "predictedReply": predicted_reply,
                "error": result.get("error", "Failed to improve prompt"),
                "rawResponse": result.get("raw_response", "")
            }), 500
    
    except Exception as e:
        print(f"❌ Error in /improve-ai: {e}")
        return jsonify({"error": str(e)}), 500


@improve_bp.route('/improve-ai-manually', methods=['POST'])
def improve_ai_manually():
    """
    Manually update the AI prompt with specific instructions.
    
    Request Body:
    {
        "instructions": "Be more concise. Always mention appointment booking proactively."
    }
    
    Response:
    {
        "updatedPrompt": "You are a visa consultant specializing in Thai DTV visas...",
        "success": true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        instructions = data.get('instructions', '')
        
        if not instructions:
            return jsonify({"error": "instructions is required"}), 400
        
        # Get prompt editor service
        editor = get_prompt_editor()
        
        # Apply manual improvements
        result = editor.improve_manually(instructions=instructions)
        
        if result.get("success"):
            return jsonify({
                "updatedPrompt": result.get("updated_prompt", ""),
                "success": True
            })
        else:
            return jsonify({
                "error": result.get("error", "Failed to improve prompt"),
                "success": False
            }), 500
    
    except Exception as e:
        print(f"❌ Error in /improve-ai-manually: {e}")
        return jsonify({"error": str(e)}), 500


@improve_bp.route('/get-prompt', methods=['GET'])
def get_current_prompt():
    """
    Get the current chatbot prompt (for debugging/viewing).
    
    Response:
    {
        "prompt": "You are a friendly immigration consultant..."
    }
    """
    try:
        editor = get_prompt_editor()
        prompt = editor.get_current_prompt()
        return jsonify({"prompt": prompt})
    
    except Exception as e:
        print(f"❌ Error in /get-prompt: {e}")
        return jsonify({"error": str(e)}), 500


@improve_bp.route('/reset-prompt', methods=['POST'])
def reset_prompt():
    """
    Reset the chatbot prompt to the default base template.
    Use this if the prompt gets corrupted or you want to start fresh.
    
    Response:
    {
        "success": true,
        "message": "Prompt reset to default template"
    }
    """
    try:
        from app.prompts.base_prompts import CHATBOT_PROMPT
        from app.services.db_service import get_db_service
        
        db = get_db_service()
        success = db.update_prompt("chatbot_prompt", CHATBOT_PROMPT)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Prompt reset to default template"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to reset prompt"
            }), 500
    
    except Exception as e:
        print(f"❌ Error in /reset-prompt: {e}")
        return jsonify({"error": str(e)}), 500
