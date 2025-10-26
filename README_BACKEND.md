# VoiceVault Backend Setup

## Quick Start

1. **Navigate to backend directory:**
   ```bash
   cd voice-vault/backend
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Run the server:**
   ```bash
   python main.py
   # or
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/portfolio` - Get portfolio data
- `GET /api/transactions` - Get transaction history
- `POST /api/voice/process` - Process voice command
- `POST /api/agents/execute` - Execute with agents

## Next Steps

1. Add ElevenLabs integration (STT/TTS)
2. Implement AI agents (Planner, Risk, Executor)
3. Integrate Circle User Controlled Wallets
4. Connect to Arc blockchain
5. Add MongoDB for persistence

## Environment Variables

See `env.example` for all required variables:
- ELEVENLABS_API_KEY
- OPENAI_API_KEY
- CIRCLE_API_KEY
- CIRCLE_ENTITY_SECRET
- ARC_RPC_URL
- MONGODB_URI

