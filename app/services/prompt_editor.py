from app.services.llm_service import get_llm_service
from app.services.db_service import get_db_service
from app.prompts.base_prompts import EDITOR_PROMPT, MANUAL_EDITOR_PROMPT, CHATBOT_PROMPT
import re


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

        # Fallback: try to salvage a prompt from raw LLM output when JSON parsing fails
        fallback = self._extract_prompt_from_raw(result.get("raw_response", ""))
        if fallback:
            success = self.db.update_prompt("chatbot_prompt", fallback)
            return {
                "success": success,
                "updated_prompt": fallback,
                "changes_made": result.get("changes_made", "Extracted prompt from raw response")
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
        raw_reply = self.llm.generate(full_prompt, max_tokens=220)
        return self._postprocess_reply(raw_reply, chat_history)

    def _postprocess_reply(self, reply: str, chat_history: str) -> str:
        """Enforce greeting/question bans and length caps."""
        is_follow_up = chat_history.strip() != "No previous messages."

        # Strip leading greetings on follow-ups
        if is_follow_up:
            reply = re.sub(r"^\s*(sawasdee[^\w]*|hello[^\w]*|hi[^\w]*|hey[^\w]*)", "", reply, flags=re.IGNORECASE)

        # Split into lines to handle lists
        lines = [line.strip() for line in reply.splitlines() if line.strip()]

        # Drop greeting lines that slipped through
        if is_follow_up:
            lines = [line for line in lines if not re.match(r'^(sawasdee|hello|hi|hey)\b', line, flags=re.IGNORECASE)]

        # Remove handholding/invite phrases
        invite_patterns = [r"would you like", r"let me ", r"can i ", r"shall i", r"i can .*guide", r"we can .*guide"]
        filtered_lines = []
        for line in lines:
            lower = line.lower()
            if any(re.search(pat, lower) for pat in invite_patterns):
                continue
            filtered_lines.append(line)
        lines = filtered_lines

        # Rejoin for sentence trimming
        text = " ".join(lines)

        # Sentence split
        sentences = re.split(r"(?<=[.!?])\s+", text)
        # Drop empty fragments
        sentences = [s.strip() for s in sentences if s.strip()]

        if is_follow_up:
            sentences = sentences[:2]  # max 2 sentences, may include one question if present
        else:
            sentences = sentences[:3]  # max 3 sentences

        # Reassemble
        final = " ".join(sentences).strip()

        return final

    def _extract_prompt_from_raw(self, raw: str) -> str:
        """
        Attempt to pull a prompt string out of a messy LLM response when JSON parsing failed.
        """
        import re
        if not raw:
            return ""

        # Try to capture text inside a "prompt": "..." block
        match = re.search(r'"prompt"\s*:\s*"(.*?)"', raw, re.DOTALL)
        if match:
            extracted = match.group(1)
        else:
            extracted = raw

        # Clean common escape sequences and trim
        extracted = extracted.replace('\\n', '\n').replace('\\"', '"').strip()

        # Ignore obviously too-short outputs that aren't real prompts
        return extracted if len(extracted) > 100 else ""


# Singleton instance
_editor_instance = None

def get_prompt_editor(llm_provider: str = None) -> PromptEditorService:
    """Get or create prompt editor service instance."""
    global _editor_instance
    if _editor_instance is None:
        _editor_instance = PromptEditorService(llm_provider=llm_provider)
    return _editor_instance
