from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
import traceback




# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="VoiceVault API", version="1.0.0")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
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

# class PortfolioResponse(BaseModel):
#     total_value: float
#     assets: list
#     allocations: dict

# ElevenLabs API Models
class STTRequest(BaseModel):
    audio: str  # Base64 encoded audio

class STTResponse(BaseModel):
    text: str

class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None

# Wallet API Models
class WalletCreateResponse(BaseModel):
    user_id: str
    app_id: str
    challenge_id: str
    user_token: str
    encryption_key: str
    message: str

class WalletStatusResponse(BaseModel):
    exists: bool
    wallet: Optional[dict] = None

class TransactionListResponse(BaseModel):
    transactions: list
    page_before: Optional[str] = None
    page_after: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "VoiceVault API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


# ElevenLabs API Endpoints
@app.post("/api/elevenlabs/stt", response_model=STTResponse)
async def speech_to_text(request: STTRequest):
    """
    Convert audio to text using ElevenLabs Speech-to-Text API
    """
    try:
        from utils.ElevenLabsSDK import get_elevenlabs_client
        
        client = get_elevenlabs_client()
        text = client.convert_base64_audio_to_text(request.audio)
        
        return STTResponse(text=text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT Error: {str(e)}")

@app.post("/api/elevenlabs/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using ElevenLabs Text-to-Speech API
    """
    try:
        from utils.ElevenLabsSDK import get_elevenlabs_client
        
        client = get_elevenlabs_client()
        audio_bytes = client.text_to_speech(text=request.text, voice_id=request.voice_id)
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")
        

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


#  test

class Weather(BaseModel):
    city: str
    temperature_range: str
    conditions: str


@function_tool
def get_weather(city: str) -> Weather:
    print("[debug] get_weather called")
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind")

story_agent = Agent(
    name="story_agent",
    instructions="Get the weather for the given city.",
    output_type=str,
    tools=[get_weather]
)

@app.post("/api/agents/test")
async def test_agent(request: VoiceRequest):
    result = await Runner.run(story_agent, request.text)
    return result.final_output

# Agent execution endpoint
@app.post("/api/agents/execute")
async def execute_with_agents(
    request: VoiceRequest,
    user_id: Optional[str] = Query(None, description="User ID for wallet operations")
):
    print(request)
    # return request
    """
    Execute transaction using AI agent system (agent-based sequential workflow)
    Returns challengeId if transaction requires PIN confirmation
    """
    try:
        from services.agents_runner import AgentRunner

        if not request.text:
            raise HTTPException(status_code=400, detail="text or audio is required")

        text = request.text or ""
        print(text, "going to the agent runner")
        runner = AgentRunner()
        result = await runner.run(text, user_id=user_id)
        print(result, "result from the agent runner")
        return result
    except HTTPException:
        raise
    except Exception as e:
        print("❌ Full error trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Wallet Endpoints
@app.post("/api/wallet/create", response_model=WalletCreateResponse)
async def create_wallet(user_id: Optional[str] = Query(None, description="Optional user ID. If not provided, a new UUID will be generated")):
    """
    Create Circle wallet for user (one-time setup)
    Returns: challengeId, userToken, encryptionKey, appId for frontend WebSDK
    """
    try:
        from services.circle_wallet_service import get_circle_service
        
        circle = get_circle_service()
        
        # Generate user ID if not provided
        if not user_id:
            user_id = str(uuid.uuid4())
        
        # Step 1: Create user
        try:
            circle.create_user(user_id)
        except Exception as e:
            # User might already exist, continue
            error_str = str(e).lower()
            if "already exists" not in error_str and "409" not in error_str:
                raise
        
        # Step 2: Get session token
        session = circle.get_session_token(user_id)
        
        # Step 3: Initialize user (creates wallet + PIN challenge)
        init_response = circle.initialize_user(
            session["user_token"],
            blockchains=["ETH-SEPOLIA"]
        )
        
        # Get App ID
        app_id = circle.get_app_id()
        return WalletCreateResponse(
            user_id=user_id,
            app_id=app_id,
            challenge_id=init_response["challengeId"],
            user_token=session["user_token"],
            encryption_key=session["encryption_key"],
            message="Wallet initialized. Complete PIN setup via WebSDK."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/status", response_model=WalletStatusResponse)
async def get_wallet_status(user_id: str = Query(..., description="User ID to check wallet status")):
    """
    Check if wallet exists and is ready
    Returns: wallet info if exists, null if not
    """
    try:
        from services.circle_wallet_service import get_circle_service
        
        circle = get_circle_service()
        wallets_response = circle.get_wallets(user_id)
        wallets = wallets_response.get("wallets", [])
        
        if not wallets:
            return WalletStatusResponse(exists=False, wallet=None)
        
        wallet = wallets[0]
        return WalletStatusResponse(
            exists=True,
            wallet={
                "id": wallet["id"],
                "address": wallet["address"],
                "blockchain": wallet["blockchain"],
                "state": wallet["state"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/app-id")
async def get_app_id():
    """
    Get Circle App ID for frontend
    """
    try:
        from services.circle_wallet_service import get_circle_service
        
        circle = get_circle_service()
        app_id = circle.get_app_id()
        return {"app_id": app_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/balance")
async def get_wallet_balance(user_id: str = Query(..., description="User ID")):
    """
    Get wallet balance for a user
    Returns: Token balances with amounts and token info
    """
    try:
        from services.circle_wallet_service import get_circle_service
        
        circle = get_circle_service()
        
        # Get user's wallet
        wallets_response = circle.get_wallets(user_id)
        wallets = wallets_response.get("wallets", [])
        
        if not wallets:
            return {"tokenBalances": [], "wallet_id": None}
        
        wallet_id = wallets[0]["id"]
        
        # Get user session token (required for balance queries)
        session = circle.get_session_token(user_id)
        user_token = session["user_token"]
        
        # Get wallet balance
        balance_data = circle.get_wallet_balance(
            wallet_id=wallet_id,
            user_token=user_token,
            include_all=True
        )
        
        return {
            "wallet_id": wallet_id,
            "wallet_address": wallets[0]["address"],
            **balance_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/transactions", response_model=TransactionListResponse)
async def list_transactions(
    user_id: str = Query(..., description="User ID"),
    page_size: int = Query(50, description="Number of transactions per page"),
    page_before: Optional[str] = Query(None, description="Cursor for pagination (before)"),
    page_after: Optional[str] = Query(None, description="Cursor for pagination (after)")
):
    """
    List transactions for a user
    Returns: List of transactions with pagination info
    """
    try:
        from services.circle_wallet_service import get_circle_service
        
        circle = get_circle_service()
        
        # Get user session token (required for transaction queries)
        session = circle.get_session_token(user_id)
        user_token = session["user_token"]
        
        # List transactions
        transactions_data = circle.list_transactions(
            user_id=user_id,
            user_token=user_token,
            page_size=page_size,
            page_before=page_before,
            page_after=page_after
        )
        
        return TransactionListResponse(
            transactions=transactions_data.get("transactions", []),
            page_before=transactions_data.get("pageBefore"),
            page_after=transactions_data.get("pageAfter")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    user_id: str = Query(..., description="User ID")
):
    """
    Get a single transaction by ID
    Returns: Transaction details
    """
    try:
        from services.circle_wallet_service import get_circle_service
        
        circle = get_circle_service()
        
        # Get user session token (required for transaction queries)
        session = circle.get_session_token(user_id)
        user_token = session["user_token"]
        
        # Get transaction
        transaction_data = circle.get_transaction(
            transaction_id=transaction_id,
            user_token=user_token
        )
        
        return transaction_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


