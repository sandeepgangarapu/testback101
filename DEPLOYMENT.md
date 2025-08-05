# Deployment Guide for TSA Item Checker API

## Quick Start Steps

### 1. Get OpenRouter API Key
1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the key (you'll need it for deployment)

### 2. Deploy to Render

#### Option A: One-Click Deploy (Recommended)
1. Fork/clone this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file
6. In the environment variables section, add:
   - Key: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key from step 1
7. Click "Apply" to deploy

#### Option B: Manual Deploy
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `tsa-item-checker` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable:
   - **Key**: `OPENROUTER_API_KEY`
   - **Value**: Your OpenRouter API key
6. Click "Create Web Service"

### 3. Test Your Deployment

Once deployed, you'll get a URL like `https://your-app-name.onrender.com`

#### Test with curl:
```bash
# Health check
curl https://your-app-name.onrender.com/health

# Test an item
curl -X POST "https://your-app-name.onrender.com/check-item" \
  -H "Content-Type: application/json" \
  -d '{"item": "laptop"}'

# Test with GET
curl "https://your-app-name.onrender.com/check-item/shampoo"
```

#### Use the interactive docs:
Visit `https://your-app-name.onrender.com/docs` for automatic API documentation

### 4. Integration Examples

#### JavaScript/React:
```javascript
const checkItem = async (item) => {
  const response = await fetch('https://your-app-name.onrender.com/check-item', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ item }),
  });
  return await response.json();
};

// Usage
checkItem('laptop').then(result => {
  console.log(`Check-in: ${result.check_in}`);
  console.log(`Carry-on: ${result.carry_on}`);
  console.log(`Description: ${result.description}`);
});
```

#### Python:
```python
import requests

def check_tsa_item(item, api_url="https://your-app-name.onrender.com"):
    response = requests.post(
        f"{api_url}/check-item",
        json={"item": item}
    )
    return response.json()

# Usage
result = check_tsa_item("shampoo")
print(f"Item: {result['item']}")
print(f"Check-in allowed: {result['check_in']}")
print(f"Carry-on allowed: {result['carry_on']}")
print(f"Details: {result['description']}")
```

## Troubleshooting

### Common Issues:

1. **"OpenRouter API key not configured"**
   - Make sure you've added the `OPENROUTER_API_KEY` environment variable in Render
   - Verify the API key is correct and has sufficient credits

2. **Slow first response**
   - Render free tier apps go to sleep after inactivity
   - First request after sleep takes ~30 seconds
   - Consider upgrading to paid plan for production use

3. **API timeout errors**
   - OpenRouter responses can take 10-30 seconds
   - This is normal for AI processing
   - Frontend should show loading indicators

4. **CORS errors**
   - The API includes CORS middleware allowing all origins
   - If issues persist, check your frontend's request format

### Monitoring:
- Check Render logs in the dashboard for errors
- Use the `/health` endpoint for uptime monitoring
- Monitor OpenRouter usage in their dashboard

### Cost Optimization:
- OpenRouter charges per API call (~$0.001-0.01 per request)
- Consider implementing request caching for common items
- Monitor usage to avoid unexpected bills

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key | `sk-or-v1-abc123...` |
| `PORT` | No | Port number (auto-set by Render) | `8000` |

## Model Configuration

To change the AI model, edit `main.py`:

```python
payload = {
    "model": "anthropic/claude-3.5-sonnet",  # Current default
    # Other options:
    # "openai/gpt-4-turbo"
    # "openai/gpt-3.5-turbo"
    # "google/gemini-pro"
    # "meta-llama/llama-2-70b-chat"
}
```

Visit [OpenRouter Models](https://openrouter.ai/models) for full list and pricing.