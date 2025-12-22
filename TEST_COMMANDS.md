# DTV Assistant API Test Commands

**Base URL:** `https://self-learning-ai-assistant.onrender.com`

## Quick Health Check

```bash
curl -s https://self-learning-ai-assistant.onrender.com/health
```

Expected: `{"status": "healthy"}`

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/generate-reply` | POST | Generate AI response |
| `/improve-ai` | POST | Self-learning from real consultant replies |
| `/improve-ai-manually` | POST | Manual prompt improvement |
| `/get-prompt` | GET | Get current prompt |
| `/reset-prompt` | POST | Reset to base prompt |

---

## Scenario 1: Remote Worker DTV Application

### Test 1.1 - Initial Inquiry
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I am interested in the DTV visa for Thailand. I work remotely as a software developer for a US company.",
    "chat_history": []
  }'
```

**Expected behavior:** Should greet with "Sawasdee", confirm eligibility, ask about nationality/country.

### Test 1.2 - Country and Nationality
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am American and currently in Bali. Can I apply from Indonesia?",
    "chat_history": [
      {"role": "user", "content": "Hello, I am interested in the DTV visa for Thailand. I work remotely as a software developer for a US company."},
      {"role": "assistant", "content": "Sawasdee! The DTV is perfect for remote workers like yourself. May I know your nationality and which country you would like to apply from?"}
    ]
  }'
```

**Expected behavior:** Should confirm Indonesia works, mention service fee (18,000 THB), mention processing time (~10 business days).

### Test 1.3 - Document Requirements
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What documents do I need to prepare?",
    "chat_history": [
      {"role": "user", "content": "Hello, I am interested in the DTV visa for Thailand. I work remotely as a software developer for a US company."},
      {"role": "assistant", "content": "Sawasdee! The DTV is perfect for remote workers. May I know your nationality and which country you would like to apply from?"},
      {"role": "user", "content": "I am American and currently in Bali. Can I apply from Indonesia?"},
      {"role": "assistant", "content": "Yes, you can apply from Indonesia! Our service fee is 18,000 THB including government fees. Processing takes about 10 business days."}
    ]
  }'
```

**Expected behavior:** Should list ALL required documents in numbered format:
1. Valid passport (6+ months validity)
2. Bank statements (500,000 THB for 3 months)
3. Employment contract/letter
4. Proof of income (pay slips)
5. Passport-sized photo
6. Proof of address

### Test 1.4 - Financial Requirement Confirmation
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My bank balance has been above $15,000 USD for the past year. Do I need to convert it to THB?",
    "chat_history": [
      {"role": "user", "content": "What documents do I need?"},
      {"role": "assistant", "content": "You will need: passport, bank statements showing 500,000 THB for 3 months, employment contract, pay slips, photo, and proof of address."}
    ]
  }'
```

**Expected behavior:** Should confirm $15,000 USD exceeds requirement (~$14,000-15,000 USD = 500,000 THB), no need to convert.

---

## Scenario 2: Thai Cooking Class (Soft Power)

### Test 2.1 - Initial Inquiry
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi! I want to apply for DTV using Thai cooking class. Already enrolled at a school in Chiang Mai.",
    "chat_history": []
  }'
```

**Expected behavior:** Should greet, confirm cooking class eligibility, ask nationality/country, mention 6-month minimum requirement.

### Test 2.2 - Singapore Application with Multiple Facts
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am from Singapore. Planning to apply from here. My course is from March to August next year. I have 80,000 SGD in savings. Is that enough?",
    "chat_history": [
      {"role": "user", "content": "Hi! I want to apply for DTV using Thai cooking class. Already enrolled at a school in Chiang Mai."},
      {"role": "assistant", "content": "Sawasdee! Great that you are enrolled in a cooking class. May I know your nationality and where you plan to apply from?"}
    ]
  }'
```

**Expected behavior:** Should confirm ALL THREE facts in one response:
- Singapore = 7-10 days processing, high approval rate
- March-August = meets 6-month minimum ✓
- 80,000 SGD = way above requirement (500,000 THB ≈ 19,000-20,000 SGD) ✓

Should NOT ask confirmation questions about these facts.

### Test 2.3 - School Documents
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What documents do I need from the cooking school?",
    "chat_history": [
      {"role": "user", "content": "Hi! I want to apply for DTV using Thai cooking class."},
      {"role": "assistant", "content": "Sawasdee! May I know your nationality and where you plan to apply from?"},
      {"role": "user", "content": "I am from Singapore. Course is March to August."},
      {"role": "assistant", "content": "Singapore has 7-10 day processing with high approval rates. Your March-August course meets the 6-month minimum."}
    ]
  }'
```

**Expected behavior:** Should list:
1. Enrollment letter (showing 6+ month duration)
2. Proof of payment
3. School's business registration

---

## Scenario 3: Rejected Application - Reapplication

### Test 3.1 - Rejection Help
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello I need help urgently. My DTV application was rejected in Vietnam",
    "chat_history": []
  }'
```

**Expected behavior:** Should express empathy, ask for rejection reason and DTV type applied for.

### Test 3.2 - Insufficient Documentation Analysis
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am Australian. Bank statement showed 400,000 THB for 6 months. Enrollment was for 4 months Muay Thai.",
    "chat_history": [
      {"role": "user", "content": "My DTV was rejected in Vietnam. They said insufficient documentation."},
      {"role": "assistant", "content": "I am sorry to hear that. Can you tell me more? Did your bank statement show 500,000 THB for 3 months? Was enrollment for 6+ months?"}
    ]
  }'
```

**Expected behavior:** Should identify BOTH problems:
1. 400,000 THB < required 500,000 THB
2. 4 months < required 6 months for soft power

### Test 3.3 - Reapplication Options (Laos)
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can I reapply? I can add more money and extend training.",
    "chat_history": [
      {"role": "user", "content": "Bank showed 400,000 THB, enrollment was 4 months."},
      {"role": "assistant", "content": "I see two issues: 400,000 THB is below the required 500,000 THB, and 4 months is below the 6-month minimum for Muay Thai."}
    ]
  }'
```

**Expected behavior:** Should recommend:
- Yes can reapply
- Consider Laos (highest approval for reapplications)
- Need to top up to 500,000+ THB and maintain for 3 months
- Extend enrollment to 6+ months
- Laos requires in-person interview

### Test 3.4 - Laos Interview Questions
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "An interview? What do they ask?",
    "chat_history": [
      {"role": "user", "content": "Can I reapply?"},
      {"role": "assistant", "content": "Yes! Since rejected in Vietnam, we recommend applying from Laos which has highest approval for reapplications. Laos requires in-person interview."}
    ]
  }'
```

**Expected behavior:** Should explain interview questions:
- Why you want to train Muay Thai in Thailand
- Your plans after training
- How you'll support yourself financially
- May ask to show mobile banking app to verify balance

### Test 3.5 - Laos Fees
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is your service fee for Laos?",
    "chat_history": [
      {"role": "user", "content": "I will apply from Laos then."},
      {"role": "assistant", "content": "Good choice! Laos has highest approval rate for reapplications."}
    ]
  }'
```

**Expected behavior:** Should state:
- Service fee: 5,000 THB
- Government fee: 10,000 THB (cash, paid in person at embassy)
- Total: 15,000 THB

---

## Scenario 4: Freelancer with Thai Client Issue

### Test 4.1 - Freelancer Eligibility
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi, I am a freelance graphic designer. Can I apply for DTV?",
    "chat_history": []
  }'
```

**Expected behavior:** Should confirm freelancers are eligible, ask about nationality and business registration.

### Test 4.2 - Thai Client Problem
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "One of my clients is actually a Thai company. Is that a problem?",
    "chat_history": [
      {"role": "user", "content": "I am a German freelancer with business in Germany."},
      {"role": "assistant", "content": "Great! For DTV you cannot work with Thai clients. Where do you plan to apply from?"}
    ]
  }'
```

**Expected behavior:** Should clearly state:
- YES this is problematic
- DTV rule: cannot work with Thai clients/companies
- Recommend not including Thai client invoices in application
- Ask if they have enough invoices from non-Thai clients

### Test 4.3 - Translation Requirements
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My business documents are in German. Do I need official translations?",
    "chat_history": [
      {"role": "user", "content": "I am German freelancer applying from Malaysia."},
      {"role": "assistant", "content": "Malaysia works! Processing is 10-14 business days."}
    ]
  }'
```

**Expected behavior:** Should confirm:
- Yes, documents must be in Thai or English
- Need official translations by certified translator
- Translations should be stamped/signed

---

## Scenario 5: Financial Requirements Deep Dive

### Test 5.1 - Crypto Question
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Does crypto count towards the 500,000 THB requirement?",
    "chat_history": []
  }'
```

**Expected behavior:** Should state:
- NO, crypto does not count
- Must be cash in traditional bank account
- 500,000 THB for 3 consecutive months

### Test 5.2 - Stocks Question
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about stocks or investment accounts?",
    "chat_history": [
      {"role": "user", "content": "Does crypto count towards the 500,000 THB requirement?"},
      {"role": "assistant", "content": "No, crypto does not count. Must be cash in bank account for 3 months."}
    ]
  }'
```

**Expected behavior:** Should state:
- Stocks/investments don't count as PRIMARY proof
- BUT can include them as additional evidence of financial stability
- 500,000 THB must be in savings/checking account

### Test 5.3 - Should I Sell Stocks?
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have about 300,000 THB in savings and 400,000 THB in stocks. Should I sell some stocks?",
    "chat_history": [
      {"role": "user", "content": "Does crypto count?"},
      {"role": "assistant", "content": "No, must be cash."},
      {"role": "user", "content": "What about stocks?"},
      {"role": "assistant", "content": "Stocks do not count as primary proof. Must be cash in bank account."}
    ]
  }'
```

**Expected behavior:** Should recommend:
- Transfer at least 200,000 THB more to savings (to reach 500,000 THB)
- Maintain the balance for 3 months before applying

### Test 5.4 - 3-Month Alternative (CRITICAL TEST)
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "3 months? That is a long time. Is there any way around this?",
    "chat_history": [
      {"role": "user", "content": "I have 300,000 THB cash and 400,000 THB stocks. Should I sell?"},
      {"role": "assistant", "content": "Yes, transfer at least 200,000 THB to meet the 500,000 THB requirement. Maintain for 3 months before applying."}
    ]
  }'
```

**Expected behavior:** Should mention the "money trail" option:
- The 3-month rule is set by Thai embassy
- BUT if you can show clear money trail (proof of investment sale → deposit)
- Some embassies MAY accept it
- For highest approval chances, still recommend 3 months

### Test 5.5 - Which Embassy is Flexible? (CRITICAL TEST)
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Which embassy is less strict about this?",
    "chat_history": [
      {"role": "user", "content": "Is there any way around the 3 months?"},
      {"role": "assistant", "content": "Some embassies may accept clear money trail showing investment sale to deposit. But 3 months is recommended for highest approval."}
    ]
  }'
```

**Expected behavior:** Should say:
- **Malaysia and Indonesia** tend to be more flexible (NOT Singapore)
- But there's always risk if not meeting standard requirement
- Offer to review specific documents

---

## Scenario 6: Address Proof Issues

### Test 6.1 - Staying with Friend
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am staying with a friend. I do not have utilities in my name here.",
    "chat_history": [
      {"role": "user", "content": "My address proof was rejected. What counts as acceptable?"},
      {"role": "assistant", "content": "Acceptable address proof includes: utility bills, government letters, rental agreement, driver license with address, or bank statement letter."}
    ]
  }'
```

**Expected behavior:** Should suggest alternatives:
- Driver's license from home country with address
- Recent government letter
- Bank statements mailed to address
- Letter from friend confirming you're staying there

---

## Scenario 7: Post-Approval Questions

### Test 7.1 - 90-Day Reporting
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about 90-day reporting? I heard that is required?",
    "chat_history": [
      {"role": "user", "content": "My DTV was approved! How long can I stay per entry?"},
      {"role": "assistant", "content": "Congratulations! You can stay up to 180 days per entry. The visa is valid for 5 years with multiple entries."}
    ]
  }'
```

**Expected behavior:** Should explain:
- Required if staying 90+ consecutive days
- Can be done: in person, online, or by mail
- Mention they offer 90-day reporting service

---

## Self-Learning Endpoint Tests

### Test: Improve AI with Real Consultant Reply
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/improve-ai \
  -H "Content-Type: application/json" \
  -d '{
    "client_message": "Does crypto count towards the 500,000 THB requirement?",
    "consultant_reply": "Hello! Unfortunately, cryptocurrency holdings are not accepted as proof of the required funds. The embassy requires you to have 500,000 THB equivalent as cash balance in a traditional bank account.",
    "chat_history": []
  }'
```

**Expected behavior:** Returns improved prompt based on comparing AI prediction with real consultant reply.

### Test: Get Current Prompt
```bash
curl -s https://self-learning-ai-assistant.onrender.com/get-prompt
```

**Expected behavior:** Returns current chatbot prompt.

### Test: Reset Prompt to Base
```bash
curl -s -X POST https://self-learning-ai-assistant.onrender.com/reset-prompt
```

**Expected behavior:** Resets prompt to base template, returns confirmation.

---

## Key Behaviors to Verify

| Test Area | Expected Behavior |
|-----------|-------------------|
| Greeting | "Sawasdee" only on first message, no greeting on follow-ups |
| Financial calc | 80,000 SGD > 500,000 THB (≈19-20k SGD) ✓ |
| Proactive info | Should mention fees, processing times without being asked |
| No confirmation questions | Should NOT ask "Can you confirm...?" about stated facts |
| No "would you like" | Should NOT end with "Would you like me to..." |
| Flexible embassy | Malaysia/Indonesia (NOT Singapore) |
| Money trail option | Should mention as alternative to 3-month wait |
| Thai client rule | Cannot work with Thai clients/companies |
| Soft power minimum | 6 months enrollment required |
| Laos fees | 5,000 THB service + 10,000 THB gov fee = 15,000 THB total |

---

## Running All Tests

Save each curl command response and verify against expected behaviors. For automated testing, you can pipe to a file:

```bash
# Run all tests and save outputs
curl -s -X POST https://self-learning-ai-assistant.onrender.com/generate-reply \
  -H "Content-Type: application/json" \
  -d '{"message": "Does crypto count towards the 500,000 THB requirement?", "chat_history": []}' \
  >> test_results.json

echo "\n---\n" >> test_results.json

# Continue with more tests...
```
