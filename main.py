from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Optional
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="TSA Item Checker API",
    description="API to check if items are allowed in TSA check-in and carry-on",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ItemRequest(BaseModel):
    item: str

class TSAResponse(BaseModel):
    item: str
    check_in: bool
    carry_on: bool
    description: str
    database_id: Optional[int] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Supabase configuration
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://bruqzbaiwogvcfxapixk.supabase.co")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJydXF6YmFpd29ndmNmeGFwaXhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MjI1MTIsImV4cCI6MjA2OTk5ODUxMn0.8MHnk-ec65KT0oJab_wXCQB1WrNWAblI8MbxP75XNMg")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Set up logging
logging.basicConfig(level=logging.INFO)

async def query_openrouter(item: str) -> dict:
    """Query OpenRouter API to get TSA information about an item"""
    
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    prompt = f"""
    You are a TSA (Transportation Security Administration) expert. For the item "{item}", provide information about:
    1. Whether it's allowed in checked baggage (check-in)
    2. Whether it's allowed in carry-on baggage
    3. A brief description of any restrictions or important details

    Respond ONLY with a valid JSON object in this exact format:
    {{
        "check_in": true/false,
        "carry_on": true/false,
        "description": "Brief explanation of TSA rules and any restrictions"
    }}
    
    Base your response on official TSA guidelines. If uncertain, err on the side of caution and provide relevant details in the description.
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-name.onrender.com",  # Replace with your actual domain
        "X-Title": "TSA Item Checker"
    }
    
    payload = {
        "model": "anthropic/claude-3.5-sonnet",  # You can change this model
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Parse the JSON response from the AI
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Fallback parsing if the response isn't perfect JSON
                return {
                    "check_in": False,
                    "carry_on": False,
                    "description": f"Could not parse response for {item}. Please check with official TSA guidelines."
                }
                
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"OpenRouter API error: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {e}")

async def store_tsa_response_in_supabase(item: str, check_in: bool, carry_on: bool, description: str) -> Optional[dict]:
    """Store the TSA response in Supabase database"""
    try:
        data = {
            "item": item,
            "check_in": check_in,
            "carry_on": carry_on,
            "description": description
        }
        
        result = supabase.table("tsa_responses").insert(data).execute()
        logging.info(f"Successfully stored TSA response for item: {item}")
        return result.data[0] if result.data else None
        
    except Exception as e:
        logging.error(f"Failed to store TSA response in Supabase for item {item}: {str(e)}")
        # Don't raise an exception here to avoid breaking the API response
        # Log the error and continue
        return None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "TSA Item Checker API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "TSA Item Checker API"}

@app.post("/check-item", response_model=TSAResponse)
async def check_tsa_item(request: ItemRequest):
    """
    Check if an item is allowed in TSA check-in and carry-on baggage
    
    Args:
        request: ItemRequest containing the item name to check
        
    Returns:
        TSAResponse with check-in, carry-on allowance and description
    """
    try:
        if not request.item or not request.item.strip():
            raise HTTPException(status_code=400, detail="Item name cannot be empty")
        
        item = request.item.strip()
        
        # Query OpenRouter API
        result = await query_openrouter(item)
        
        # Extract response data
        check_in = result.get("check_in", False)
        carry_on = result.get("carry_on", False)
        description = result.get("description", "No information available")
        
        # Store in Supabase
        supabase_result = await store_tsa_response_in_supabase(item, check_in, carry_on, description)
        database_id = supabase_result.get("id") if supabase_result else None
        
        return TSAResponse(
            item=item,
            check_in=check_in,
            carry_on=carry_on,
            description=description,
            database_id=database_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/check-item/{item}")
async def check_tsa_item_get(item: str):
    """
    GET endpoint to check TSA item allowance
    
    Args:
        item: The item name to check
        
    Returns:
        TSAResponse with check-in, carry-on allowance and description
    """
    request = ItemRequest(item=item)
    return await check_tsa_item(request)

@app.get("/stored-responses")
async def get_stored_responses(limit: int = 50, offset: int = 0):
    """
    Get stored TSA responses from Supabase
    
    Args:
        limit: Maximum number of responses to return (default: 50)
        offset: Number of responses to skip (default: 0)
        
    Returns:
        List of stored TSA responses
    """
    try:
        result = supabase.table("tsa_responses")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        return {
            "responses": result.data,
            "count": len(result.data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stored responses: {str(e)}")

@app.get("/stored-responses/{item}")
async def get_stored_responses_by_item(item: str):
    """
    Get stored TSA responses for a specific item
    
    Args:
        item: The item name to search for
        
    Returns:
        List of stored responses for the specified item
    """
    try:
        result = supabase.table("tsa_responses")\
            .select("*")\
            .eq("item", item)\
            .order("created_at", desc=True)\
            .execute()
        
        return {
            "item": item,
            "responses": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve responses for item {item}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)