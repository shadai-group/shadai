# ShadAI Python Client - Update Summary

**Date**: October 17, 2025
**Version**: Updated to match backend v1.0 error response format

## Overview

The ShadAI Python client has been updated to align with the backend's new standardized error response format and validation system. These changes provide better error handling, clearer error messages, and improved developer experience.

## Key Changes

### 1. Complete Exception Hierarchy ✅

**File**: `shadai/exceptions.py`

The client now includes all exception types matching the backend structure:

```python
ShadaiError (base)
├── ConnectionError
├── AuthenticationError
│   ├── InvalidAPIKeyError
│   └── MissingAccountSetupError
├── ResourceError
│   ├── ResourceNotFoundError (Session, File, Account)
│   └── ResourceAlreadyExistsError (SessionAlreadyExists)
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

**New Exception Attributes**:
- `error_code`: Machine-readable code (e.g., "SESSION_NOT_FOUND")
- `error_type`: Category (e.g., "resource_error", "validation_error")
- `context`: Dict with additional debug information
- `is_retriable`: Boolean indicating if operation can be retried
- `suggestion`: Optional user-friendly suggestion

### 2. Smart Error Parsing ✅

**File**: `shadai/client.py`

The client now automatically parses the backend's standardized error response format and raises appropriate typed exceptions:

```python
# Old behavior (generic ServerError)
except ServerError as e:
    print(f"Error: {e}")

# New behavior (specific exception types)
except ConfigurationError as e:
    print(f"Missing: {e.context['config_key']}")
    print(f"Suggestion: {e.suggestion}")

except KnowledgePointsLimitExceededError as e:
    print(f"Used: {e.context['current_value']}/{e.context['max_allowed']}")
    print(f"Needed: {e.context['points_needed']}")
```

**Error Response Format** (from backend):
```json
{
  "version": "1.0",
  "success": false,
  "error": {
    "code": "CONFIGURATION_ERROR",
    "message": "No LLM model configured. Please configure...",
    "type": "system_error",
    "context": {
      "config_key": "llm_model",
      "reason": "..."
    },
    "is_retriable": false,
    "suggestion": "Configure in Settings"
  }
}
```

### 3. Exception Factory Function ✅

**File**: `shadai/exceptions.py`

Added `create_exception_from_error_response()` helper:

```python
def create_exception_from_error_response(error_data: Dict[str, Any]) -> ShadaiError:
    """
    Convert backend error response to appropriate Python exception.

    Automatically:
    - Maps error codes to exception classes
    - Extracts context parameters
    - Handles special cases (knowledge points, file size limits)
    - Falls back to generic ShadaiError
    """
```

## New Exception Types Explained

### ConfigurationError

**When**: Session or account lacks required LLM/embedding models
**Context Fields**:
- `config_key`: "llm_model" or "embedding_model"
- `reason`: Detailed explanation

**Example**:
```python
from shadai import ConfigurationError

try:
    async with Shadai(name="my-session") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")
except ConfigurationError as e:
    print(f"Missing: {e.context['config_key']}")
    # Output: "Missing: llm_model"
```

### KnowledgePointsLimitExceededError

**When**: Monthly knowledge points quota exhausted
**Context Fields**:
- `plan_name`: e.g., "Free", "Pro"
- `current_value`: Points used this month
- `max_allowed`: Monthly quota
- `points_needed`: Points required for operation

**Example**:
```python
from shadai import KnowledgePointsLimitExceededError

try:
    await shadai.ingest("/large-file.pdf")
except KnowledgePointsLimitExceededError as e:
    print(f"Plan: {e.context['plan_name']}")
    print(f"Used: {e.context['current_value']}/{e.context['max_allowed']}")
    print(f"Need: {e.context['points_needed']} more points")
```

### SessionAlreadyExistsError

**When**: Attempting to create session with duplicate name
**Context Fields**:
- `session_name`: Conflicting name
- `account_uuid`: Account ID

**Example**:
```python
from shadai import SessionAlreadyExistsError

try:
    result = await client.call_tool(
        tool_name="session_create",
        arguments={"name": "existing-session"}
    )
except SessionAlreadyExistsError as e:
    print(f"Suggestion: {e.suggestion}")
    # Output: "Use session_get_or_create to retrieve existing..."
```

## Migration Guide

### Before (Old Client)

```python
from shadai import Shadai, ServerError

try:
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")
except ServerError as e:
    # Generic error handling
    print(f"Error: {e}")
```

### After (New Client)

```python
from shadai import (
    Shadai,
    ConfigurationError,
    KnowledgePointsLimitExceededError,
    SessionNotFoundError,
    ShadaiError,
)

try:
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")

except ConfigurationError as e:
    # Specific handling for missing models
    print(f"❌ Setup required: {e.message}")
    print(f"Missing: {e.context.get('config_key')}")
    print("→ Configure in Settings")

except KnowledgePointsLimitExceededError as e:
    # Specific handling for quota
    print(f"❌ Quota exceeded: {e.message}")
    print(f"Used: {e.context['current_value']}/{e.context['max_allowed']}")
    print("→ Upgrade or wait until next month")

except SessionNotFoundError as e:
    # Session was deleted
    print(f"❌ Session not found: {e.context['session_uuid']}")

except ShadaiError as e:
    # Generic Shadai error
    print(f"❌ Error: {e.message}")
    print(f"Code: {e.error_code}")

    if e.is_retriable:
        print("💡 You can retry this operation")

    if e.suggestion:
        print(f"💡 {e.suggestion}")
```

## Retry Logic

The new `is_retriable` flag enables smart retry logic:

```python
import asyncio
from shadai import ShadaiError

async def query_with_retry(shadai, query: str, max_retries: int = 3):
    """Retry only for retriable errors."""
    for attempt in range(max_retries):
        try:
            async for chunk in shadai.query(query):
                print(chunk, end="")
            return  # Success

        except ShadaiError as e:
            # Check if error is retriable
            if e.is_retriable and attempt < max_retries - 1:
                wait = 2 ** attempt  # Exponential backoff
                print(f"⏳ Retrying in {wait}s... (attempt {attempt + 1})")
                await asyncio.sleep(wait)
            else:
                # Don't retry non-retriable errors (auth, validation, etc.)
                print(f"❌ Error (not retriable): {e.message}")
                raise
```

## Testing

### Unit Tests

```python
import pytest
from shadai import ConfigurationError, SessionNotFoundError

@pytest.mark.asyncio
async def test_configuration_error():
    """Test missing model configuration."""
    with pytest.raises(ConfigurationError) as exc_info:
        async with Shadai(name="unconfigured") as shadai:
            async for chunk in shadai.query("test"):
                pass

    error = exc_info.value
    assert error.error_code == "CONFIGURATION_ERROR"
    assert "config_key" in error.context
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

## Backend Compatibility

The client is now compatible with the backend's error handling system:

**Backend Error Format** → **Client Exception**

| Backend Error Code | Client Exception | Retriable |
|--------------------|------------------|-----------|
| `CONFIGURATION_ERROR` | `ConfigurationError` | No |
| `SESSION_NOT_FOUND` | `SessionNotFoundError` | No |
| `SESSION_ALREADY_EXISTS` | `SessionAlreadyExistsError` | No |
| `PLAN_LIMIT_EXCEEDED` (knowledge points) | `KnowledgePointsLimitExceededError` | No |
| `PLAN_LIMIT_EXCEEDED` (file size) | `FileSizeLimitExceededError` | No |
| `INVALID_FILE_TYPE` | `InvalidFileTypeError` | No |
| `INVALID_PARAMETER` | `InvalidParameterError` | No |
| `LLM_PROVIDER_ERROR` | `LLMProviderError` | Yes |
| `CONNECTION_ERROR` | `ConnectionError` | Yes |
| `DATABASE_ERROR` | `DatabaseError` | Yes |

## Documentation Updates

### Updated Files

1. **`docs/guides/error-handling.md`** ✅
   - Complete exception hierarchy
   - All error types with examples
   - Retry strategies
   - User-friendly error messages
   - Testing patterns

2. **`shadai/exceptions.py`** ✅
   - All exception classes
   - Error factory function
   - Type hints and docstrings

3. **`shadai/client.py`** ✅
   - Error response parsing
   - Automatic exception creation

## Breaking Changes

### ⚠️ None

All changes are **backward compatible**. Old code using generic `ServerError` will continue to work, but you can now catch more specific exceptions for better handling.

## Recommendations

### For New Projects

Use specific exception types from the start:

```python
from shadai import (
    ConfigurationError,
    KnowledgePointsLimitExceededError,
    SessionNotFoundError,
    AuthenticationError,
)

# Catch specific errors for targeted UX
```

### For Existing Projects

Gradually migrate to specific exception handling:

```python
# Phase 1: Add specific handlers for common errors
except ConfigurationError as e:
    show_setup_modal()
except ShadaiError as e:
    # Keep generic handler
    pass

# Phase 2: Add more specific handlers
except KnowledgePointsLimitExceededError as e:
    show_upgrade_prompt()
except SessionNotFoundError as e:
    create_new_session()

# Phase 3: Comprehensive error handling
# (See error-handling.md for full examples)
```

## Benefits

### For Developers

1. **Type Safety**: Catch specific exception types
2. **Better Debugging**: Rich context information
3. **Smart Retries**: Use `is_retriable` flag
4. **Clearer Code**: Intent is obvious from exception type

### For Users

1. **Better Error Messages**: User-friendly, actionable
2. **Contextual Help**: Suggestions for resolution
3. **Proactive Guidance**: Know what to do next
4. **Less Frustration**: Clear path to fix issues

## Example: Production Error Handler

```python
def handle_shadai_error(error: ShadaiError) -> dict:
    """Convert Shadai error to UI-friendly format."""

    if isinstance(error, ConfigurationError):
        return {
            "title": "⚙️ Setup Required",
            "message": error.message,
            "action": "Configure Settings",
            "severity": "warning"
        }

    elif isinstance(error, KnowledgePointsLimitExceededError):
        return {
            "title": "📊 Quota Reached",
            "message": error.message,
            "action": "Upgrade Plan",
            "severity": "error"
        }

    elif isinstance(error, LLMProviderError):
        return {
            "title": "⚠️ Service Unavailable",
            "message": "AI service temporarily unavailable",
            "action": "Retry" if error.is_retriable else "Contact Support",
            "severity": "warning"
        }

    else:
        return {
            "title": "❌ Error",
            "message": error.message,
            "action": "Retry" if error.is_retriable else "Contact Support",
            "severity": "error"
        }
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/shadai/shadai-python/issues
- Documentation: https://docs.shadai.com
- Email: support@shadai.com

---

## Checklist for Developers

- [ ] Update imports to include specific exceptions
- [ ] Add error handling for `ConfigurationError`
- [ ] Add error handling for `KnowledgePointsLimitExceededError`
- [ ] Implement retry logic using `is_retriable` flag
- [ ] Use `error.context` for detailed error information
- [ ] Display `error.suggestion` when available
- [ ] Update tests to check for specific exception types
- [ ] Review user-facing error messages
- [ ] Add logging with error context
- [ ] Test error scenarios end-to-end

---

**Last Updated**: October 17, 2025
**Compatible With**: Backend v1.0+ (standardized error format)
