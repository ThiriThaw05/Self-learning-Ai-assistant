from app.services.llm_service import get_llm_service
from app.services.db_service import get_db_service
from app.prompts.base_prompts import EDITOR_PROMPT, MANUAL_EDITOR_PROMPT, CHATBOT_PROMPT


class PromptEditorService:
    """
    Service for self-learning prompt improvement.
    Compares AI predictions with real consultant replies to refine the chatbot prompt.
    """
    
    def __init__(self, llm_provider: str = None):
        self.llm = get_llm_service(provider=llm_provider)
        self.db = get_db_service()
    
    def get_current_prompt(self) -> str:
        """Get the current chatbot prompt from database, or initialize with default."""
        prompt = self.db.get_prompt("chatbot_prompt")
        if not prompt:
            # Initialize with base prompt if not exists
            self.db.create_prompt("chatbot_prompt", CHATBOT_PROMPT)
            return CHATBOT_PROMPT
        return prompt
    
    def improve_from_example(
        self,
        client_message: str,
        chat_history: str,
        consultant_reply: str,
        predicted_reply: str
    ) -> dict:
        """
        Improve the prompt based on comparing predicted vs actual consultant reply.
        
        Args:
            client_message: The client's message
            chat_history: Formatted chat history string
            consultant_reply: What the real consultant said
            predicted_reply: What the AI predicted
            
        Returns:
            dict with success status, updated_prompt, and changes description
        """
        current_prompt = self.get_current_prompt()
        
        # Build the editor prompt
        editor_input = EDITOR_PROMPT.format(
            current_prompt=current_prompt,
            chat_history=chat_history,
            client_message=client_message,
            consultant_reply=consultant_reply,
            predicted_reply=predicted_reply
        )
        
        # Get improvement suggestions from LLM
        result = self.llm.generate_json(editor_input)
        
        if "prompt" in result and result["prompt"]:
            # Update database with new prompt
            success = self.db.update_prompt("chatbot_prompt", result["prompt"])
            
            return {
                "success": success,
                "updated_prompt": result["prompt"],
                "changes_made": result.get("changes_made", "No description provided")
            }
        
        return {
            "success": False,
            "error": result.get("error", "Failed to generate improved prompt"),
            "raw_response": result.get("raw_response", "")
        }
    
    def improve_manually(self, instructions: str) -> dict:
        """
        Improve the prompt based on manual user instructions.
        
        Args:
            instructions: Natural language instructions for how to improve the prompt
            
        Returns:
            dict with success status and updated_prompt
        """
        import re
        current_prompt = self.get_current_prompt()
        
        # Build the manual editor prompt
        editor_input = MANUAL_EDITOR_PROMPT.format(
            current_prompt=current_prompt,
            instructions=instructions
        )
        
        # Get updated prompt from LLM
        result = self.llm.generate_json(editor_input)
        
        if "prompt" in result and result["prompt"]:
            # Update database with new prompt
            success = self.db.update_prompt("chatbot_prompt", result["prompt"])
            
            return {
                "success": success,
                "updated_prompt": result["prompt"]
            }
        
        # If JSON parsing failed, try to extract prompt from raw response
        raw = result.get("raw_response", "")
        if raw:
            # Try to find a large text block that looks like a prompt
            # Look for text between "prompt": and the end
            match = re.search(r'"prompt"\s*:\s*"(.+)', raw, re.DOTALL)
            if match:
                extracted = match.group(1)
                # Find where it ends (before "changes_made" or end of JSON)
                end_match = re.search(r'"\s*,?\s*"?changes_made|"\s*\}', extracted)
                if end_match:
                    extracted = extracted[:end_match.start()]
                
                # Clean up escaped characters
                extracted = extracted.replace('\\n', '\n').replace('\\"', '"').rstrip('"')
                
                if len(extracted) > 100:  # Reasonable prompt length
                    success = self.db.update_prompt("chatbot_prompt", extracted)
                    return {
                        "success": success,
                        "updated_prompt": extracted[:200] + "..." if len(extracted) > 200 else extracted
                    }
        
        return {
            "success": False,
            "error": result.get("error", "Failed to generate improved prompt"),
            "raw_response": raw[:500] if raw else ""
        }
    
    def generate_reply(self, client_message: str, chat_history: str) -> str:
        """
        Generate a reply using the current prompt.
        
        Args:
            client_message: The client's message
            chat_history: Formatted chat history string
            
        Returns:
            Generated reply string
        """
        current_prompt = self.get_current_prompt()
        
        # Format the full prompt
        full_prompt = current_prompt.format(
            chat_history=chat_history,
            client_message=client_message
        )
        
        return self.llm.generate(full_prompt)


# Singleton instance
_editor_instance = None

def get_prompt_editor(llm_provider: str = None) -> PromptEditorService:
    """Get or create prompt editor service instance."""
    global _editor_instance
    if _editor_instance is None:
        _editor_instance = PromptEditorService(llm_provider=llm_provider)
    return _editor_instance
