# TSA Item Checker API

A FastAPI application that uses OpenRouter AI to determine if items are allowed in TSA check-in and carry-on baggage.

## Features

- 🚀 Fast API with automatic OpenAPI documentation
- 🤖 AI-powered TSA rule checking using OpenRouter
- 📦 Returns structured data: check-in allowed, carry-on allowed, and description
- 🌐 CORS enabled for web applications
- ☁️ Ready for deployment on Render

## API Endpoints

### POST /check-item
Check if an item is allowed by TSA.

**Request Body:**
```json
{
  "item": "laptop"
}
```

**Response:**
```json
{
  "item": "laptop",
  "check_in": true,
  "carry_on": true,
  "description": "Laptops are allowed in both checked and carry-on baggage. Must be removed from bag during security screening."
}
```

### GET /check-item/{item}
Alternative GET endpoint for checking items.

Example: `GET /check-item/shampoo`

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

3. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Deployment on Render

### Method 1: Using render.yaml (Recommended)

1. **Connect your repository to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository

2. **Set environment variables**
   - In Render dashboard, go to your service settings
   - Add environment variable: `OPENROUTER_API_KEY` with your API key

### Method 2: Manual Deployment

1. **Create a new Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service:**
   - **Name:** `tsa-item-checker`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set environment variables:**
   - `OPENROUTER_API_KEY`: Your OpenRouter API key

## OpenRouter Setup

1. **Get an API key:**
   - Go to [OpenRouter](https://openrouter.ai)
   - Sign up and get your API key

2. **Configure the API key:**
   - For local development: Add to `.env` file
   - For Render: Add as environment variable in dashboard

## Testing the API

### Using curl:
```bash
# POST request
curl -X POST "https://your-app.onrender.com/check-item" \
  -H "Content-Type: application/json" \
  -d '{"item": "shampoo"}'

# GET request
curl "https://your-app.onrender.com/check-item/shampoo"
```

### Using Python:
```python
import requests

response = requests.post(
    "https://your-app.onrender.com/check-item",
    json={"item": "shampoo"}
)
print(response.json())
```

## Model Configuration

The app uses `anthropic/claude-3.5-sonnet` by default. You can change the model in `main.py`:

```python
payload = {
    "model": "anthropic/claude-3.5-sonnet",  # Change this
    # ... other options: "openai/gpt-4", "google/gemini-pro", etc.
}
```

## Error Handling

The API includes comprehensive error handling:
- Invalid input validation
- OpenRouter API errors
- Network timeout handling
- JSON parsing fallbacks

## License

MIT License