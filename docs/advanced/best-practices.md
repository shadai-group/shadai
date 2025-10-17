# Best Practices

Production-ready patterns and recommendations.

## Code Organization

### Structure Your Application

```
my_app/
├── config/
│   └── shadai_config.py
├── tools/
│   ├── __init__.py
│   ├── database_tools.py
│   └── api_tools.py
├── services/
│   └── qa_service.py
└── main.py
```

### Configuration Management

```python
# config/shadai_config.py
import os
from dataclasses import dataclass

@dataclass
class ShadaiConfig:
    api_key: str = os.getenv("SHADAI_API_KEY")
    base_url: str = os.getenv("SHADAI_BASE_URL", "http://localhost")
    timeout: int = int(os.getenv("SHADAI_TIMEOUT", "30"))
    docs_folder: str = "./documents"

config = ShadaiConfig()
```

## Error Handling

### Comprehensive Error Handling

```python
from shadai import (
    Shadai,
    AuthenticationError,
    ConnectionError,
    ServerError
)
import logging

logger = logging.getLogger(__name__)

async def robust_query(query: str):
    try:
        async with Shadai(name="app") as shadai:
            response = ""
            async for chunk in shadai.query(query):
                response += chunk
            return response

    except AuthenticationError:
        logger.error("Authentication failed")
        raise
    except ConnectionError:
        logger.error("Connection failed")
        # Retry logic here
    except ServerError as e:
        logger.error(f"Server error: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise
```

## Security

### API Key Management

```python
# ✅ Use environment variables
import os
api_key = os.getenv("SHADAI_API_KEY")

# ✅ Use secret management services
from your_secrets_manager import get_secret
api_key = get_secret("shadai_api_key")

# ❌ Never hardcode
api_key = "sk-123456"  # Don't do this!
```

### Input Validation

```python
def validate_query(query: str) -> bool:
    if not query or len(query) < 3:
        return False
    if len(query) > 1000:
        return False
    return True

async def safe_query(query: str):
    if not validate_query(query):
        raise ValueError("Invalid query")

    async with Shadai(name="app") as shadai:
        async for chunk in shadai.query(query):
            print(chunk, end="")
```

## Testing

### Unit Tests

```python
import pytest
from shadai import Shadai

@pytest.mark.asyncio
async def test_query():
    async with Shadai(name="test", temporal=True) as shadai:
        # Test query functionality
        response = ""
        async for chunk in shadai.query("test"):
            response += chunk
        assert len(response) > 0

@pytest.mark.asyncio
async def test_ingestion():
    async with Shadai(name="test", temporal=True) as shadai:
        results = await shadai.ingest(folder_path="./test-docs")
        assert results["successful_count"] > 0
```

## Monitoring

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def monitored_query(query: str):
    logger.info(f"Processing query: {query}")
    try:
        async with Shadai(name="app") as shadai:
            response = ""
            async for chunk in shadai.query(query):
                response += chunk
            logger.info("Query completed successfully")
            return response
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
```

### Metrics

```python
import time
from dataclasses import dataclass

@dataclass
class QueryMetrics:
    query: str
    duration: float
    response_length: int
    success: bool

async def query_with_metrics(query: str) -> QueryMetrics:
    start = time.time()
    try:
        async with Shadai(name="app") as shadai:
            response = ""
            async for chunk in shadai.query(query):
                response += chunk

            return QueryMetrics(
                query=query,
                duration=time.time() - start,
                response_length=len(response),
                success=True
            )
    except Exception:
        return QueryMetrics(
            query=query,
            duration=time.time() - start,
            response_length=0,
            success=False
        )
```

## See Also

- [Performance Optimization](performance-optimization.md)
- [Error Handling Guide](../guides/error-handling.md)
- [Custom Tools](custom-tools.md)
