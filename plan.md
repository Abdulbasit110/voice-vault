# VoiceVault - AI-Powered Voice DeFi Platform

## 🎯 Project Goal
Build a voice-autonomous DeFi system that executes blockchain transactions via voice commands, using multi-agent AI orchestration.

## 🏆 Hackathon: LabLab.ai AI Agents + Arc & USDC
**Event**: Oct 27 - Nov 8, 2025
**Submission Deadline**: Nov 8, 11:59 PM EST

### Core Requirements
- ✅ **Arc Blockchain**: EVM-compatible Layer-1, USDC as native gas
- ✅ **Circle User Controlled Wallets**: Wallet management & authentication
- ✅ **AI Agents**: Multi-agent system for autonomous transaction execution
- ✅ **Voice Interface**: ElevenLabs for STT/TTS
- ✅ **USDC Transactions**: Native stablecoin for all operations

## 🏗️ Architecture

### Flow
```
User Voice → ElevenLabs STT → Text
    ↓
Backend FastAPI → OpenAI Agents SDK → Multi-Agent System
    ↓
   ├─ Planner Agent: Parse voice command → transaction intent
   ├─ Risk Analyst Agent: Analyze portfolio safety & market conditions
   ├─ Portfolio Manager Agent: Check balance & allocation
   ├─ Security Validator Agent: Validate transaction parameters
   ├─ Transaction Executor Agent: Execute via Circle API → Arc Blockchain
   └─ Auditor Agent: Verify transaction on-chain
    ↓
MongoDB Update (portfolio, transactions)
    ↓
Response → ElevenLabs TTS → Voice Audio
    ↓
Frontend UI Updates (transactions, portfolio, charts)
```

### Technology Stack
**Frontend**:
- Next.js 16 (React 19)
- Framer Motion (animations)
- Tailwind CSS
- lucide-react (icons)

**Backend**:
- FastAPI (Python)
- OpenAI Agents SDK (multi-agent orchestration)
- Circle User Controlled Wallets SDK (@circle-fin/user-controlled-wallets)
- ElevenLabs (voice STT/TTS)
- MongoDB (portfolio & transaction storage)
- ethers.js (Arc blockchain interaction)

**Blockchain**:
- Arc Network (EVM-compatible Layer-1)
- USDC (native gas & transactions)

## 📋 Implementation Phases

### Phase 1: Foundation (Days 1-3)
- [ ] Setup FastAPI backend structure
- [ ] Configure Arc blockchain connection (ethers.js)
- [ ] Integrate Circle User Controlled Wallets SDK
- [ ] Setup MongoDB connection & models
- [ ] Basic agent structure (Planner, Executor)

### Phase 2: Voice Integration (Days 4-6)
- [ ] ElevenLabs API integration (STT)
- [ ] Voice command processing
- [ ] ElevenLabs TTS for responses
- [ ] Voice assistant UI connection

### Phase 3: AI Agents (Days 7-8)
- [ ] **Planner Agent**: Voice → transaction parameters
- [ ] **Risk Analyst Agent**: Portfolio safety checks
- [ ] **Portfolio Manager Agent**: Balance & allocation verification
- [ ] **Security Validator Agent**: Transaction validation
- [ ] **Executor Agent**: Circle API + Arc blockchain execution
- [ ] **Auditor Agent**: On-chain verification

### Phase 4: Integration & Polish (Days 9-10)
- [ ] Connect frontend ↔ backend
- [ ] Real-time transaction updates
- [ ] Portfolio visualization updates
- [ ] Error handling & user feedback
- [ ] Demo video recording

### Phase 5: Submission (Day 11)
- [ ] Final testing on Arc testnet
- [ ] Deploy live demo
- [ ] Prepare README & documentation
- [ ] Submit to LabLab.ai

## 🛠️ Backend Structure (to be created)
```
backend/
├── main.py                    # FastAPI app entry
├── agents/
│   ├── planner.py             # Parses voice → transaction
│   ├── risk_analyst.py        # Portfolio risk analysis
│   ├── portfolio_manager.py    # Balance & allocation checks
│   ├── security_validator.py  # Transaction validation
│   ├── executor.py            # Circle API → Arc execution
│   └── auditor.py             # On-chain verification
├── services/
│   ├── elevenlabs_service.py  # Voice STT/TTS
│   ├── circle_wallet_service.py # Circle wallet operations
│   ├── arc_blockchain_service.py # Arc transactions
│   └── mongodb_service.py     # Database operations
├── models/
│   ├── transaction.py         # Transaction models
│   └── portfolio.py           # Portfolio models
├── tools/
│   └── agent_tools.py         # Tools for agents
└── requirements.txt
```

## 🎨 Frontend Components (already ready ✅)
- Voice Assistant (`voice-assistant.tsx`)
- Portfolio Overview (`portfolio-overview.tsx`)
- Transaction History (`transaction-history.tsx`)
- Asset List (`asset-list.tsx`)
- Risk Analysis (`risk-analysis.tsx`)
- AI Insights (`ai-insights.tsx`)

## 🔑 Environment Variables Needed
```
# Voice
ELEVENLABS_API_KEY=

# AI Agents
OPENAI_API_KEY=

# Blockchain - Circle
CIRCLE_API_KEY=
CIRCLE_ENTITY_SECRET=

# Blockchain - Arc
ARC_RPC_URL=
PRIVATE_KEY=

# Database
MONGODB_URI=

# Frontend
NEXT_PUBLIC_API_URL=
```

## 📝 TODO (for implementation)
1. ✅ Frontend UI
2. ⏳ Backend FastAPI setup
3. ⏳ Agent orchestration (OpenAI Agents SDK)
4. ⏳ ElevenLabs voice integration
5. ⏳ Circle wallet integration
6. ⏳ Arc blockchain integration
7. ⏳ MongoDB models & queries
8. ⏳ Real-time frontend updates

## 🎯 Key Features for Hackathon
1. **Voice-Activated Transactions**: "Buy 0.5 ETH with 25% of USDC"
2. **Multi-Agent Safety**: Agents validate before execution
3. **Real-Time Portfolio**: Live updates after transactions
4. **Risk Analysis**: AI-driven portfolio health checks
5. **Blockchain Integration**: Arc + USDC native
6. **Circle Wallets**: Secure wallet management

## 📊 Judging Criteria Alignment
- ✅ **Innovation**: Voice + AI Agents + Blockchain
- ✅ **Technical Execution**: Multi-agent architecture
- ✅ **User Experience**: Voice-first, intuitive
- ✅ **Impact**: Real-world DeFi use case
- ✅ **Alignment**: Arc + USDC + AI Agents

**Additional Notes**:
- Focus on ElevenLabs integration for Best Use of ElevenLabs prize
- Emphasize Arc network + USDC for Best Use of Arc prizes
- Showcase multi-agent safety system
