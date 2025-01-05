# Intelligence Client

A Python client for interacting with the SHADAI Intelligence API. This client provides a simple interface for document processing, querying, and session management.

## Installation

```bash
pip install shadai
```

## Requirements

- Python >= 3.12
- Environment Variables:
  - `INTELLIGENCE_API_KEY`: Your SHADAI Intelligence API key

## Quick Start

```python
import asyncio
from intelligence.core.session import Session

async def main():
    async with Session(type="standard", delete_session=True) as session:
        await session.ingest(input_dir=input_dir)

        await session.query(
            query="¿De qué habla la quinta enmienda?", display_in_console=True
        )

        await session.get_summary(
            display_in_console=True
        )

        await session.create_article(
            topic="Enmiendas de los estados unidos y su impacto en la sociedad",
            display_in_console=True,
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Asynchronous API interactions
- Automatic session management
- File ingestion with progress tracking
- Interactive query interface
- Robust error handling and retries
- Rich console output

## Session Configuration

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| type | str | Processing type ("light", "standard", "deep") | "standard" |
| llm_model | str | Language model to use | None |
| llm_temperature | float | Model temperature | None |
| llm_max_tokens | int | Maximum tokens for response | None |
| query_mode | str | Query processing mode | None |
| language | str | Response language | None |
| delete_session | bool | Auto-delete session on exit | True |

## Error Handling

The client includes comprehensive error handling for:
- Configuration errors
- API communication issues
- File processing problems
- Session management failures

## Development

To set up for development:

```bash
# Clone the repository
git clone <repository-url>

# Install with development dependencies
pip install -e ".[dev]"
```

## Author

SHADAI GROUP <jaisir@shadai.ai>
