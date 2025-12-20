# User Setup Guide - Things YOU Need To Do

This guide covers all the steps **you** need to complete to set up the project infrastructure.

---

## 📋 Pre-Development Checklist

### Step 1: Get LLM API Keys (Choose 1 or more)

#### Option A: Google AI (Recommended - Generous Free Tier)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with Google account
3. Click "Get API Key" → "Create API Key"
4. Copy and save your API key
5. **Free tier**: 60 requests/minute for Gemini Pro

#### Option B: Groq API (Fastest - Free)
1. Go to [Groq Console](https://console.groq.com/)
2. Create account / Sign in
3. Go to "API Keys" section
4. Click "Create API Key"
5. Copy and save your API key
6. **Free tier**: Very generous, fast inference (Llama 3, Mistral)

#### Option C: Anthropic Claude API
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create account and verify email
3. Go to "API Keys"
4. Click "Create Key"
5. Copy and save your API key
6. **Free tier**: $5 credit for new accounts

#### Option D: OpenAI API
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account / Sign in
3. Go to "API Keys" section
4. Click "Create new secret key"
5. Copy and save your API key
6. **Free tier**: $5 credit for new accounts (limited time)

---

### Step 2: Set Up Database (Choose 1)

#### Option A: Supabase (Recommended - Easiest)
1. Go to [Supabase](https://supabase.com/)
2. Click "Start your project" → Sign up with GitHub
3. Create new project:
   - Name: `Ai-assistant` (or your choice)
   - Database Password: Create a strong password (SAVE THIS!)
   - Region: Choose closest to you
4. Wait for project to initialize (~2 minutes)
5. Get your credentials:
   - Go to **Settings** → **API**
   - Copy **Project URL** (looks like `https://xxxxx.supabase.co`)
   - Copy **anon/public** key
6. Create the prompts table:
   - Go to **SQL Editor**
   - Run this SQL:
   ```sql
   CREATE TABLE prompts (
     id SERIAL PRIMARY KEY,
     name VARCHAR(255) UNIQUE NOT NULL,
     content TEXT NOT NULL,
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );
   
   -- Insert initial prompt placeholder
   INSERT INTO prompts (name, content) 
   VALUES ('chatbot_prompt', 'You are a helpful visa consultant...');
   ```

#### Option B: Neon (PostgreSQL)
1. Go to [Neon](https://neon.tech/)
2. Sign up with GitHub/Google
3. Create new project
4. Copy connection string from dashboard
5. Create same table structure as above

#### Option C: Firebase Firestore
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create new project
3. Go to Build → Firestore Database
4. Create database in test mode
5. Get your config from Project Settings → General → Your apps → Web app

---

### Step 3: VS Code with GitHub Copilot (Already Set Up ✅)
You're already using VS Code with GitHub Copilot - perfect!

**Quick Tips:**
1. Open your project folder in VS Code
2. Use Copilot Chat (Cmd + Shift + I) for AI assistance
3. Copilot will help with code completion and suggestions
4. Use the integrated terminal (Ctrl + `) for running commands

---

### Step 4: Set Up Hosting Platform (Choose 1)

#### Option A: Railway (Easiest)
1. Go to [Railway.app](https://railway.app/)
2. Sign up with GitHub
3. First, create a workspace:
   - Click on your profile (top-right) → "Create Workspace"
   - Name it (e.g., "personal" or "dtv-assistant")
4. Once in your workspace, click "New Project"
5. Choose "Deploy from GitHub repo" (connect your repo later) OR "Empty Project"
6. You'll deploy from GitHub after pushing your code
7. **Free tier**: $5/month credit, 500 hours

#### Option B: Render
1. Go to [Render.com](https://render.com/)
2. Sign up with GitHub
3. Create new "Web Service"
4. Connect to your GitHub repo
5. **Free tier**: 750 hours/month (spins down after inactivity)

#### Option C: Fly.io
1. Go to [Fly.io](https://fly.io/)
2. Sign up
3. Install flyctl: `brew install flyctl`
4. Run `fly auth login`
5. **Free tier**: 3 shared VMs, 160GB transfer

---

### Step 5: Create Your .env File

Create a `.env` file in your project root with your keys:

```bash
# LLM API Keys (use the ones you got)
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database (Supabase example)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Or if using Neon
DATABASE_URL=postgresql://user:pass@host/dbname

# Flask
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=generate_a_random_string_here
```

**⚠️ IMPORTANT**: 
- Never commit `.env` to GitHub!
- Add `.env` to your `.gitignore`

---

### Step 6: Initialize Git Repository

```bash
# In your project folder
cd "/Users/thirithaw/self-learning AI assistant"

# Initialize git
git init

# Create .gitignore
echo ".env
__pycache__/
*.pyc
.DS_Store
venv/
.venv/
*.log" > .gitignore

# Initial commit
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
# Go to github.com → New Repository → Create
# Then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## 🔑 Quick Reference: Your API Keys Checklist

| Service | Status | Key Location |
|---------|--------|--------------|
| Google AI (Gemini) | ⬜ | `.env` → `GOOGLE_API_KEY` |
| Groq (Llama/Mistral) | ⬜ | `.env` → `GROQ_API_KEY` |
| Anthropic (Claude) | ⬜ | `.env` → `ANTHROPIC_API_KEY` |
| OpenAI (GPT) | ⬜ | `.env` → `OPENAI_API_KEY` |
| Supabase URL | ⬜ | `.env` → `SUPABASE_URL` |
| Supabase Key | ⬜ | `.env` → `SUPABASE_KEY` |

---

## 📝 After Setup - Test Your Keys

Create a quick test script to verify everything works:

```python
# test_setup.py
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
```

---

## 🚀 Ready to Develop!

Once you've completed all steps above:
1. ✅ At least 1 LLM API key obtained
2. ✅ Database set up with prompts table
3. ✅ VS Code with GitHub Copilot (you have this!)
4. ✅ Hosting platform account created
5. ✅ `.env` file created with your keys
6. ✅ Git repository initialized

**You're ready to start development!** 

Proceed to the **DEVELOPMENT_PLAN.md** for the step-by-step coding guide.

---

## 🆘 Troubleshooting

### "API key not working"
- Ensure no extra spaces/newlines in `.env`
- Some keys take a few minutes to activate
- Check if you've exceeded free tier limits

### "Database connection failed"
- Verify Supabase project is fully initialized
- Check if you're using the correct URL and key
- Ensure the `prompts` table exists

### "Copilot not responding"
- Check your GitHub Copilot subscription status
- Try restarting VS Code
- Use Claude/ChatGPT in browser as backup for complex planning
