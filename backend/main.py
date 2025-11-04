from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import os
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
async def execute_with_agents(request: VoiceRequest):
    print(request)
    # return request
    """
    Execute transaction using AI agent system (agent-based sequential workflow)
    """
    try:
        from services.agents_runner import AgentRunner

        if not request.text:
            raise HTTPException(status_code=400, detail="text or audio is required")

        text = request.text or ""
        print(text, "going to the agent runner")
        runner = AgentRunner()
        result = await runner.run(text)
        print(result, "result from the agent runner")
        return result
    except HTTPException:
        raise
    except Exception as e:
        print("❌ Full error trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


