# Development Plan - Microservice Implementation Guide

This document serves as a detailed reference for building the self-learning AI assistant microservice.

---

## 🗓️ Development Phases

### Phase 1: Foundation (30-45 mins)
- [ ] Set up Python project structure
- [ ] Create basic Flask server
- [ ] Test "Hello World" endpoint
- [ ] Deploy initial version to hosting

### Phase 2: Data Processing (30 mins)
- [ ] Parse conversations.json
- [ ] Create (client_sequence, consultant_reply, history) tuples
- [ ] Test data extraction

### Phase 3: LLM Integration (45 mins)
- [ ] Create LLM service wrapper
- [ ] Generate initial chatbot prompt
- [ ] Test AI reply generation

### Phase 4: Database Integration (30 mins)
- [ ] Connect to Supabase/database
- [ ] Store prompt in database
- [ ] Read prompt from database
- [ ] Test live prompt updates

### Phase 5: Self-Learning (45 mins)
- [ ] Create editor prompt
- [ ] Implement prompt comparison logic
- [ ] Test self-improvement loop

### Phase 6: API Endpoints (30 mins)
- [ ] Implement `/generate-reply`
- [ ] Implement `/improve-ai`
- [ ] Implement `/improve-ai-manually`
- [ ] Test all endpoints

### Phase 7: Polish & Deploy (30 mins)
- [ ] Error handling
- [ ] Logging
- [ ] Final deployment
- [ ] Test with cURL commands

---

## 📝 Phase 1: Foundation

### 1.1 Create Project Structure

```bash
mkdir -p app/{routes,services,utils}
touch app/__init__.py
touch app/main.py
touch app/routes/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
touch requirements.txt
touch .env.example
```

### 1.2 requirements.txt

```txt
flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
requests==2.31.0
supabase==2.0.0
google-generativeai==0.3.0
anthropic==0.8.0
groq==0.4.0
openai==1.6.0
gunicorn==21.2.0
```

### 1.3 Basic Flask Server (app/main.py)

```python
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return jsonify({"message": "DTV Assistant API is running!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

### 1.4 Deploy to Render (Initial)

Create `Procfile`:
```
web: gunicorn app.main:app
```

Create `runtime.txt`:
```
python-3.11.0
```

**Render Configuration:**
1. Connect your GitHub repo to Render
2. Configure the Web Service:
   - **Name**: `dtv-assistant`
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app`
3. Add Environment Variables in Render dashboard:
   - `GOOGLE_API_KEY` (or your LLM provider key)
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `FLASK_ENV=production`

Push to GitHub, Render will auto-deploy.

---

## 📝 Phase 2: Data Processing

### 2.1 Conversation Parser (app/utils/conversation_parser.py)

```python
import json
from typing import List, Dict, Tuple

def load_conversations(filepath: str) -> List[Dict]:
    """Load conversations from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def parse_conversation_pairs(conversations: List[Dict]) -> List[Dict]:
    """
    Parse conversations into training pairs.
    
    Returns list of:
    {
        "client_sequence": [list of client messages],
        "consultant_reply": [list of consultant messages],
        "chat_history": [preceding messages]
    }
    """
    training_pairs = []
    
    for conv in conversations:
        messages = conv.get('conversation', [])
        
        i = 0
        while i < len(messages):
            # Collect client sequence (consecutive "in" messages)
            client_sequence = []
            while i < len(messages) and messages[i]['direction'] == 'in':
                client_sequence.append(messages[i]['text'])
                i += 1
            
            # Collect consultant reply (consecutive "out" messages)
            consultant_reply = []
            while i < len(messages) and messages[i]['direction'] == 'out':
                consultant_reply.append(messages[i]['text'])
                i += 1
            
            # Only add if we have both
            if client_sequence and consultant_reply:
                # Chat history is everything before this exchange
                history_end = i - len(client_sequence) - len(consultant_reply)
                chat_history = []
                for msg in messages[:history_end]:
                    role = "client" if msg['direction'] == 'in' else "consultant"
                    chat_history.append({
                        "role": role,
                        "message": msg['text']
                    })
                
                training_pairs.append({
                    "client_sequence": client_sequence,
                    "consultant_reply": consultant_reply,
                    "chat_history": chat_history,
                    "scenario": conv.get('scenario', 'Unknown')
                })
    
    return training_pairs

def format_client_sequence(sequence: List[str]) -> str:
    """Format client messages into single string."""
    return "\n".join(sequence)

def format_chat_history(history: List[Dict]) -> str:
    """Format chat history for prompt."""
    if not history:
        return "No previous messages."
    
    formatted = []
    for msg in history:
        role = msg['role'].upper()
        formatted.append(f"[{role}]: {msg['message']}")
    return "\n".join(formatted)
```

### 2.2 Test Script (scripts/parse_conversations.py)

```python
from app.utils.conversation_parser import (
    load_conversations,
    parse_conversation_pairs,
    format_client_sequence,
    format_chat_history
)

def main():
    conversations = load_conversations('conversations.json')
    pairs = parse_conversation_pairs(conversations)
    
    print(f"Total training pairs: {len(pairs)}\n")
    
    # Print first 3 samples
    for i, pair in enumerate(pairs[:3]):
        print(f"=== Sample {i+1} ({pair['scenario']}) ===")
        print(f"\nClient Sequence:")
        print(format_client_sequence(pair['client_sequence']))
        print(f"\nConsultant Reply:")
        print("\n".join(pair['consultant_reply']))
        print(f"\nChat History:")
        print(format_chat_history(pair['chat_history']))
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
```

---

## 📝 Phase 3: LLM Integration

### 3.1 LLM Service (app/services/llm_service.py)

```python
import os
from typing import Optional
import google.generativeai as genai
from groq import Groq
from anthropic import Anthropic

class LLMService:
    def __init__(self, provider: str = "google"):
        self.provider = provider
        self._init_client()
    
    def _init_client(self):
        if self.provider == "google":
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel('gemini-pro')
        elif self.provider == "groq":
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            self.model_name = "llama-3.1-70b-versatile"
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model_name = "claude-3-sonnet-20240229"
    
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response from LLM."""
        try:
            if self.provider == "google":
                response = self.model.generate_content(prompt)
                return response.text
            
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
                
        except Exception as e:
            print(f"LLM Error: {e}")
            raise
    
    def generate_json(self, prompt: str) -> dict:
        """Generate response and parse as JSON."""
        import json
        response = self.generate(prompt)
        
        # Try to extract JSON from response
        try:
            # Look for JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass
        
        return {"error": "Failed to parse JSON", "raw": response}
```

### 3.2 Base Chatbot Prompt (app/prompts/base_prompts.py)

```python
CHATBOT_PROMPT = """You are a friendly immigration consultant at Issa Compass, helping clients with Thailand DTV (Destination Thailand Visa) applications.

PERSONALITY:
- Warm, helpful, and professional but casual
- Use simple, clear language
- Be proactive in offering next steps
- Sound human, not robotic

KNOWLEDGE BASE:
- DTV is available for remote workers, digital nomads, and those pursuing "soft power" activities (Muay Thai, cooking classes, etc.)
- Financial requirement: 500,000 THB equivalent (must be maintained for 3 months)
- Enrollment period: Minimum 6 months for soft power activities
- Service fee: 18,000 THB (includes government fees)
- Processing time varies by country (typically 7-10 business days)
- Countries with high approval rates: Singapore, Laos
- Required documents: Passport (6+ months validity), bank statements, proof of enrollment/employment, passport photo, proof of address

RESPONSE GUIDELINES:
1. Address the client's specific question first
2. Provide relevant details without overwhelming
3. Always suggest a clear next step
4. Keep responses concise but complete
5. Use occasional emojis where natural (sparingly)

Given the conversation context below, generate an appropriate response.

CHAT HISTORY:
{chat_history}

CLIENT MESSAGE:
{client_message}

Respond naturally as the consultant would. Return ONLY the response text, nothing else."""

EDITOR_PROMPT = """You are an expert prompt engineer analyzing an AI chatbot's performance.

CURRENT CHATBOT PROMPT:
{current_prompt}

CONVERSATION CONTEXT:
Chat History: {chat_history}
Client Message: {client_message}

REAL CONSULTANT REPLY:
{consultant_reply}

AI PREDICTED REPLY:
{predicted_reply}

TASK:
1. Compare the real consultant reply with the AI's predicted reply
2. Identify specific differences in:
   - Tone and style
   - Information accuracy
   - Response structure
   - Helpfulness and clarity
3. Determine what changes to the prompt would help the AI match the real consultant better
4. Make SURGICAL, PRECISE edits to the prompt - don't rewrite everything

Return your updated prompt in this JSON format:
{{"prompt": "the updated prompt text here", "changes_made": "brief description of changes"}}

Only output the JSON, nothing else."""

MANUAL_EDITOR_PROMPT = """You are an expert prompt engineer.

CURRENT CHATBOT PROMPT:
{current_prompt}

USER INSTRUCTIONS:
{instructions}

TASK:
Apply the user's instructions to improve the chatbot prompt.
Make targeted changes while preserving the overall structure and knowledge.

Return the updated prompt in this JSON format:
{{"prompt": "the updated prompt text here"}}

Only output the JSON, nothing else."""
```

---

## 📝 Phase 4: Database Integration

### 4.1 Database Service (app/services/db_service.py)

```python
import os
from supabase import create_client, Client
from typing import Optional

class DatabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(url, key)
    
    def get_prompt(self, name: str = "chatbot_prompt") -> Optional[str]:
        """Retrieve prompt from database."""
        try:
            response = self.client.table("prompts") \
                .select("content") \
                .eq("name", name) \
                .single() \
                .execute()
            return response.data.get("content") if response.data else None
        except Exception as e:
            print(f"DB Error getting prompt: {e}")
            return None
    
    def update_prompt(self, name: str, content: str) -> bool:
        """Update prompt in database."""
        try:
            self.client.table("prompts") \
                .update({"content": content}) \
                .eq("name", name) \
                .execute()
            return True
        except Exception as e:
            print(f"DB Error updating prompt: {e}")
            return False
    
    def create_prompt(self, name: str, content: str) -> bool:
        """Create new prompt in database."""
        try:
            self.client.table("prompts") \
                .insert({"name": name, "content": content}) \
                .execute()
            return True
        except Exception as e:
            print(f"DB Error creating prompt: {e}")
            return False
```

---

## 📝 Phase 5: Self-Learning Logic

### 5.1 Prompt Editor Service (app/services/prompt_editor.py)

```python
from app.services.llm_service import LLMService
from app.services.db_service import DatabaseService
from app.prompts.base_prompts import EDITOR_PROMPT, MANUAL_EDITOR_PROMPT

class PromptEditorService:
    def __init__(self, llm_provider: str = "google"):
        self.llm = LLMService(provider=llm_provider)
        self.db = DatabaseService()
    
    def improve_from_example(
        self,
        client_message: str,
        chat_history: str,
        consultant_reply: str,
        predicted_reply: str
    ) -> dict:
        """
        Improve the prompt based on comparing predicted vs actual reply.
        """
        current_prompt = self.db.get_prompt("chatbot_prompt")
        
        editor_input = EDITOR_PROMPT.format(
            current_prompt=current_prompt,
            chat_history=chat_history,
            client_message=client_message,
            consultant_reply=consultant_reply,
            predicted_reply=predicted_reply
        )
        
        result = self.llm.generate_json(editor_input)
        
        if "prompt" in result:
            # Update database with new prompt
            self.db.update_prompt("chatbot_prompt", result["prompt"])
            return {
                "success": True,
                "updated_prompt": result["prompt"],
                "changes": result.get("changes_made", "No description")
            }
        
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    def improve_manually(self, instructions: str) -> dict:
        """
        Improve the prompt based on manual instructions.
        """
        current_prompt = self.db.get_prompt("chatbot_prompt")
        
        editor_input = MANUAL_EDITOR_PROMPT.format(
            current_prompt=current_prompt,
            instructions=instructions
        )
        
        result = self.llm.generate_json(editor_input)
        
        if "prompt" in result:
            self.db.update_prompt("chatbot_prompt", result["prompt"])
            return {
                "success": True,
                "updated_prompt": result["prompt"]
            }
        
        return {"success": False, "error": result.get("error", "Unknown error")}
```

---

## 📝 Phase 6: API Endpoints

### 6.1 Generate Reply Route (app/routes/generate.py)

```python
from flask import Blueprint, request, jsonify
from app.services.llm_service import LLMService
from app.services.db_service import DatabaseService

generate_bp = Blueprint('generate', __name__)

@generate_bp.route('/generate-reply', methods=['POST'])
def generate_reply():
    """Generate AI response based on conversation context."""
    try:
        data = request.get_json()
        
        client_sequence = data.get('clientSequence', '')
        chat_history = data.get('chatHistory', [])
        
        # Format chat history
        history_text = "No previous messages."
        if chat_history:
            history_text = "\n".join([
                f"[{msg['role'].upper()}]: {msg['message']}"
                for msg in chat_history
            ])
        
        # Get prompt from database
        db = DatabaseService()
        prompt_template = db.get_prompt("chatbot_prompt")
        
        if not prompt_template:
            return jsonify({"error": "Prompt not found in database"}), 500
        
        # Format the prompt
        full_prompt = prompt_template.format(
            chat_history=history_text,
            client_message=client_sequence
        )
        
        # Generate response
        llm = LLMService(provider="google")  # or from config
        ai_reply = llm.generate(full_prompt)
        
        return jsonify({"aiReply": ai_reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 6.2 Improve AI Route (app/routes/improve.py)

```python
from flask import Blueprint, request, jsonify
from app.services.llm_service import LLMService
from app.services.db_service import DatabaseService
from app.services.prompt_editor import PromptEditorService

improve_bp = Blueprint('improve', __name__)

@improve_bp.route('/improve-ai', methods=['POST'])
def improve_ai():
    """Auto-improve AI prompt by comparing predicted vs actual reply."""
    try:
        data = request.get_json()
        
        client_sequence = data.get('clientSequence', '')
        chat_history = data.get('chatHistory', [])
        consultant_reply = data.get('consultantReply', '')
        
        # Format history
        history_text = "\n".join([
            f"[{msg['role'].upper()}]: {msg['message']}"
            for msg in chat_history
        ]) if chat_history else "No previous messages."
        
        # First, generate a prediction with current prompt
        db = DatabaseService()
        prompt_template = db.get_prompt("chatbot_prompt")
        
        full_prompt = prompt_template.format(
            chat_history=history_text,
            client_message=client_sequence
        )
        
        llm = LLMService(provider="google")
        predicted_reply = llm.generate(full_prompt)
        
        # Now improve the prompt
        editor = PromptEditorService(llm_provider="google")
        result = editor.improve_from_example(
            client_message=client_sequence,
            chat_history=history_text,
            consultant_reply=consultant_reply,
            predicted_reply=predicted_reply
        )
        
        return jsonify({
            "predictedReply": predicted_reply,
            "updatedPrompt": result.get("updated_prompt", ""),
            "changes": result.get("changes", "")
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@improve_bp.route('/improve-ai-manually', methods=['POST'])
def improve_ai_manually():
    """Manually update AI prompt with specific instructions."""
    try:
        data = request.get_json()
        instructions = data.get('instructions', '')
        
        if not instructions:
            return jsonify({"error": "Instructions required"}), 400
        
        editor = PromptEditorService(llm_provider="google")
        result = editor.improve_manually(instructions)
        
        return jsonify({
            "updatedPrompt": result.get("updated_prompt", ""),
            "success": result.get("success", False)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 6.3 Updated Main App (app/main.py)

```python
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from app.routes.generate import generate_bp
from app.routes.improve import improve_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(generate_bp)
    app.register_blueprint(improve_bp)
    
    @app.route('/')
    def hello():
        return jsonify({
            "message": "DTV Assistant API is running!",
            "endpoints": [
                "POST /generate-reply",
                "POST /improve-ai",
                "POST /improve-ai-manually"
            ]
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

---

## 📝 Phase 7: Testing & Deployment

### 7.1 Test cURL Commands

```bash
# Test health (replace with your Render URL)
curl https://your-app.onrender.com/health

# Test generate-reply
curl -X POST https://your-app.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "clientSequence": "I am American and currently in Bali. Can I apply from Indonesia?",
    "chatHistory": [
      {"role": "consultant", "message": "Hi there! Thank you for reaching out. The DTV is perfect for remote workers. May I know your nationality and which country you would like to apply from?"},
      {"role": "client", "message": "Hello, I am interested in the DTV visa for Thailand. I work remotely as a software developer."}
    ]
  }'

# Test improve-ai
curl -X POST https://your-app.onrender.com/improve-ai \
  -H "Content-Type: application/json" \
  -d '{
    "clientSequence": "I am American and currently in Bali. Can I apply from Indonesia?",
    "chatHistory": [
      {"role": "consultant", "message": "Hi there! Thank you for reaching out."},
      {"role": "client", "message": "Hello, I am interested in the DTV visa."}
    ],
    "consultantReply": "Yes, you can apply from Indonesia! For remote workers, our service fees are 18,000 THB including all government fees. Processing time is typically around 10 business days."
  }'

# Test improve-ai-manually
curl -X POST https://your-app.onrender.com/improve-ai-manually \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "Be more concise. Always mention the money-back guarantee when discussing our services."
  }'
```

### 7.2 Initial Training Script (scripts/train_initial.py)

```python
"""
Run this script to train the AI on all conversation samples.
This will iteratively improve the prompt using the self-learning loop.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.utils.conversation_parser import (
    load_conversations,
    parse_conversation_pairs,
    format_client_sequence,
    format_chat_history
)
from app.services.prompt_editor import PromptEditorService
from app.services.db_service import DatabaseService
from app.prompts.base_prompts import CHATBOT_PROMPT

def main():
    # Initialize with base prompt if not exists
    db = DatabaseService()
    if not db.get_prompt("chatbot_prompt"):
        db.create_prompt("chatbot_prompt", CHATBOT_PROMPT)
        print("Initialized base prompt in database")
    
    # Load training data
    conversations = load_conversations('conversations.json')
    pairs = parse_conversation_pairs(conversations)
    
    print(f"Training on {len(pairs)} conversation pairs...")
    
    editor = PromptEditorService(llm_provider="google")
    
    for i, pair in enumerate(pairs):
        print(f"\n[{i+1}/{len(pairs)}] Training on: {pair['scenario'][:50]}...")
        
        client_msg = format_client_sequence(pair['client_sequence'])
        history = format_chat_history(pair['chat_history'])
        consultant_reply = "\n".join(pair['consultant_reply'])
        
        # Generate prediction and improve
        result = editor.improve_from_example(
            client_message=client_msg,
            chat_history=history,
            consultant_reply=consultant_reply,
            predicted_reply=""  # Will be generated internally
        )
        
        if result.get("success"):
            print(f"  ✓ Prompt updated: {result.get('changes', 'No description')[:100]}")
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown')}")
    
    print("\nTraining complete!")
    print("Final prompt saved to database.")

if __name__ == "__main__":
    main()
```

---

## 🌟 A+ Score Enhancements (Optional)

### Enhancement Ideas

1. **Docker Deployment**
   - Create Dockerfile
   - Deploy to GCP Cloud Run or AWS ECS

2. **Next.js Chat Interface**
   - Create frontend at `/frontend`
   - Real-time chat visualization
   - Deploy to Vercel

3. **Diff Visualization**
   - Show before/after prompt changes
   - Track learning history

4. **Analytics Dashboard**
   - Track response quality
   - Monitor self-learning improvements

5. **Multi-LLM Support**
   - A/B test different providers
   - Fallback mechanisms

6. **Intent Classification**
   - Classify incoming messages
   - Route to specialized handlers

7. **High-Interest Detection**
   - Score customer engagement
   - Prioritize leads

---

## 📌 Quick Reference

### Environment Variables Required
```
GOOGLE_API_KEY=xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
```

### Endpoints Summary
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/generate-reply` | Generate AI response |
| POST | `/improve-ai` | Auto-improve from example |
| POST | `/improve-ai-manually` | Manual prompt update |

### File Structure Summary
```
app/
├── main.py              # Flask app
├── routes/
│   ├── generate.py      # /generate-reply
│   └── improve.py       # /improve-ai, /improve-ai-manually
├── services/
│   ├── llm_service.py   # LLM API wrapper
│   ├── db_service.py    # Database operations
│   └── prompt_editor.py # Self-learning logic
├── utils/
│   └── conversation_parser.py
└── prompts/
    └── base_prompts.py
```
