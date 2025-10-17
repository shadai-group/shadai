# Exceptions Reference

Complete reference for all Shadai exception types with attributes and usage examples.

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

## Base Exception

### ShadaiError

**Base exception for all Shadai errors.**

**Attributes:**
- `message` (str): Human-readable error message
- `error_code` (str): Machine-readable error code
- `error_type` (str): Error category
- `context` (dict): Additional debugging context
- `is_retriable` (bool): Whether operation can be retried
- `suggestion` (str | None): Optional user guidance

**Example:**
```python
from shadai import ShadaiError

try:
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")
except ShadaiError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.error_code}")
    print(f"Type: {e.error_type}")
    print(f"Context: {e.context}")

    if e.is_retriable:
        print("💡 You can retry this operation")

    if e.suggestion:
        print(f"💡 Suggestion: {e.suggestion}")
```

---

## Authentication Errors

### AuthenticationError

Raised when authentication fails.

**Error Code:** `AUTHENTICATION_ERROR`
**Retriable:** No

```python
from shadai import AuthenticationError

try:
    async with Shadai(api_key="invalid") as shadai:
        pass
except AuthenticationError as e:
    print("Authentication failed - check your API key")
```

### InvalidAPIKeyError

Raised when API key is invalid.

**Error Code:** `INVALID_API_KEY`
**Retriable:** No

```python
from shadai import InvalidAPIKeyError

try:
    async with Shadai(api_key="invalid-key") as shadai:
        pass
except InvalidAPIKeyError:
    print("Invalid API key - please regenerate")
```

### MissingAccountSetupError

Raised when account setup is missing or incomplete.

**Error Code:** `MISSING_ACCOUNT_SETUP`
**Retriable:** No

```python
from shadai import MissingAccountSetupError

try:
    async with Shadai(name="test") as shadai:
        pass
except MissingAccountSetupError:
    print("Complete account setup at https://shadai.com/setup")
```

---

## Resource Errors

### SessionNotFoundError

Raised when session doesn't exist.

**Error Code:** `SESSION_NOT_FOUND`
**Retriable:** No
**Context:** `session_uuid`, `account_uuid`

```python
from shadai import SessionNotFoundError

try:
    # Access deleted session
    pass
except SessionNotFoundError as e:
    print(f"Session {e.context['session_uuid']} not found")
    # Create new session
```

### FileNotFoundError

Raised when file doesn't exist.

**Error Code:** `FILE_NOT_FOUND`
**Retriable:** No
**Context:** `resource_id`

```python
from shadai import FileNotFoundError

try:
    # Access deleted file
    pass
except FileNotFoundError as e:
    print(f"File {e.context['resource_id']} not found")
```

### SessionAlreadyExistsError

Raised when session name already exists.

**Error Code:** `SESSION_ALREADY_EXISTS`
**Retriable:** No
**Context:** `session_name`, `account_uuid`
**Suggestion:** "Use session_get_or_create..."

```python
from shadai import SessionAlreadyExistsError

try:
    # Create duplicate session name
    pass
except SessionAlreadyExistsError as e:
    print(f"Session '{e.context['session_name']}' exists")
    print(f"Suggestion: {e.suggestion}")
```

---

## Validation Errors

### InvalidFileTypeError

Raised when file type is not supported.

**Error Code:** `INVALID_FILE_TYPE`
**Retriable:** No
**Context:** `file_extension`, `allowed_extensions`

```python
from shadai import InvalidFileTypeError

try:
    await shadai.ingest("/path/to/file.exe")
except InvalidFileTypeError as e:
    print(f"File type '{e.context['file_extension']}' not allowed")
    print(f"Allowed: {', '.join(e.context['allowed_extensions'])}")
```

### InvalidParameterError

Raised when parameter value is invalid.

**Error Code:** `INVALID_PARAMETER`
**Retriable:** No
**Context:** `parameter_name`, `parameter_value`, `reason`

```python
from shadai import InvalidParameterError

try:
    # Invalid page_size value
    pass
except InvalidParameterError as e:
    print(f"Invalid {e.context['parameter_name']}: {e.context['reason']}")
```

### MissingParameterError

Raised when required parameter is missing.

**Error Code:** `MISSING_PARAMETER`
**Retriable:** No
**Context:** `parameter_name`

```python
from shadai import MissingParameterError

try:
    # Missing required parameter
    pass
except MissingParameterError as e:
    print(f"Missing required parameter: {e.context['parameter_name']}")
```

---

## Authorization Errors

### KnowledgePointsLimitExceededError

Raised when monthly knowledge points quota is exhausted.

**Error Code:** `PLAN_LIMIT_EXCEEDED`
**Retriable:** No
**Context:** `plan_name`, `current_value`, `max_allowed`, `points_needed`

```python
from shadai import KnowledgePointsLimitExceededError

try:
    await shadai.ingest("/large-file.pdf")
except KnowledgePointsLimitExceededError as e:
    print(f"Plan: {e.context['plan_name']}")
    print(f"Used: {e.context['current_value']}/{e.context['max_allowed']}")
    print(f"Need: {e.context['points_needed']} more points")
    print("\n💡 Options:")
    print("1. Delete old files")
    print("2. Wait until next month")
    print("3. Upgrade plan")
```

### FileSizeLimitExceededError

Raised when file exceeds plan's size limit.

**Error Code:** `PLAN_LIMIT_EXCEEDED`
**Retriable:** No
**Context:** `filename`, `current_value`, `max_allowed`, `plan_name`

```python
from shadai import FileSizeLimitExceededError

try:
    await shadai.ingest("/huge-file.pdf")
except FileSizeLimitExceededError as e:
    size_mb = e.context['current_value'] / (1024 * 1024)
    max_mb = e.context['max_allowed'] / (1024 * 1024)
    print(f"File '{e.context['filename']}' is {size_mb:.2f}MB")
    print(f"Max allowed: {max_mb:.2f}MB for {e.context['plan_name']} plan")
```

---

## External Service Errors

### LLMProviderError

Raised when LLM provider API fails.

**Error Code:** `LLM_PROVIDER_ERROR`
**Retriable:** Yes
**Context:** `provider_name`, `status_code` (optional)

```python
from shadai import LLMProviderError

try:
    async for chunk in shadai.query("test"):
        print(chunk, end="")
except LLMProviderError as e:
    print(f"Provider '{e.context['provider_name']}' error")

    if e.is_retriable:
        # Retry with exponential backoff
        await asyncio.sleep(5)
        # retry...
```

---

## System Errors

### ConfigurationError

Raised when required configuration is missing.

**Error Code:** `CONFIGURATION_ERROR`
**Retriable:** No
**Context:** `config_key`, `reason`

```python
from shadai import ConfigurationError

try:
    async for chunk in shadai.query("test"):
        print(chunk, end="")
except ConfigurationError as e:
    print(f"Missing: {e.context['config_key']}")
    print(f"Reason: {e.context['reason']}")
    print("→ Configure in Settings")
```

### ConnectionError

Raised when cannot connect to server.

**Error Code:** `CONNECTION_ERROR`
**Retriable:** Yes

```python
from shadai import ConnectionError

try:
    async with Shadai(name="test") as shadai:
        pass
except ConnectionError as e:
    print("Cannot connect to server")
    print("Check internet connection and server URL")
```

### ServerError

Raised when server encounters an error.

**Error Code:** `SERVER_ERROR`
**Retriable:** No
**Context:** `status_code` (optional)

```python
from shadai import ServerError

try:
    async with Shadai(name="test") as shadai:
        pass
except ServerError as e:
    print(f"Server error: {e.message}")
    if 'status_code' in e.context:
        print(f"Status: {e.context['status_code']}")
```

---

## Comprehensive Error Handling

### Pattern 1: Specific Error Types

```python
from shadai import (
    Shadai,
    ConfigurationError,
    KnowledgePointsLimitExceededError,
    SessionNotFoundError,
    AuthenticationError,
    ConnectionError,
    LLMProviderError,
)

try:
    async with Shadai(name="app") as shadai:
        async for chunk in shadai.query("Question"):
            print(chunk, end="")

except ConfigurationError as e:
    # Missing LLM or embedding model
    show_setup_modal(e.context['config_key'])

except KnowledgePointsLimitExceededError as e:
    # Quota exceeded
    show_upgrade_prompt(e.context['plan_name'])

except SessionNotFoundError as e:
    # Session deleted
    create_new_session()

except AuthenticationError:
    # Invalid credentials
    redirect_to_login()

except ConnectionError:
    # Network issues
    show_offline_message()

except LLMProviderError as e:
    # External service error
    if e.is_retriable:
        schedule_retry()
    else:
        show_error(e.message)
```

### Pattern 2: Smart Retry Logic

```python
import asyncio
from shadai import ShadaiError

async def query_with_retry(shadai, query: str, max_retries: int = 3):
    """Retry only retriable errors."""
    for attempt in range(max_retries):
        try:
            async for chunk in shadai.query(query):
                print(chunk, end="")
            return  # Success

        except ShadaiError as e:
            # Check if error is retriable
            if e.is_retriable and attempt < max_retries - 1:
                wait = 2 ** attempt  # Exponential backoff
                print(f"\n⏳ Retrying in {wait}s...")
                await asyncio.sleep(wait)
            else:
                # Don't retry non-retriable errors
                print(f"\n❌ Error (not retriable): {e.message}")
                raise
```

### Pattern 3: User-Friendly Messages

```python
from shadai import ShadaiError

def get_user_message(error: ShadaiError) -> dict:
    """Convert exception to UI-friendly format."""

    if isinstance(error, ConfigurationError):
        return {
            "title": "⚙️ Setup Required",
            "message": error.message,
            "action": "Configure Settings"
        }

    elif isinstance(error, KnowledgePointsLimitExceededError):
        return {
            "title": "📊 Quota Reached",
            "message": error.message,
            "action": "Upgrade Plan"
        }

    elif isinstance(error, ConnectionError):
        return {
            "title": "🌐 Connection Error",
            "message": "Unable to connect to Shadai",
            "action": "Retry"
        }

    else:
        return {
            "title": "❌ Error",
            "message": error.message,
            "action": "Retry" if error.is_retriable else "Contact Support"
        }
```

---

## Exception Attributes Reference

All exceptions inherit these attributes from `ShadaiError`:

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | str | Human-readable error message for display |
| `error_code` | str | Machine-readable code (e.g., "SESSION_NOT_FOUND") |
| `error_type` | str | Error category (validation_error, resource_error, etc.) |
| `context` | dict | Additional debugging information |
| `is_retriable` | bool | Whether operation can be retried |
| `suggestion` | str \| None | Optional actionable suggestion |

---

## Error Types Reference

| Error Type | Description | Typical Action |
|------------|-------------|----------------|
| `validation_error` | Invalid input or parameters | Fix input and retry |
| `authentication_error` | Invalid credentials | Re-authenticate |
| `authorization_error` | Insufficient permissions or quota | Upgrade or wait |
| `resource_error` | Resource not found or exists | Check resource |
| `external_service_error` | Third-party service failure | Retry later |
| `system_error` | Internal server error | Contact support |

---

## Best Practices

### ✅ Do This

```python
# 1. Catch specific exceptions
except ConfigurationError as e:
    show_setup_modal(e.context['config_key'])

# 2. Check retry flag
except ShadaiError as e:
    if e.is_retriable:
        schedule_retry()

# 3. Use error context
except KnowledgePointsLimitExceededError as e:
    show_usage(e.context['current_value'], e.context['max_allowed'])

# 4. Display suggestions
except ShadaiError as e:
    if e.suggestion:
        show_suggestion(e.suggestion)
```

### ❌ Don't Do This

```python
# Don't catch all and ignore
except:
    pass  # Silent failure

# Don't expose technical details
except ShadaiError as e:
    print(e.context)  # Shows internal details

# Don't retry non-retriable errors
except ShadaiError as e:
    retry()  # Might retry auth errors
```

---

## See Also

- [Error Handling Guide](../guides/error-handling.md) - Comprehensive guide with examples
- [Best Practices](../advanced/best-practices.md) - Production patterns
- [Shadai Client API](shadai-client.md) - Main client interface
