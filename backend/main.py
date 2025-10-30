from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="VoiceVault API", version="1.0.0")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class VoiceRequest(BaseModel):
    text: Optional[str] = None
    audio: Optional[str] = None  # Base64 encoded audio

class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    message: str

class PortfolioResponse(BaseModel):
    total_value: float
    assets: list
    allocations: dict

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "VoiceVault API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

# Voice processing endpoint
@app.post("/api/voice/process")
async def process_voice(request: VoiceRequest):
    """
    Process voice command and return transaction result
    """
    try:
        # TODO: Integrate with ElevenLabs STT if audio provided
        # TODO: Send to agent system
        # TODO: Return transaction response
        
        return {
            "transaction_id": "mock_tx_123",
            "status": "success",
            "message": f"Processed voice command: {request.text or 'audio received'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get portfolio endpoint
@app.get("/api/portfolio")
async def get_portfolio():
    """
    Get current portfolio data
    """
    # TODO: Fetch from MongoDB
    return {
        "total_value": 18450.32,
        "assets": [
            {"name": "USDC", "value": 11070.19, "percentage": 60},
            {"name": "ETH", "value": 4612.58, "percentage": 25},
            {"name": "BTC", "value": 2767.55, "percentage": 15}
        ],
        "allocations": {
            "USDC": 60,
            "ETH": 25,
            "BTC": 15
        }
    }

# Get transactions endpoint
@app.get("/api/transactions")
async def get_transactions():
    """
    Get transaction history
    """
    # TODO: Fetch from MongoDB
    return {
        "transactions": [
            {
                "id": 1,
                "type": "buy",
                "asset": "ETH",
                "amount": 0.5,
                "value": 1072.61,
                "date": "2024-10-24",
                "status": "completed"
            }
        ],
        "total_count": 1
    }

# Agent execution endpoint
@app.post("/api/agents/execute")
async def execute_with_agents(request: VoiceRequest):
    """
    Execute transaction using AI agent system (mocked execution)
    """
    try:
        from backend.services.agents_runner import AgenticFlowRunner

        runner = AgenticFlowRunner()
        if not request.text and not request.audio:
            raise HTTPException(status_code=400, detail="text or audio is required")

        # For this MVP we only handle text. Audio-to-text handled in a later step.
        text = request.text or ""
        result = runner.run(text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

