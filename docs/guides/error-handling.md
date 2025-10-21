# Error Handling

Build robust applications with Shadai's comprehensive error handling system that provides structured, actionable error information.

## Automatic Error Handling

**New in v0.1.31**: Shadai now automatically displays clean, user-friendly error messages without requiring try-except blocks!

### Clean Error Messages by Default

When an error occurs, Shadai automatically displays a formatted message instead of a verbose Python traceback:

```python
from shadai import Shadai

async def main():
    # No try-except needed!
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.query("What is AI?"):
            print(chunk, end="")

# If an error occurs, you'll see:
# ❌ Error [CONFIGURATION_ERROR]:
#    Invalid configuration for 'provider_credentials': You need to configure
#    at least one Provider credential before creating a session.
#
# 💡 Suggestion:
#    Add your Provider credential in → Secrets.
```

**No more verbose tracebacks!** The error handler automatically:
- ✅ Shows the error code in brackets
- ✅ Displays a clear, concise message
- ✅ Includes actionable suggestions when available
- ✅ Hides internal stack traces from users
- ✅ Exits cleanly with appropriate error code

### When to Use Manual Error Handling

You can still use try-except blocks for programmatic error handling:

```python
from shadai import Shadai, ConfigurationError, KnowledgePointsLimitExceededError

async def main():
    try:
        async with Shadai(name="test") as shadai:
            async for chunk in shadai.query("Question"):
                print(chunk, end="")

    except ConfigurationError as e:
        # Custom handling for configuration errors
        show_setup_modal(e.context["config_key"])

    except KnowledgePointsLimitExceededError as e:
        # Custom handling for quota errors
        show_upgrade_prompt(e.context["plan_name"])
```

**Use manual error handling when:**
- Building UIs that need to show custom error dialogs
- Implementing retry logic or fallback mechanisms
- Logging errors to external services
- Need programmatic access to error details

**Don't use manual error handling when:**
- Building simple CLI scripts
- Prototyping or testing
- Error messages are displayed directly to users
- Default formatting is sufficient

## Overview

Shadai uses a hierarchical exception system with:
- **Structured error messages** - Human-readable and user-friendly
- **Machine-readable error codes** - For programmatic handling
- **Contextual information** - Debug details and affected resources
- **Retry flags** - Indicates if operation can be retried
- **Suggestions** - Actionable guidance for resolution
- **Automatic formatting** - Clean output without verbose tracebacks

## Exception Hierarchy

```
ShadaiError (base)
├── ConnectionError
├── AuthenticationError
│   ├── InvalidAPIKeyError
│   └── MissingAccountSetupError
├── ResourceError
│   ├── ResourceNotFoundError
│   │   ├── SessionNotFoundError
│   │   ├── FileNotFoundError
│   │   └── AccountNotFoundError
│   └── ResourceAlreadyExistsError
│       └── SessionAlreadyExistsError
├── ValidationError
│   ├── InvalidFileTypeError
│   ├── InvalidParameterError
│   ├── MissingParameterError
│   ├── InvalidBase64Error
│   └── BatchSizeLimitExceededError
├── AuthorizationError
│   └── PlanLimitExceededError
│       ├── KnowledgePointsLimitExceededError
│       └── FileSizeLimitExceededError
├── ExternalServiceError
│   ├── LLMProviderError
│   ├── VectorStoreError
│   └── S3StorageError
├── ProcessingError
│   ├── FileParsingError
│   └── ChunkIngestionError
└── SystemError
    ├── ConfigurationError
    ├── DatabaseError
    ├── TimeoutError
    └── ServerError
```

## Import Exceptions

```python
from shadai import (
    Shadai,
    # Base
    ShadaiError,
    # Authentication
    AuthenticationError,
    InvalidAPIKeyError,
    MissingAccountSetupError,
    # Resources
    SessionNotFoundError,
    FileNotFoundError,
    SessionAlreadyExistsError,
    # Validation
    ValidationError,
    InvalidFileTypeError,
    InvalidParameterError,
    # Authorization
    PlanLimitExceededError,
    KnowledgePointsLimitExceededError,
    FileSizeLimitExceededError,
    # System
    ConfigurationError,
    ServerError,
    ConnectionError,
)
```

## Common Errors

### Authentication Errors

#### Invalid API Key

**Cause**: API key is missing or incorrect

```python
from shadai import Shadai, InvalidAPIKeyError

try:
    async with Shadai(api_key="invalid-key") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")
except InvalidAPIKeyError as e:
    print(f"❌ {e.message}")
    print("Please check your API key at https://shadai.com/settings")
```

**Solutions**:
- Verify API key in `.env` file
- Regenerate API key if compromised
- Ensure `SHADAI_API_KEY` environment variable is set

#### Missing Account Setup

**Cause**: API key valid but account not configured

```python
from shadai import MissingAccountSetupError

try:
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")
except MissingAccountSetupError as e:
    print(f"❌ {e.message}")
    print("Please complete account setup at https://shadai.com/setup")
```

### Configuration Errors

#### Missing LLM or Embedding Model

**Cause**: Session or account lacks required AI models

```python
from shadai import ConfigurationError

try:
    async with Shadai(name="my-session") as shadai:
        # Upload file or query - requires models
        async for chunk in shadai.query("What is AI?"):
            print(chunk, end="")
except ConfigurationError as e:
    print(f"❌ Configuration Error: {e.message}")
    print(f"Missing: {e.context.get('config_key')}")
    print(f"Reason: {e.context.get('reason')}")
    # Example output:
    # "No LLM model configured. Please configure an LLM model
    #  in → Settings to continue."
```

**Solutions**:
- Configure LLM model in session or account settings
- Configure embedding model for document processing
- Check that models are properly saved

**Context Fields**:
- `config_key`: "llm_model" or "embedding_model"
- `reason`: Detailed explanation

### Resource Errors

#### Session Not Found

**Cause**: Session was deleted or UUID is incorrect

```python
from shadai import SessionNotFoundError

try:
    result = await client.call_tool(
        tool_name="shadai_query",
        arguments={"session_uuid": "invalid-uuid", "query": "test"}
    )
except SessionNotFoundError as e:
    print(f"❌ {e.message}")
    print(f"Session: {e.context['session_uuid']}")
    # Create new session
    async with Shadai(name="new-session") as shadai:
        pass
```

**Solutions**:
- Verify session UUID is correct
- Create new session if old one was deleted
- List available sessions

#### Session Already Exists

**Cause**: Attempting to create duplicate session name

```python
from shadai import SessionAlreadyExistsError

try:
    # Try to create session with existing name
    result = await client.call_tool(
        tool_name="session_create",
        arguments={"name": "existing-session"}
    )
except SessionAlreadyExistsError as e:
    print(f"❌ {e.message}")
    print(f"Suggestion: {e.suggestion}")
    # Outputs: "Use session_get_or_create to retrieve existing
    #           session or create new one"

    # Use get_or_create instead
    result = await client.call_tool(
        tool_name="session_get_or_create",
        arguments={"name": "existing-session"}
    )
```

**Solutions**:
- Use `session_get_or_create` instead of `session_create`
- Choose a different session name
- Delete existing session if intended

### Validation Errors

#### Invalid File Type

**Cause**: Uploading unsupported file format

```python
from shadai import InvalidFileTypeError

try:
    await shadai.ingest("/path/to/document.exe")
except InvalidFileTypeError as e:
    print(f"❌ {e.message}")
    print(f"Extension: {e.context['file_extension']}")
    print(f"Allowed: {', '.join(e.context['allowed_extensions'])}")
```

**Supported Types**: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.webp`

#### Invalid Parameter

**Cause**: Parameter value out of acceptable range

```python
from shadai import InvalidParameterError

try:
    # page_size must be 1-10
    history = await client.get_session_history(
        session_uuid="abc",
        page_size=100  # Too large
    )
except InvalidParameterError as e:
    print(f"❌ {e.message}")
    print(f"Parameter: {e.context['parameter_name']}")
    print(f"Value: {e.context['parameter_value']}")
    print(f"Reason: {e.context['reason']}")
```

### Authorization & Limit Errors

#### Knowledge Points Limit Exceeded

**Cause**: Monthly knowledge points quota exhausted

```python
from shadai import KnowledgePointsLimitExceededError

try:
    # Upload file that exceeds remaining quota
    await shadai.ingest("/path/to/large-document.pdf")
except KnowledgePointsLimitExceededError as e:
    print(f"❌ {e.message}")
    print(f"Plan: {e.context['plan_name']}")
    print(f"Used: {e.context['current_value']}/{e.context['max_allowed']}")
    print(f"This operation needs: {e.context['points_needed']} points")
    print("\n💡 Options:")
    print("1. Delete old files to free up points")
    print("2. Wait until next month (resets on 1st)")
    print("3. Upgrade plan at https://shadai.com/pricing")
```

**Solutions**:
- Delete unused files to free knowledge points
- Upgrade to higher plan tier
- Wait for monthly reset (1st of month)

**Context Fields**:
- `plan_name`: Current plan (e.g., "Free", "Pro")
- `current_value`: Points used this month
- `max_allowed`: Monthly quota
- `points_needed`: Points required for operation

#### File Size Limit Exceeded

**Cause**: File exceeds plan's maximum file size

```python
from shadai import FileSizeLimitExceededError

try:
    await shadai.ingest("/path/to/huge-file.pdf")  # 50MB file
except FileSizeLimitExceededError as e:
    print(f"❌ {e.message}")
    print(f"File: {e.context['filename']}")
    size_mb = e.context['current_value'] / (1024 * 1024)
    max_mb = e.context['max_allowed'] / (1024 * 1024)
    print(f"Size: {size_mb:.2f} MB (max: {max_mb:.2f} MB)")
```

**Solutions**:
- Split large file into smaller parts
- Compress or optimize file
- Upgrade to plan with larger file limits

### External Service Errors

#### LLM Provider Error

**Cause**: AI provider API failure or rate limit

```python
from shadai import LLMProviderError

try:
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")
except LLMProviderError as e:
    print(f"❌ {e.message}")
    print(f"Provider: {e.context['provider_name']}")
    if 'status_code' in e.context:
        print(f"Status: {e.context['status_code']}")

    if e.is_retriable:
        # Retry after delay
        await asyncio.sleep(5)
        # retry...
```

**Solutions**:
- Retry after delay (exponential backoff)
- Check if provider is experiencing outages
- Switch to different model provider

### Connection Errors

**Cause**: Network issues or server unreachable

```python
from shadai import ConnectionError

try:
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")
except ConnectionError as e:
    print(f"❌ Connection failed: {e.message}")
    print("Please check:")
    print("- Internet connection")
    print("- Server URL is correct")
    print("- Firewall/proxy settings")
```

**Solutions**:
- Check internet connectivity
- Verify `base_url` is correct
- Increase timeout: `Shadai(..., timeout=60)`
- Check firewall/proxy settings

## Comprehensive Error Handling

### Basic Pattern

```python
from shadai import Shadai, ShadaiError

try:
    async with Shadai(name="app") as shadai:
        async for chunk in shadai.query("What is machine learning?"):
            print(chunk, end="", flush=True)

except ShadaiError as e:
    # Catches all Shadai-specific errors
    print(f"\n❌ Error: {e.message}")
    print(f"Code: {e.error_code}")
    print(f"Type: {e.error_type}")

    if e.is_retriable:
        print("💡 You can retry this operation")

    if e.suggestion:
        print(f"💡 Suggestion: {e.suggestion}")

except Exception as e:
    # Catches any other errors
    print(f"\n❌ Unexpected error: {e}")
```

### Detailed Pattern with Specific Handlers

```python
from shadai import (
    Shadai,
    ConfigurationError,
    SessionNotFoundError,
    KnowledgePointsLimitExceededError,
    AuthenticationError,
    ConnectionError,
)

try:
    async with Shadai(name="app") as shadai:
        async for chunk in shadai.query("Question"):
            print(chunk, end="", flush=True)

except ConfigurationError as e:
    # Missing LLM or embedding model
    print(f"\n❌ Setup required: {e.message}")
    print(f"Missing: {e.context.get('config_key')}")
    print("→ Please configure models in Settings")

except SessionNotFoundError as e:
    # Session was deleted
    print(f"\n❌ Session not found: {e.context['session_uuid']}")
    print("Creating new session...")
    async with Shadai(name="new-session") as new_shadai:
        # Use new session
        pass

except KnowledgePointsLimitExceededError as e:
    # Quota exceeded
    print(f"\n❌ Knowledge points limit reached")
    print(f"Plan: {e.context['plan_name']}")
    print(f"Used: {e.context['current_value']}/{e.context['max_allowed']}")
    print("→ Upgrade at https://shadai.com/pricing")

except AuthenticationError:
    # Invalid API key
    print("\n❌ Authentication failed. Check your API key.")

except ConnectionError:
    # Network issues
    print("\n❌ Connection failed. Check your internet.")

except Exception as e:
    # Unexpected errors
    print(f"\n❌ Unexpected error: {e}")
```

## Retry Logic

### Smart Retry with Retriable Check

```python
import asyncio

async def query_with_retry(shadai, query: str, max_retries: int = 3):
    """Retry only for retriable errors."""
    for attempt in range(max_retries):
        try:
            result = []
            async for chunk in shadai.query(query):
                result.append(chunk)
            return "".join(result)  # Success

        except ShadaiError as e:
            # Check if error is retriable
            if e.is_retriable and attempt < max_retries - 1:
                wait = 2 ** attempt  # Exponential backoff
                print(f"\n⏳ Retrying in {wait}s... ({attempt + 1}/{max_retries})")
                print(f"Reason: {e.message}")
                await asyncio.sleep(wait)
            else:
                # Don't retry non-retriable errors
                print(f"\n❌ Error (not retriable): {e.message}")
                raise

# Usage
async with Shadai(name="app") as shadai:
    result = await query_with_retry(shadai, "What is AI?")
    print(result)
```

### Exponential Backoff with Jitter

```python
import random

async def exponential_backoff_retry(
    func,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
):
    """Retry with exponential backoff and optional jitter."""
    for attempt in range(max_retries):
        try:
            return await func()

        except ShadaiError as e:
            if e.is_retriable and attempt < max_retries - 1:
                # Calculate delay with exponential backoff
                delay = min(base_delay * (2 ** attempt), max_delay)

                # Add jitter to prevent thundering herd
                if jitter:
                    delay = delay * (0.5 + random.random() * 0.5)

                print(f"⏳ Retry {attempt + 1}/{max_retries} in {delay:.1f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"❌ Failed after {attempt + 1} attempts: {e.message}")
                raise

# Usage
async def query():
    async with Shadai(name="retry") as shadai:
        result = []
        async for chunk in shadai.query("Question"):
            result.append(chunk)
        return "".join(result)

result = await exponential_backoff_retry(query)
```

## Graceful Degradation

### Feature Fallback Strategy

```python
async def query_with_fallback(query: str):
    """Try advanced features first, fall back to basics."""

    # Try 1: Full engine with all features
    try:
        async with Shadai(name="primary") as shadai:
            print("🚀 Using full engine...")
            async for chunk in shadai.engine(
                prompt=query,
                use_knowledge_base=True,
                use_summary=True,
                use_web_search=True
            ):
                print(chunk, end="")
            return

    except (LLMProviderError, ConnectionError):
        print("\n⚠️ Engine unavailable, trying basic query...")

    # Try 2: Simple knowledge base query
    try:
        async with Shadai(name="fallback") as shadai:
            print("📚 Using knowledge base only...")
            async for chunk in shadai.query(query):
                print(chunk, end="")
            return

    except Exception:
        # Try 3: Offline mode or cached response
        print("\n⚠️ All services unavailable")
        print("💡 Suggestion: Try again later or contact support")

# Usage
await query_with_fallback("Explain quantum computing")
```

## User-Friendly Error Messages

### Production-Ready Error Handler

```python
def get_user_friendly_message(error: Exception) -> dict:
    """Convert exceptions to user-friendly UI messages."""

    if isinstance(error, ConfigurationError):
        return {
            "title": "⚙️ Setup Required",
            "message": error.message,
            "action": "Configure Settings",
            "link": "/settings/models"
        }

    elif isinstance(error, KnowledgePointsLimitExceededError):
        used = error.context["current_value"]
        max_points = error.context["max_allowed"]
        return {
            "title": "📊 Quota Reached",
            "message": f"You've used {used}/{max_points} knowledge points",
            "action": "Upgrade Plan",
            "link": "/pricing"
        }

    elif isinstance(error, SessionNotFoundError):
        return {
            "title": "🔍 Session Not Found",
            "message": "This session may have been deleted",
            "action": "Create New Session",
            "link": "/sessions/new"
        }

    elif isinstance(error, AuthenticationError):
        return {
            "title": "🔐 Authentication Failed",
            "message": "Please check your API key",
            "action": "Update API Key",
            "link": "/settings/api-keys"
        }

    elif isinstance(error, ConnectionError):
        return {
            "title": "🌐 Connection Error",
            "message": "Unable to connect to Shadai",
            "action": "Retry",
            "link": None
        }

    else:
        return {
            "title": "❌ Unexpected Error",
            "message": "Something went wrong. Our team has been notified.",
            "action": "Contact Support",
            "link": "/support"
        }

# Usage in UI
try:
    async with Shadai(name="app") as shadai:
        async for chunk in shadai.query("Question"):
            display_chunk(chunk)

except Exception as e:
    error_info = get_user_friendly_message(e)
    show_error_dialog(
        title=error_info["title"],
        message=error_info["message"],
        action_button=error_info["action"],
        action_link=error_info["link"]
    )
```

## Logging Errors

### Structured Logging with Context

```python
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_shadai_error(error: ShadaiError, operation: str, **kwargs):
    """Log Shadai errors with full context."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "error_code": error.error_code,
        "error_type": error.error_type,
        "error_message": error.message,
        "is_retriable": error.is_retriable,
        "context": error.context,
        "suggestion": error.suggestion,
        **kwargs  # Additional context
    }

    if error.is_retriable:
        logger.warning(f"Retriable error: {json.dumps(log_entry)}")
    else:
        logger.error(f"Non-retriable error: {json.dumps(log_entry)}")

# Usage
try:
    async with Shadai(name="app") as shadai:
        async for chunk in shadai.query("Question"):
            print(chunk, end="")

except ShadaiError as e:
    log_shadai_error(
        error=e,
        operation="query",
        session_name="app",
        query="Question",
        user_id="user-123"
    )
```

## Best Practices

### ✅ Do This

```python
# 1. Catch specific exceptions for targeted handling
try:
    async with Shadai(name="app") as shadai:
        async for chunk in shadai.query("Question"):
            print(chunk, end="")
except ConfigurationError as e:
    # Show setup modal
    show_setup_modal(e.context['config_key'])
except KnowledgePointsLimitExceededError as e:
    # Show upgrade prompt
    show_upgrade_prompt(e.context['plan_name'])
except ShadaiError as e:
    # Generic handler
    show_error(e.message)

# 2. Check retry flag before retrying
except ShadaiError as e:
    if e.is_retriable:
        schedule_retry()
    else:
        show_error(e.message)

# 3. Use error context for better UX
except ConfigurationError as e:
    missing = e.context.get('config_key')
    show_message(f"Please configure {missing}")

# 4. Provide actionable suggestions
except ShadaiError as e:
    if e.suggestion:
        show_suggestion(e.suggestion)
```

### ❌ Don't Do This

```python
# Don't catch all and ignore
try:
    await shadai.query("test")
except:
    pass  # Silent failure - BAD

# Don't expose technical details to users
except ShadaiError as e:
    print(e.context)  # Shows internal details - BAD
    # Instead: print(e.message)

# Don't retry non-retriable errors
except ShadaiError as e:
    await retry()  # Might retry auth errors - BAD
    # Instead: Check e.is_retriable first

# Don't ignore error codes
except ShadaiError as e:
    show_generic_error()  # Loses specificity - BAD
    # Instead: Handle by error_code or type
```

## Testing Error Scenarios

### Unit Tests with pytest

```python
import pytest
from shadai import (
    Shadai,
    ConfigurationError,
    KnowledgePointsLimitExceededError,
    SessionNotFoundError,
)

@pytest.mark.asyncio
async def test_configuration_error():
    """Test missing model configuration."""
    with pytest.raises(ConfigurationError) as exc_info:
        async with Shadai(name="unconfigured-session") as shadai:
            async for chunk in shadai.query("test"):
                pass

    assert exc_info.value.error_code == "CONFIGURATION_ERROR"
    assert "llm_model" in exc_info.value.context.get("config_key", "")

@pytest.mark.asyncio
async def test_knowledge_points_limit():
    """Test knowledge points quota."""
    with pytest.raises(KnowledgePointsLimitExceededError) as exc_info:
        async with Shadai(name="test") as shadai:
            # Upload file that exceeds quota
            await shadai.ingest("/large-file.pdf")

    error = exc_info.value
    assert error.error_code == "PLAN_LIMIT_EXCEEDED"
    assert error.context["points_needed"] > 0
    assert not error.is_retriable

@pytest.mark.asyncio
async def test_session_not_found():
    """Test invalid session UUID."""
    from shadai import ShadaiClient

    client = ShadaiClient(api_key="test-key")
    with pytest.raises(SessionNotFoundError):
        await client.call_tool(
            tool_name="shadai_query",
            arguments={"session_uuid": "invalid-uuid", "query": "test"}
        )
```

## Error Monitoring

### Integration with Sentry

```python
import sentry_sdk
from shadai import ShadaiError

sentry_sdk.init(dsn="your-sentry-dsn")

try:
    async with Shadai(name="app") as shadai:
        async for chunk in shadai.query("Question"):
            print(chunk, end="")

except ShadaiError as e:
    # Add custom context to Sentry
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("error_code", e.error_code)
        scope.set_tag("error_type", e.error_type)
        scope.set_tag("is_retriable", e.is_retriable)
        scope.set_context("shadai_context", e.context)

        if e.suggestion:
            scope.set_extra("suggestion", e.suggestion)

        sentry_sdk.capture_exception(e)

    # Still show user-friendly message
    print(f"Error: {e.message}")
```

## Next Steps

- [Session Management](session-management.md) - Handle session lifecycle
- [File Ingestion](file-ingestion.md) - Manage file uploads and errors
- [Best Practices](../advanced/best-practices.md) - Production patterns
- [API Reference](../api-reference/exceptions.md) - Complete exception docs

---

**Pro Tip**: Use `error.context` to provide specific, actionable feedback. The backend provides rich context to help you build great UX.
