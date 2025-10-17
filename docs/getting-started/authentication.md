# Authentication

Shadai uses API keys for secure authentication. This guide will help you set up your credentials.

## Getting Your API Key

1. Log in to your Shadai web application
2. Navigate to **API Keys** page (accessible from your sidebar)
3. Click **Create New Key**
4. Give your key a descriptive name
5. Copy your API key immediately (you'll only see it once!)

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
SHADAI_API_KEY=your_api_key_here
SHADAI_BASE_URL=https://api.shadai.com  # Optional
```

Load it in your code:

```python
from dotenv import load_dotenv
from shadai import Shadai

load_dotenv()

# API key loaded automatically from environment
async with Shadai(name="my-session") as shadai:
    async for chunk in shadai.query("Hello world"):
        print(chunk, end="")
```

### Method 2: Direct Initialization

Pass the API key directly (not recommended for production):

```python
from shadai import Shadai

shadai = Shadai(api_key="your_api_key_here")
```

### Method 3: Context Manager with API Key

```python
from shadai import Shadai

async with Shadai(name="my-session", api_key="your_api_key") as shadai:
    async for chunk in shadai.query("Hello"):
        print(chunk, end="")
```

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SHADAI_API_KEY` | Your API key | - | ✅ |
| `SHADAI_BASE_URL` | API base URL | `http://localhost` | ❌ |
| `SHADAI_TIMEOUT` | Request timeout (seconds) | `30` | ❌ |

## Security Best Practices

### ✅ Do This

- Store API keys in `.env` files
- Add `.env` to `.gitignore`
- Use different keys for dev/staging/production
- Rotate keys regularly
- Use environment-specific secrets management (AWS Secrets Manager, etc.)

### ❌ Don't Do This

- Hard-code API keys in source code
- Commit API keys to version control
- Share API keys via email or chat
- Use the same key across all environments
- Store keys in plain text files

## Example .gitignore

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# API keys
*_api_key*
secrets/
```

## Testing Authentication

Verify your authentication is working:

```python
import asyncio
from shadai import Shadai

async def test_auth():
    try:
        async with Shadai(name="auth-test") as shadai:
            # Simple health check
            health = await shadai.client.health()
            print(f"✅ Authentication successful! Status: {health['status']}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

asyncio.run(test_auth())
```

Expected output:
```
✅ Authentication successful! Status: ok
```

## Error Handling

### Invalid API Key

```python
from shadai import Shadai, AuthenticationError

try:
    async with Shadai(name="test", api_key="invalid") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk)
except AuthenticationError:
    print("Invalid API key. Please check your credentials.")
```

### Missing API Key

```python
from shadai import Shadai

# This will raise an error if SHADAI_API_KEY is not set
try:
    shadai = Shadai(name="test")
except ValueError as e:
    print(f"Error: {e}")
```

## Multiple Accounts

Working with multiple Shadai accounts:

```python
from shadai import Shadai

# Account 1
async with Shadai(name="work", api_key="work_api_key") as shadai_work:
    async for chunk in shadai_work.query("Work query"):
        print(chunk, end="")

# Account 2
async with Shadai(name="personal", api_key="personal_api_key") as shadai_personal:
    async for chunk in shadai_personal.query("Personal query"):
        print(chunk, end="")
```

## Custom Base URL

For self-hosted or enterprise deployments:

```python
from shadai import Shadai

shadai = Shadai(
    name="my-session",
    api_key="your_api_key",
    base_url="https://custom.shadai.com"
)
```

## Next Steps

✅ Authentication configured! Let's run your first query.

→ [Quick Start Guide](quickstart.md)
