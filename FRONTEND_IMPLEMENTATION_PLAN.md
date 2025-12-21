# Frontend Implementation Plan - DTV Assistant Chat Interface

This document provides step-by-step instructions for building a Next.js chat interface that connects to the Self-Learning AI Assistant backend.

---

## 🎯 Overview

**Goal**: Build a modern chat interface for the DTV visa assistant  
**Framework**: Next.js 14 (App Router)  
**Hosting**: Vercel (free tier)  
**Backend API**: https://self-learning-ai-assistant.onrender.com

---

## 📋 Prerequisites

Before starting, ensure you have:
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm or yarn installed
- [ ] Git installed
- [ ] GitHub account
- [ ] Vercel account (sign up at vercel.com with GitHub)

---

## 🚀 Step 1: Create Next.js Project

### 1.1 Create New Project

Open terminal and run:

```bash
npx create-next-app@latest dtv-assistant-frontend
```

When prompted, select these options:
```
✔ Would you like to use TypeScript? Yes
✔ Would you like to use ESLint? Yes
✔ Would you like to use Tailwind CSS? Yes
✔ Would you like to use `src/` directory? Yes
✔ Would you like to use App Router? Yes
✔ Would you like to customize the default import alias? No
```

### 1.2 Navigate to Project

```bash
cd dtv-assistant-frontend
```

### 1.3 Install Additional Dependencies

```bash
npm install lucide-react
npm install -D @types/node
```

---

## 🔧 Step 2: Environment Setup

### 2.1 Create Environment File

Create `.env.local` in the root folder:

```bash
touch .env.local
```

Add this content:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=https://self-learning-ai-assistant.onrender.com

# Optional: For development/testing
# NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 2.2 Create `.env.example` (for reference)

```bash
touch .env.example
```

Add:

```env
# Backend API URL (your Render deployment)
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### 2.3 Update `.gitignore`

Ensure `.env.local` is in `.gitignore` (it should be by default):

```
# local env files
.env*.local
```

---

## 📁 Step 3: Project Structure

Create the following folder structure:

```
dtv-assistant-frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page (chat interface)
│   │   ├── globals.css         # Global styles
│   │   └── admin/
│   │       └── page.tsx        # Admin panel for prompt management
│   ├── components/
│   │   ├── ChatInterface.tsx   # Main chat component
│   │   ├── ChatMessage.tsx     # Individual message bubble
│   │   ├── ChatInput.tsx       # Message input field
│   │   ├── Header.tsx          # App header
│   │   └── LoadingDots.tsx     # Typing indicator
│   ├── lib/
│   │   └── api.ts              # API service functions
│   └── types/
│       └── index.ts            # TypeScript types
├── public/
│   └── logo.svg                # App logo (optional)
├── .env.local                  # Environment variables
├── .env.example                # Example env file
├── tailwind.config.ts          # Tailwind configuration
├── next.config.js              # Next.js configuration
└── package.json
```

Create folders:

```bash
mkdir -p src/components src/lib src/types src/app/admin
```

---

## 📝 Step 4: Implementation Files

### 4.1 TypeScript Types (`src/types/index.ts`)

```typescript
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatHistory {
  role: 'client' | 'consultant';
  message: string;
}

export interface GenerateReplyRequest {
  message: string;
  chatHistory?: ChatHistory[];
}

export interface GenerateReplyResponse {
  aiReply: string;
}

export interface ImproveAIRequest {
  clientSequence: string;
  chatHistory: ChatHistory[];
  consultantReply: string;
}

export interface ImproveAIManuallyRequest {
  instructions: string;
}

export interface ImproveResponse {
  success: boolean;
  updatedPrompt?: string;
  predictedReply?: string;
  changesMade?: string;
  error?: string;
}
```

### 4.2 API Service (`src/lib/api.ts`)

```typescript
import { 
  GenerateReplyRequest, 
  GenerateReplyResponse, 
  ImproveAIManuallyRequest,
  ImproveResponse,
  ChatHistory 
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://self-learning-ai-assistant.onrender.com';

export async function generateReply(
  message: string, 
  chatHistory: ChatHistory[] = []
): Promise<string> {
  const response = await fetch(`${API_URL}/generate-reply`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      chatHistory,
    } as GenerateReplyRequest),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to generate reply');
  }

  const data: GenerateReplyResponse = await response.json();
  return data.aiReply;
}

export async function improveAIManually(instructions: string): Promise<ImproveResponse> {
  const response = await fetch(`${API_URL}/improve-ai-manually`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ instructions } as ImproveAIManuallyRequest),
  });

  const data = await response.json();
  return data;
}

export async function getCurrentPrompt(): Promise<string> {
  const response = await fetch(`${API_URL}/get-prompt`);
  
  if (!response.ok) {
    throw new Error('Failed to get prompt');
  }

  const data = await response.json();
  return data.prompt;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
```

### 4.3 Loading Animation (`src/components/LoadingDots.tsx`)

```typescript
export default function LoadingDots() {
  return (
    <div className="flex space-x-1 items-center">
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
    </div>
  );
}
```

### 4.4 Chat Message Component (`src/components/ChatMessage.tsx`)

```typescript
import { Message } from '@/types';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-gray-100 text-gray-800 rounded-bl-md'
        }`}
      >
        {/* Avatar */}
        <div className="flex items-start gap-3">
          {!isUser && (
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              🇹🇭
            </div>
          )}
          <div className="flex-1">
            {!isUser && (
              <p className="text-xs text-gray-500 mb-1 font-medium">DTV Assistant</p>
            )}
            <p className="text-sm md:text-base whitespace-pre-wrap">{message.content}</p>
            <p className={`text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 4.5 Chat Input Component (`src/components/ChatInput.tsx`)

```typescript
'use client';

import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({ onSend, disabled = false, placeholder = "Type your message..." }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end gap-2 p-4 border-t bg-white">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-sm md:text-base"
        style={{ maxHeight: '120px', minHeight: '48px' }}
      />
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="p-3 rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        <Send size={20} />
      </button>
    </div>
  );
}
```

### 4.6 Header Component (`src/components/Header.tsx`)

```typescript
import Link from 'next/link';
import { Settings } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-4 shadow-lg">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-xl">
            🇹🇭
          </div>
          <div>
            <h1 className="text-lg md:text-xl font-bold">DTV Visa Assistant</h1>
            <p className="text-xs md:text-sm text-blue-100">Powered by Issa Compass</p>
          </div>
        </div>
        <Link 
          href="/admin" 
          className="p-2 rounded-lg hover:bg-white/20 transition-colors"
          title="Admin Panel"
        >
          <Settings size={20} />
        </Link>
      </div>
    </header>
  );
}
```

### 4.7 Main Chat Interface (`src/components/ChatInterface.tsx`)

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { Message, ChatHistory } from '@/types';
import { generateReply } from '@/lib/api';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import LoadingDots from './LoadingDots';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Convert messages to chat history format for API
  const getChatHistory = (): ChatHistory[] => {
    return messages.map((msg) => ({
      role: msg.role === 'user' ? 'client' : 'consultant',
      message: msg.content,
    }));
  };

  const handleSend = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Get AI response
      const chatHistory = getChatHistory();
      const aiReply = await generateReply(content, chatHistory);

      // Add AI message
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: aiReply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get response');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] max-w-4xl mx-auto bg-white shadow-xl">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🇹🇭</div>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              Welcome to DTV Visa Assistant
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              I can help you with Thailand Destination Visa (DTV) applications. 
              Ask me about requirements, documents, processing times, and more!
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {[
                "What is the DTV visa?",
                "What documents do I need?",
                "How much does it cost?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSend(suggestion)}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
              <LoadingDots />
            </div>
          </div>
        )}

        {error && (
          <div className="text-center py-2">
            <p className="text-red-500 text-sm">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-blue-600 text-sm hover:underline"
            >
              Dismiss
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
```

### 4.8 Home Page (`src/app/page.tsx`)

```typescript
import Header from '@/components/Header';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <Header />
      <ChatInterface />
    </main>
  );
}
```

### 4.9 Admin Page (`src/app/admin/page.tsx`)

```typescript
'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, RefreshCw, Save } from 'lucide-react';
import Link from 'next/link';
import { getCurrentPrompt, improveAIManually } from '@/lib/api';

export default function AdminPage() {
  const [currentPrompt, setCurrentPrompt] = useState<string>('');
  const [instructions, setInstructions] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchPrompt = async () => {
    setIsFetching(true);
    try {
      const prompt = await getCurrentPrompt();
      setCurrentPrompt(prompt);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to fetch current prompt' });
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    fetchPrompt();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instructions.trim()) return;

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await improveAIManually(instructions);
      if (result.success) {
        setMessage({ type: 'success', text: 'Prompt updated successfully!' });
        setInstructions('');
        fetchPrompt(); // Refresh the prompt
      } else {
        setMessage({ type: 'error', text: result.error || 'Failed to update prompt' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to update prompt' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-4 shadow-lg">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <Link href="/" className="p-2 rounded-lg hover:bg-white/20 transition-colors">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-lg md:text-xl font-bold">Admin Panel</h1>
            <p className="text-xs md:text-sm text-purple-100">Manage AI Prompt</p>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-4 space-y-6">
        {/* Current Prompt Display */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800">Current Prompt</h2>
            <button
              onClick={fetchPrompt}
              disabled={isFetching}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <RefreshCw size={18} className={isFetching ? 'animate-spin' : ''} />
            </button>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            {isFetching ? (
              <p className="text-gray-500">Loading...</p>
            ) : (
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                {currentPrompt || 'No prompt found'}
              </pre>
            )}
          </div>
        </div>

        {/* Improve Prompt Form */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Improve AI Prompt</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Instructions for improvement
              </label>
              <textarea
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                placeholder="Example: Always greet users with Sawasdee. Be more concise in responses. Mention the money-back guarantee more often."
                rows={4}
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
              />
            </div>

            {message && (
              <div
                className={`p-3 rounded-lg text-sm ${
                  message.type === 'success'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {message.text}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !instructions.trim()}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isLoading ? (
                <>
                  <RefreshCw size={18} className="animate-spin" />
                  Updating...
                </>
              ) : (
                <>
                  <Save size={18} />
                  Update Prompt
                </>
              )}
            </button>
          </form>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Quick Improvements</h2>
          <div className="flex flex-wrap gap-2">
            {[
              'Be more concise in responses',
              'Use more emojis',
              'Always mention the free document review',
              'Add urgency when discussing processing times',
              'Be more empathetic with rejected applicants',
            ].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setInstructions(suggestion)}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
```

### 4.10 Root Layout (`src/app/layout.tsx`)

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'DTV Visa Assistant - Thailand Destination Visa Help',
  description: 'AI-powered assistant for Thailand DTV visa applications. Get help with requirements, documents, and application process.',
  keywords: 'DTV visa, Thailand visa, digital nomad visa, Thai visa application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

### 4.11 Global Styles (`src/app/globals.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Animation for loading dots */
@keyframes bounce {
  0%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-6px);
  }
}

.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out;
}
```

---

## 🚀 Step 5: Deploy to Vercel

### 5.1 Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit: DTV Assistant Frontend"
```

### 5.2 Create GitHub Repository

1. Go to https://github.com/new
2. Create new repository: `dtv-assistant-frontend`
3. Keep it public or private (your choice)
4. Don't initialize with README

### 5.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/dtv-assistant-frontend.git
git branch -M main
git push -u origin main
```

### 5.4 Deploy to Vercel

1. Go to https://vercel.com
2. Sign in with GitHub
3. Click **"Add New..."** → **"Project"**
4. Import your `dtv-assistant-frontend` repository
5. Configure project:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `./` (default)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

6. **Add Environment Variable**:
   - Click **"Environment Variables"**
   - Add:
     - **Name**: `NEXT_PUBLIC_API_URL`
     - **Value**: `https://self-learning-ai-assistant.onrender.com`

7. Click **"Deploy"**

### 5.5 Wait for Deployment

Vercel will build and deploy your app. Once complete, you'll get a URL like:
- `https://dtv-assistant-frontend.vercel.app`

---

## ✅ Step 6: Test Everything

### Test Chat Interface
1. Open your Vercel URL
2. Send a message: "What is DTV visa?"
3. Verify AI responds with DTV-specific info

### Test Admin Panel
1. Go to `/admin`
2. View current prompt
3. Try improving with: "Be more concise"
4. Test chat again to see changes

---

## 📱 Optional: Mobile Responsiveness

The implementation above is already mobile-responsive, but you can test on:
- Chrome DevTools (F12 → Mobile view)
- Your actual phone

---

## 🎨 Customization Notes

### Change Colors
Edit `tailwind.config.ts` to customize the color scheme:

```typescript
theme: {
  extend: {
    colors: {
      primary: '#your-color',
    },
  },
},
```

### Add Logo
Replace the emoji in `Header.tsx` with an image:

```typescript
<Image src="/logo.png" alt="Logo" width={40} height={40} />
```

### Add More Pages
Create new pages in `src/app/` folder:
- `/about` → `src/app/about/page.tsx`
- `/faq` → `src/app/faq/page.tsx`

---

## 🔧 Troubleshooting

### CORS Errors
If you see CORS errors, the backend already has CORS enabled. If issues persist, check:
- API URL is correct in `.env.local`
- Backend is running (check https://self-learning-ai-assistant.onrender.com/health)

### Build Errors
```bash
npm run build
```
Fix any TypeScript errors before deploying.

### Environment Variables Not Working
- Ensure variable starts with `NEXT_PUBLIC_`
- Restart dev server after changing `.env.local`
- Add variable in Vercel dashboard for production

---

## 📋 Deployment Checklist

Before sharing your app:

- [ ] Test all chat functionality
- [ ] Test admin panel
- [ ] Check mobile responsiveness
- [ ] Verify environment variables in Vercel
- [ ] Test error handling (turn off backend temporarily)
- [ ] Check loading states work correctly

---

## 🎉 Done!

Your frontend is now live on Vercel and connected to your self-learning AI backend!

**URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://self-learning-ai-assistant.onrender.com`
- Admin: `https://your-app.vercel.app/admin`
