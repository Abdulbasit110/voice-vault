from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import os
import sys
import uuid
from dotenv import load_dotenv
import traceback

# Add the backend directory to Python path for Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="VoiceVault API", version="1.0.0")

# Initialize MongoDB connection on startup
@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection when server starts"""
    try:
        from services.mongodb_service import MongoDBService
        import os
        
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/voicevault")
        # Mask password in URI for logging
        print(mongodb_uri, "mongodb_uri")
        safe_uri = mongodb_uri
        if "@" in mongodb_uri:
            parts = mongodb_uri.split("@")
            if len(parts) == 2:
                safe_uri = f"mongodb://***@{parts[1]}"
        
        print(f"🔌 Connecting to MongoDB...")
        print(f"   URI: {safe_uri}")
        
        # Create singleton instance to establish connection
        mongo = MongoDBService()
        
        # Test connection
        mongo.client.admin.command('ping')
        
        # Get database info
        db_name = mongo.db.name
        server_info = mongo.client.server_info()
        
        print(f"✅ MongoDB connection established successfully!")
        print(f"   Database: {db_name}")
        print(f"   Server Version: {server_info.get('version', 'unknown')}")
        print(f"   Collections: transactions, portfolios, audio_files, circle_users, contacts")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print(f"⚠️  Server will continue but MongoDB features may not work")
        import traceback
        traceback.print_exc()

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection when server shuts down"""
    try:
        from services.mongodb_service import MongoDBService
        # Get the singleton instance and close connection
        mongo = MongoDBService()
        mongo.client.close()
        print("✅ MongoDB connection closed")
    except Exception as e:
        print(f"⚠️  Error closing MongoDB connection: {e}")

# CORS middleware for Next.js frontend
# Allow Vercel deployment URLs
cors_origins = [
    "http://localhost:3000",
    "http://139.59.152.104:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

# Add Vercel preview/production URLs if available
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    cors_origins.append(f"https://{vercel_url}")

next_public_url = os.getenv("NEXT_PUBLIC_URL")
if next_public_url:
    cors_origins.append(next_public_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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

# Contacts API Models
class AddContactRequest(BaseModel):
    wallet_address: str
    name: str

class ContactResponse(BaseModel):
    id: str
    wallet_address: str
    name: str
    created_at: str

# Query Enhancement Models
class EnhanceQueryRequest(BaseModel):
    query: str

class EnhanceQueryResponse(BaseModel):
    enhanced_query: str
    original_query: str
    extracted_name: Optional[str] = None  # Name extracted from query (if any)

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
    Also saves audio to MongoDB for record keeping
    """
    try:
        from utils.ElevenLabsSDK import get_elevenlabs_client
        from services.mongodb_service import MongoDBService
        
        # Save audio to MongoDB first
        mongo = MongoDBService()
        audio_id = mongo.save_audio_base64(
            request.audio,
            user_id="default_user",  # TODO: Get from auth/session
            metadata={"source": "stt", "format": "base64"}
        )
        print(f"✅ Audio saved to MongoDB with ID: {audio_id}")
        
        # Convert to text using ElevenLabs
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

@app.post("/api/agents/test")
async def test_agent(request: VoiceRequest):
    # Lazy import and initialization to avoid module-level crashes in Vercel
    from agents import Agent, Runner, function_tool
    
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
            user_data = circle.create_user(user_id)
        except Exception as e:
            # User might already exist, continue
            error_str = str(e).lower()
            if "already exists" not in error_str and "409" not in error_str:
                raise
            user_data = None
        
        # Step 1.5: Save user to MongoDB immediately after creation
        try:
            from services.mongodb_service import MongoDBService
            mongo = MongoDBService()
            mongo.save_circle_user_initial(
                user_id=user_id,
                metadata={"circle_user_data": user_data} if user_data else {}
            )
            print(f"✅ Circle user saved to MongoDB: {user_id}")
        except Exception as e:
            print(f"⚠️  Failed to save Circle user to MongoDB: {e}")
            # Don't fail the request if MongoDB save fails
        
        # Step 2: Get session token
        session = circle.get_session_token(user_id)
        
        # Step 3: Initialize user (creates wallet + PIN challenge)
        init_response = circle.initialize_user(
            session["user_token"],
            blockchains=["ETH-SEPOLIA"]
        )
        
        # Step 4: Try to get wallet address and save to MongoDB (may not be available until PIN is confirmed)
        try:
            from services.mongodb_service import MongoDBService
            wallets_response = circle.get_wallets(user_id)
            print(f"🔍 Wallets response: {wallets_response}")
            wallets = wallets_response.get("wallets", [])
            
            if wallets and len(wallets) > 0:
                wallet = wallets[0]
                wallet_address = wallet.get("address")
                wallet_id = wallet.get("id")
                blockchain = wallet.get("blockchain")
                
                if wallet_address:
                    # Save to MongoDB if wallet address is available
                    mongo = MongoDBService()
                    mongo.save_circle_user(
                        user_id=user_id,
                        wallet_address=wallet_address,
                        wallet_id=wallet_id,
                        blockchain=blockchain,
                        metadata={"app_id": circle.get_app_id()}
                    )
                    print(f"✅ Circle wallet saved to MongoDB: {user_id} -> {wallet_address}")
                else:
                    print(f"⚠️  Wallet created but address not yet available (PIN not confirmed): {user_id}")
            else:
                print(f"⚠️  No wallets found yet for user: {user_id} (will be available after PIN confirmation)")
        except Exception as e:
            print(f"⚠️  Failed to get/save wallet to MongoDB: {e}")
            import traceback
            traceback.print_exc()
            # Don't fail the request if MongoDB save fails
        
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
    Also updates MongoDB with wallet address when wallet is found
    Returns: wallet info if exists, null if not
    """
    try:
        from services.circle_wallet_service import get_circle_service
        from services.mongodb_service import MongoDBService
        
        circle = get_circle_service()
        wallets_response = circle.get_wallets(user_id)
        wallets = wallets_response.get("wallets", [])
        
        if not wallets:
            return WalletStatusResponse(exists=False, wallet=None)
        
        wallet = wallets[0]
        wallet_address = wallet.get("address")
        wallet_id = wallet.get("id")
        blockchain = wallet.get("blockchain")
        
        # Update MongoDB with wallet address if available
        if wallet_address:
            try:
                mongo = MongoDBService()
                mongo.save_circle_user(
                    user_id=user_id,
                    wallet_address=wallet_address,
                    wallet_id=wallet_id,
                    blockchain=blockchain,
                    metadata={"app_id": circle.get_app_id(), "updated_via": "status_check"}
                )
                print(f"✅ Wallet address updated in MongoDB: {user_id} -> {wallet_address}")
            except Exception as e:
                print(f"⚠️  Failed to update wallet in MongoDB: {e}")
        
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

# Contacts Endpoints
@app.post("/api/contacts/add")
async def add_contact(
    request: AddContactRequest,
    user_id: str = Query(..., description="User ID from localStorage")
):
    """
    Add a new contact for the user
    """
    try:
        from services.mongodb_service import MongoDBService
        import re
        
        # Validate wallet address format
        if not re.match(r"^0x[a-fA-F0-9]{40}$", request.wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        
        # Validate name
        if not request.name or not request.name.strip():
            raise HTTPException(status_code=400, detail="Name is required")
        
        mongo = MongoDBService()
        contact_id = mongo.add_contact(
            user_id=user_id,
            wallet_address=request.wallet_address,
            name=request.name.strip()
        )
        
        return {
            "success": True,
            "contact_id": contact_id,
            "message": "Contact added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding contact: {str(e)}")

@app.get("/api/contacts")
async def get_contacts(
    user_id: str = Query(..., description="User ID from localStorage"),
    name: Optional[str] = Query(None, description="Optional: Search contacts by name")
):
    """
    Get all contacts for a user, optionally filtered by name
    """
    try:
        from services.mongodb_service import MongoDBService
        
        mongo = MongoDBService()
        
        # If name is provided, search by name; otherwise get all
        if name:
            contacts = mongo.search_contacts_by_name(user_id, name)
        else:
            contacts = mongo.get_contacts(user_id)
        
        # Convert ObjectId to string and format dates
        formatted_contacts = []
        for contact in contacts:
            formatted_contacts.append({
                "id": str(contact["_id"]),
                "wallet_address": contact["wallet_address"],
                "name": contact["name"],
                "created_at": contact["created_at"].isoformat() if contact.get("created_at") else None
            })
        
        return {
            "contacts": formatted_contacts,
            "count": len(formatted_contacts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting contacts: {str(e)}")

# Query Enhancement Endpoint
@app.post("/api/query/enhance", response_model=EnhanceQueryResponse)
async def enhance_query(request: EnhanceQueryRequest):
    """
    Enhance and normalize user query to standard format
    Converts queries like "send 100 rupees to 0x..." to "send 100 usdc to 0x..."
    Uses simple LLM (not agents) for query normalization
    """
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""You are a query normalizer for cryptocurrency transactions. Your task is to normalize user queries into a standard format.

Standard format: "send [amount] usdc to [wallet_address]"

Rules:
1. Always convert amounts to USDC (convert rupees, dollars, USD, etc. to USDC)
2. Extract wallet addresses (they start with 0x and are 42 characters long)
3. Always use the format: "send [amount] usdc to [wallet_address]"
4. If no wallet address is found, keep the original query but normalize the currency to USDC
5. Preserve the exact amount mentioned by the user
6. Keep it simple and direct

Examples:
- "send 100 rupees to 0x1234..." → "send 100 usdc to 0x1234..."
- "transfer 50 dollars to 0xabcd..." → "send 50 usdc to 0xabcd..."
- "send 25 usdc to 0x5678..." → "send 25 usdc to 0x5678..."
- "100 rupees to john" → "send 100 usdc to john" (if no address, keep name)

User query: {request.query}

Normalized query:"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using mini for faster/cheaper responses
            messages=[
                {"role": "system", "content": "You are a query normalizer. Always respond with only the normalized query, nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent formatting
            max_tokens=100
        )
        
        enhanced_query = response.choices[0].message.content.strip()
        
        # Extract name from query (if it's not a wallet address)
        extracted_name = None
        # Check if query contains a name (not a wallet address starting with 0x)
        # Pattern: "send X usdc to [name]" where name is not a wallet address
        import re
        wallet_pattern = r"0x[a-fA-F0-9]{40}"
        if not re.search(wallet_pattern, enhanced_query.lower()):
            # Extract text after "to" - this might be a name
            match = re.search(r"to\s+([^\s]+(?:\s+[^\s]+)*)", enhanced_query, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip()
                # If it's not a number and not "usdc", it's likely a name
                if not potential_name.replace(".", "").replace(",", "").isdigit() and potential_name.lower() != "usdc":
                    extracted_name = potential_name
        
        return EnhanceQueryResponse(
            enhanced_query=enhanced_query,
            original_query=request.query,
            extracted_name=extracted_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
