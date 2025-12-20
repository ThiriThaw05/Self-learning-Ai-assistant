# Self-Learning AI Assistant - Project Plan

## 📋 Project Overview

Build a **self-learning AI customer support assistant** for Issa Compass that helps customers through the DTV (Destination Thailand Visa) process. The AI learns from real consultant conversations to improve over time.

---

## 🎯 Project Requirements

### Core Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| R1 | Microservice that accepts client messages + conversation history | **Must Have** |
| R2 | Returns intelligent AI-generated responses via LLM API | **Must Have** |
| R3 | Responses must sound human/casual (not robotic AI) | **Must Have** |
| R4 | Self-learning capability - AI improves from sample data | **Must Have** |
| R5 | Prompt stored in database (editable at runtime) | **Must Have** |
| R6 | Hosted publicly (Render/Railway/Fly.io) | **Must Have** |

### Technical Stack
- **Backend**: Python Flask (or alternative)
- **LLM**: Claude API / Gemini API / Groq API (Llama/Mistral)
- **Database**: Supabase / Neon / Firestore (free tier)
- **Hosting**: Render / Railway.app / Fly.io
- **Optional Frontend**: Next.js on Vercel

---

## ✨ Features & Functionalities

### Feature 1: AI Reply Generation
**Endpoint**: `POST /generate-reply`

```json
// Request
{
  "clientSequence": "I'm American and currently in Bali. Can I apply from Indonesia?",
  "chatHistory": [
    { "role": "consultant", "message": "Hi there! ..." },
    { "role": "client", "message": "Hello, I'm interested in..." }
  ]
}

// Response
{
  "aiReply": "Great news! As a US citizen, you can apply..."
}
```

**Acceptance Criteria**:
- [x] Accepts client message(s) and conversation history
- [x] Returns contextually appropriate response
- [x] Response tone matches sample consultant data (casual, helpful)
- [x] Uses prompt from database (not hardcoded)

---

### Feature 2: Auto-Improvement (Self-Learning)
**Endpoint**: `POST /improve-ai`

```json
// Request
{
  "clientSequence": "I'm American and currently in Bali...",
  "chatHistory": [...],
  "consultantReply": "Yes, absolutely! You can apply at..."
}

// Response
{
  "predictedReply": "Great news! As a US citizen...",
  "updatedPrompt": "You are a visa consultant..."
}
```

**Acceptance Criteria**:
- [x] Compares AI prediction vs actual consultant reply
- [x] Identifies differences in logic/style
- [x] Updates prompt with surgical precision
- [x] Saves updated prompt to database

---

### Feature 3: Manual Prompt Improvement
**Endpoint**: `POST /improve-ai-manually`

```json
// Request
{
  "instructions": "Be more concise. Always mention appointment booking proactively."
}

// Response
{
  "updatedPrompt": "You are a visa consultant..."
}
```

**Acceptance Criteria**:
- [x] Accepts natural language instructions
- [x] Modifies existing prompt based on instructions
- [x] Saves to database

---

## 📊 Fulfillment Criteria (Scoring)

### F Score (Baseline - Following Steps)
- [ ] Basic Flask server running
- [ ] Single endpoint that calls LLM
- [ ] Returns hardcoded or basic responses

### C Score (Meaningful Progress)
- [ ] All 3 endpoints working
- [ ] Prompt stored in database
- [ ] Self-learning loop functional
- [ ] Human-like responses

### B Score (Above Most Submissions)
- [ ] Everything in C
- [ ] Excellent response quality
- [ ] Robust error handling
- [ ] Clean, well-documented code
- [ ] Comprehensive testing

### A+ Score (Offer-worthy)
- [ ] Everything in B
- [ ] **Surprise factor** - unique innovations
- [ ] Examples of A+ improvements:
  - Docker deployment to GCP/AWS
  - Next.js chat interface
  - Diff visualization for self-learning edits
  - Analytics dashboard
  - Multi-LLM comparison
  - Conversation intent classification
  - High-interest customer detection
  - Drop-off pattern analysis

---

## 🗂️ Data Analysis (from conversations.json)

### Conversation Scenarios Covered
1. First-time DTV applicant (Digital Nomad)
2. Thai Cooking Class DTV
3. Rejected Application - Reapplication
4. Self-Employed / Freelancer
5. Document Issues
6. Post-Approval Questions
7. Bank Balance Requirements
8. Payment Issues
9. Embassy Interview Prep
10. Muay Thai Training DTV
11. Tourist Visa to DTV Switch
12. Embassy Document Follow-up
13. Long-term Stay & Extensions
14. Pricing & Money-back Guarantee
15. Urgent/Time-Sensitive Applications

### Key Topics AI Must Handle
- DTV eligibility (remote workers, soft power activities)
- Document requirements (passport, bank statements, enrollment)
- Financial requirements (500,000 THB minimum)
- Processing times by country
- Embassy interviews
- Rejection handling & reapplication
- Pricing (18,000 THB service fee)
- Money-back guarantee conditions

### Response Style Analysis
- Friendly, professional but casual
- Uses emojis sparingly (when appropriate)
- Structured lists for document requirements
- Clear next steps guidance
- Proactive information sharing

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Request                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Microservice                        │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │ /generate   │  │ /improve-ai │  │ /improve-manually│    │
│  │   -reply    │  │             │  │                  │    │
│  └─────────────┘  └─────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
     │   Database  │  │   LLM API   │  │  Editor LLM │
     │  (Prompts)  │  │ (Responses) │  │  (Learning) │
     └─────────────┘  └─────────────┘  └─────────────┘
```

---

## 📁 Recommended Project Structure

```
self-learning-ai-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Flask app entry
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── generate.py         # /generate-reply endpoint
│   │   ├── improve.py          # /improve-ai endpoint
│   │   └── manual.py           # /improve-ai-manually endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py      # LLM API integration
│   │   ├── db_service.py       # Database operations
│   │   └── prompt_editor.py    # Prompt improvement logic
│   ├── utils/
│   │   ├── __init__.py
│   │   └── conversation_parser.py
│   └── prompts/
│       └── base_prompts.py     # Initial prompts (before DB)
├── scripts/
│   ├── parse_conversations.py  # Parse conversations.json
│   ├── train_initial.py        # Initial training script
│   └── test_endpoints.py       # Endpoint testing
├── tests/
│   └── test_*.py
├── .env                        # API keys (DO NOT COMMIT)
├── .env.example               # Template for env vars
├── requirements.txt
├── Dockerfile                  # For A+ deployment
├── README.md
├── conversations.json          # Sample data
└── PROJECT_PLAN.md            # This file
```
