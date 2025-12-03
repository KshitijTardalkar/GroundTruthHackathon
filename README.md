# H-002 | Customer Experience Automation


> **GroundTruth AI Hackathon 2025**

**EVA (Enhanced Virtual Assistant)** is a privacy-first conversational AI that delivers hyper-personalized customer support through Retrieval-Augmented Generation (RAG). By combining customer history retrieval, PII masking, and contextual memory, EVA transforms generic chatbot interactions into intelligent, context-aware conversations.

***

## 🚀 The Problem We're Solving

### Current State: Generic Chatbots Fail Customers

Retail customers expect instant, personalized service:

- ❌ **"Is this store open?"** → *"Please check our website"*
- ❌ **"Do you have my size?"** → *"I don't have that information"*  
- ❌ **"I'm cold"** → *"I don't understand"*

**The core problem**: Traditional chatbots lack context, memory, and privacy safeguards.

### My Solution: RAG + Privacy + Context

EVA delivers hyper-personalized responses while protecting customer data:

| **Feature** | **EVA's Implementation** | **Business Impact** |
|------------|-------------------------|-------------------|
| ✅ **RAG Pipeline** | Retrieves customer profiles, purchase history from vector store | Personalized recommendations based on past behavior |
| ✅ **PII Protection** | Microsoft Presidio masks sensitive data before LLM processing | GDPR-compliant, enterprise-ready privacy |
| ✅ **Conversation Memory** | Session-based chat history with LangChain | Multi-turn dialogue maintains context |
| ✅ **Fast Inference** | Groq sub-2s response time | Real-time customer experience |

**Example Interaction**:
```
User: "I'm cold and want my usual."
EVA:  "I understand! Based on your order history, you love our Hot Cocoa. 
       The Downtown Starbucks is 50m away and open until 9 PM. 
       I've applied your 10% loyalty discount. Ready to order?"

[Note: Customer phone number 9876543210 was automatically masked 
 before processing to protect privacy]
```

***

## ✨ Core Features

### 🔒 **Privacy-First Architecture (Presidio PII Masking)**
- **Automatic Detection**: Identifies phone numbers, emails, names, credit cards
- **Pre-LLM Masking**: Sensitive data never reaches Groq/external APIs
- **95%+ Accuracy**: Microsoft Presidio handles 30+ entity types

**How it works**:
```python
# Input: "My number is 9876543210"
# After masking: "My number is <PHONE_NUMBER>"
# LLM receives masked version only
```

### 📚 **RAG Pipeline (Customer Context Retrieval)**
- **Vector Database**: ChromaDB stores customer profiles, order history, preferences
- **Semantic Search**: Finds relevant context based on conversation intent
- **Context Injection**: Retrieved data enriches LLM prompts for personalization

**RAG Flow**:
```
User Query → Embed query → Search ChromaDB → Retrieve top-3 docs 
→ Inject into prompt → Groq generates personalized response
```

### 🧠 **Conversation Memory (Session Management)**
- Session-based chat history using LangChain's `RunnableWithMessageHistory`
- Each user gets isolated storage (no cross-contamination)
- Maintains context across multiple conversation turns

### ⚡ **Production-Grade Engineering**
- **Error Handling**: Comprehensive validation + exception handlers
- **Logging**: Structured logs for debugging (request/response tracking)
- **Type Safety**: Pydantic schemas enforce API contracts
- **Auto Docs**: OpenAPI/Swagger UI at `/docs`

***

## 🏗️ Technical Architecture

### System Design (Phase 2 Complete)

```
┌─────────────────┐
│   User Query    │
│  "I'm cold +    │
│   9876543210"   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      FastAPI Endpoint (/chat)           │
│   • Pydantic validation                 │
│   • Session ID routing                  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│    PII Masking Layer (Presidio)         │
├─────────────────────────────────────────┤
│ • AnalyzerEngine detects entities       │
│ • AnonymizerEngine masks sensitive data │
│ • Output: "I'm cold + <PHONE_NUMBER>"   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│    RAG Retrieval (ChromaDB)             │
├─────────────────────────────────────────┤
│ • Embed masked query                    │
│ • Semantic search customer profiles     │
│ • Retrieve: Purchase history, prefs     │
│ • Context: "Loves hot cocoa, VIP tier"  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│    LangChain LCEL Chain                 │
├─────────────────────────────────────────┤
│ • ChatPromptTemplate                    │
│   - System: Retail assistant            │
│   - Context: RAG results                │
│   - History: MessagesPlaceholder        │
│   - Input: Masked user query            │
│                                         │
│ • RunnableWithMessageHistory            │
│   - Session store (isolated)            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│       Groq LLM Inference                │
│    Model: llama3-8b-8192                │
│    Prompt: System + Context + History   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│    Hyper-Personalized Response          │
│ "Based on your history, you love Hot    │
│  Cocoa. Starbucks 50m away, 10% off!"   │
└─────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Web Framework** | FastAPI 0.115.0 | Async-native, production-ready API |
| **LLM Inference** | Groq (GPT-OSS 120B) | <100ms latency, privacy-friendly |
| **AI Framework** | LangChain 0.3+ (LCEL) | Modern composition, RAG support |
| **PII Protection** | Microsoft Presidio 2.2 | Enterprise-grade entity detection |
| **Vector Database** | ChromaDB 0.5+ | Semantic search for RAG |
| **Embeddings** | OllamaEmbeddings | Local embedding generation |
| **Memory** | ChatMessageHistory | Session-based conversation tracking |
| **Validation** | Pydantic | Type-safe schemas |
| **Package Manager** | uv | 10-100x faster than pip |

***

## 🚀 Quick Start

### Prerequisites
- **Python** 3.12+
- **Groq API Key** ([Get free](https://console.groq.com/))
- **Ollama** (for local embeddings - optional)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/KshitijTardalkar/GroundTruthHackathon
cd GroundTruthHackathon

# 2. Install dependencies
uv venv && uv sync
# Make sure that uv is setup

# 3. Configure environment
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=openai/gpt-oss-120b
MEMORY_LENGTH=10
EOF

# 4. Index sample customer data (RAG setup)
python scripts/index_customer_data.py

# 5. Run server
python main.py
```

**Server**: `http://0.0.0.0:8000`  
**Docs**: `http://0.0.0.0:8000/docs`

***

## 📡 API Endpoints

### 1. Chat (Main Endpoint)
```bash
POST /chat
```

**Request**:
```json
{
  "message": "I'm cold, my number is 9876543210",
  "session_id": "customer-123"
}
```

**Response**:
```json
{
  "response": "I understand you're feeling cold! Based on your purchase history, you absolutely loved our Hot Cocoa last month. The Downtown Starbucks is just 50m away and open until 9 PM. I've applied your 10% VIP discount. Would you like me to place an order?",
  "session_id": "customer-123",
  "timestamp": "2025-12-03T11:40:00",
  "pii_masked": true,
  "context_retrieved": true
}
```

**Privacy Note**: Phone number `9876543210` was automatically masked to `<PHONE_NUMBER>` before processing.

### 2. Health Check
```bash
GET /
```

### 3. Clear Session
```bash
DELETE /session/{session_id}
```

### 4. List Active Sessions
```bash
GET /sessions
```

***

## 💻 Testing the System

### Test PII Masking
```bash
curl -X POST "http://0.0.0.0:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My email is john@example.com and phone 9876543210",
    "session_id": "privacy-test"
  }'
```

**Expected**: Response shows EVA understood intent without exposing raw PII.

### Test RAG Retrieval
```bash
curl -X POST "http://0.0.0.0:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want my usual order",
    "session_id": "customer-456"
  }'
```

**Expected**: EVA references past order history (retrieved from ChromaDB).

### Test Conversation Memory
```bash
# First message
curl -X POST "http://0.0.0.0:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I love hot chocolate", "session_id": "memory-test"}'

# Follow-up
curl -X POST "http://0.0.0.0:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Do you remember what I just said?", "session_id": "memory-test"}'
```

**Expected**: EVA recalls the previous message about hot chocolate.

***

## 🧩 Project Structure

```
GroundTruthHackathon/
├── config/
│   └── settings.py              # Environment + API key validation
├── modules/
│   ├── llm_handler.py           # LangChain LCEL chain + RAG
│   ├── pii_masker.py            # Presidio PII detection/masking
│   ├── rag_retriever.py         # ChromaDB retrieval logic
│   └── prompts.py               # System prompts
├── models/
│   └── schemas.py               # Pydantic request/response
├── data/
│   ├── customer_profiles/       # Sample customer PDFs
│   └── chroma_db/               # Vector database storage
├── scripts/
│   └── index_customer_data.py   # RAG indexing script
├── main.py                      # FastAPI app
├── .env                         # API keys (gitignored)
├── .gitignore
├── pyproject.toml               # uv dependencies
├── requirements.txt
└── README.md
```

--- 
## 🚀 What Makes EVA Different?

Unlike typical hackathon demos with hardcoded responses, EVA demonstrates **production-ready AI engineering**:

1. **Real Privacy Protection**: Presidio actually masks PII (not just claimed)
2. **Working RAG Pipeline**: ChromaDB retrieves relevant customer context
3. **Modern LangChain 0.3+**: LCEL patterns, not deprecated chains
4. **Session Isolation**: Proper multi-user architecture
5. **Comprehensive Logging**: Track PII masking + RAG retrieval + responses
