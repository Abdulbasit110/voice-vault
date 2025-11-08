# VoiceVault 🎙️💰

A voice-controlled cryptocurrency wallet management platform powered by AI agents. VoiceVault enables users to manage their crypto portfolio, execute transactions, and interact with their wallet using natural language voice commands.

## 🌟 Features

### Core Capabilities
- **Voice-Controlled Transactions**: Execute crypto transactions using natural language voice commands
- **AI Agent System**: Multi-agent architecture for intelligent transaction processing
- **Circle Wallet Integration**: Secure wallet management via Circle's User Controlled Wallets API
- **Portfolio Management**: Real-time portfolio tracking and asset allocation visualization
- **Risk Analysis**: Automated risk assessment before transaction execution
- **Security Validation**: Multi-layer security checks for transaction safety
- **Contact Management**: Save and manage frequently used wallet addresses
- **Transaction History**: Complete audit trail of all transactions

### Technology Stack
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), OpenAI Agents Framework
- **Blockchain**: Circle User Controlled Wallets (ETH-SEPOLIA testnet)
- **Database**: MongoDB
- **Voice**: ElevenLabs Speech-to-Text & Text-to-Speech
- **AI**: OpenAI GPT-4o-mini for agent orchestration

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Agent System](#agent-system)
- [Deployment](#deployment)
- [Development](#development)

## 🏗️ Architecture

### System Overview

VoiceVault follows a multi-agent architecture where specialized AI agents work together to process voice commands:

```
User Voice Command
    ↓
ElevenLabs STT (Speech-to-Text)
    ↓
Planner Agent (Intent Extraction)
    ↓
Portfolio Manager Agent (Balance Check)
    ↓
Risk Analyst Agent (Risk Assessment)
    ↓
Security Validator Agent (Security Checks)
    ↓
Executor Agent (Transaction Creation)
    ↓
Circle Wallet API (PIN Confirmation)
    ↓
Auditor Agent (Transaction Verification)
    ↓
ElevenLabs TTS (Text-to-Speech Response)
```

### Project Structure

```
voice-vault/
├── app/                    # Next.js frontend pages
│   ├── page.tsx           # Main dashboard
│   ├── layout.tsx         # App layout
│   └── globals.css        # Global styles
├── components/             # React components
│   ├── voice-assistant.tsx
│   ├── portfolio-overview.tsx
│   ├── transaction-history.tsx
│   ├── wallet-setup.tsx
│   └── ...
├── backend/
│   ├── api/
│   │   └── main.py        # FastAPI application (Vercel deployment)
│   ├── main.py            # FastAPI application (local)
│   ├── Agents/            # AI Agent implementations
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── risk_analyst.py
│   │   ├── security_validator.py
│   │   ├── portfolio_manager.py
│   │   └── auditor.py
│   ├── services/          # Core services
│   │   ├── agents_runner.py
│   │   ├── circle_wallet_service.py
│   │   └── mongodb_service.py
│   ├── tools/             # Agent tools
│   │   └── agent_tools.py
│   ├── utils/             # Utilities
│   │   └── ElevenLabsSDK.py
│   ├── models/            # Data models
│   │   ├── portfolio.py
│   │   └── transaction.py
│   ├── requirements.txt   # Python dependencies
│   └── vercel.json        # Vercel configuration
└── README.md
```

## 🚀 Installation

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **MongoDB** (local or cloud instance)
- API Keys:
  - OpenAI API Key
  - ElevenLabs API Key
  - Circle API Key

### Frontend Setup

```bash
cd voice-vault
npm install
```

### Backend Setup

```bash
cd voice-vault/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Voice (ElevenLabs)
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# AI Agents (OpenAI)
OPENAI_API_KEY=your_openai_api_key

# Blockchain (Circle)
CIRCLE_API_KEY=your_circle_api_key

# Database
MONGODB_URI=mongodb://localhost:27017/voicevault
# Or for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/voicevault

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
# For production:
# NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### MongoDB Collections

The application automatically creates the following collections:
- `transactions` - Transaction history
- `portfolios` - User portfolio data
- `audio_files` - Voice recordings
- `circle_users` - Circle wallet user data
- `contacts` - User contacts (wallet addresses)

## 💻 Usage

### Starting the Development Servers

#### Backend (FastAPI)

```bash
cd voice-vault/backend
source venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

#### Frontend (Next.js)

```bash
cd voice-vault
npm run dev
```

The frontend will be available at `http://localhost:3000`

### First-Time Setup

1. **Create Wallet**: On first launch, the app will prompt you to create a Circle wallet
2. **Set PIN**: Complete PIN setup via Circle's WebSDK
3. **Fund Wallet**: Add testnet USDC to your wallet (for ETH-SEPOLIA testnet)
4. **Add Contacts**: Save frequently used wallet addresses

### Voice Commands

VoiceVault supports natural language commands:

- **Transfer**: "Send 100 USDC to 0x..."
- **Transfer to Contact**: "Send 50 USDC to John"
- **Portfolio Check**: "Show my portfolio"
- **Transaction History**: "Show my transactions"

### Example Workflow

1. Click the microphone button in the Voice Assistant component
2. Speak your command: "Send 10 USDC to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
3. The system processes through agents:
   - Planner extracts intent
   - Portfolio Manager checks balance
   - Risk Analyst evaluates risk
   - Security Validator validates address
   - Executor creates transaction
4. Confirm transaction with PIN via Circle WebSDK
5. Receive voice confirmation

## 📡 API Documentation

### Base URL

- **Local**: `http://localhost:8000`
- **Production**: Configure via `NEXT_PUBLIC_API_URL`

### Key Endpoints

#### Health Check
```
GET /health
```

#### Voice Processing
```
POST /api/elevenlabs/stt
Body: { "audio": "base64_encoded_audio" }
Response: { "text": "transcribed_text" }

POST /api/elevenlabs/tts
Body: { "text": "text_to_speak", "voice_id": "optional_voice_id" }
Response: audio/mpeg file
```

#### Agent Execution
```
POST /api/agents/execute
Body: { "text": "user_command", "audio": "optional_base64_audio" }
Query: ?user_id=optional_user_id
Response: Transaction result with challenge_id for PIN confirmation
```

#### Wallet Management
```
POST /api/wallet/create
Query: ?user_id=optional_user_id
Response: { "user_id", "app_id", "challenge_id", "user_token", "encryption_key" }

GET /api/wallet/status
Query: ?user_id=user_id
Response: { "exists": true, "wallet": {...} }

GET /api/wallet/balance
Query: ?user_id=user_id
Response: { "tokenBalances": [...], "wallet_id": "..." }

GET /api/wallet/transactions
Query: ?user_id=user_id&page_size=50&page_before=cursor&page_after=cursor
Response: { "transactions": [...], "page_before": "...", "page_after": "..." }
```

#### Contacts
```
POST /api/contacts/add
Body: { "wallet_address": "0x...", "name": "Contact Name" }
Query: ?user_id=user_id
Response: { "success": true, "contact_id": "..." }

GET /api/contacts
Query: ?user_id=user_id&name=optional_search
Response: { "contacts": [...], "count": 10 }
```

#### Query Enhancement
```
POST /api/query/enhance
Body: { "query": "send 100 rupees to 0x..." }
Response: { "enhanced_query": "send 100 usdc to 0x...", "original_query": "...", "extracted_name": null }
```

## 🤖 Agent System

VoiceVault uses a sequential multi-agent workflow:

### 1. Planner Agent
- **Purpose**: Extract intent from natural language
- **Output**: Structured command (action, asset, amount, destination)
- **Model**: GPT-4o-mini

### 2. Portfolio Manager Agent
- **Purpose**: Check wallet balance and portfolio status
- **Output**: Current portfolio data (balances, prices, total value)
- **Data Source**: Circle Wallet API

### 3. Risk Analyst Agent
- **Purpose**: Assess transaction risk
- **Checks**:
  - Sufficient balance
  - Percentage of portfolio
  - Transaction size limits
- **Output**: Risk assessment with approval/rejection

### 4. Security Validator Agent
- **Purpose**: Validate transaction security
- **Checks**:
  - Wallet address format
  - Known scam addresses
  - Transaction patterns
- **Output**: Security validation result

### 5. Executor Agent
- **Purpose**: Create transaction challenge
- **Action**: Calls Circle API to create transfer challenge
- **Output**: Challenge ID for PIN confirmation

### 6. Auditor Agent
- **Purpose**: Verify transaction completion
- **Action**: Checks transaction status after confirmation
- **Output**: Transaction confirmation details

## 🚢 Deployment

### Vercel Deployment

1. Connect GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `.next`
4. Configure environment variables:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL

### Environment Variables for Production

Ensure all environment variables are set in your deployment platform:
- `ELEVENLABS_API_KEY`
- `OPENAI_API_KEY`
- `CIRCLE_API_KEY`
- `MONGODB_URI`
- `NEXT_PUBLIC_API_URL`

## 🛠️ Development

### Code Structure

- **Agents**: Located in `backend/Agents/` - Each agent is a separate module
- **Services**: Core business logic in `backend/services/`
- **Tools**: Agent tools in `backend/tools/`
- **Components**: React components in `components/`

### Adding New Features

1. **New Agent**: Create agent file in `backend/Agents/` and add to `agents_runner.py`
2. **New API Endpoint**: Add route in `backend/api/main.py`
3. **New Component**: Create component in `components/` and import in `app/page.tsx`

### Debugging

- Backend logs: Check console output from uvicorn
- Frontend logs: Check browser console
- MongoDB: Use MongoDB Compass or CLI to inspect collections
- Circle API: Check Circle dashboard for transaction status

## 🔒 Security Considerations

- **API Keys**: Never commit API keys to version control
- **PIN Security**: PIN confirmation handled by Circle WebSDK (client-side)
- **Wallet Security**: Private keys managed by Circle (non-custodial)
- **CORS**: Configured for specific origins
- **Input Validation**: All user inputs validated before processing

## 🙏 Acknowledgments

- **Circle**: User Controlled Wallets API
- **ElevenLabs**: Speech-to-Text and Text-to-Speech
- **OpenAI**: Agents Framework
- **Next.js & FastAPI**: Web frameworks

---

**Note**: This project uses ETH-SEPOLIA testnet by default. Ensure you're using testnet tokens for development and testing.
