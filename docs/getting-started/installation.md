# Installation

Get Shadai up and running in under 60 seconds.

## Requirements

- **Python 3.10+** (Python 3.12 recommended)
- **pip** or **uv** package manager

## Install via pip

```bash
pip install shadai
```

## Install via uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a blazingly fast Python package installer:

```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Shadai
uv pip install shadai
```

## Install from Source

For the latest development version:

```bash
git clone https://github.com/shadai/shadai-client.git
cd shadai-client
pip install -e .
```

## Verify Installation

```python
import shadai
print(shadai.__version__)  # Should print: 0.1.29
```

## Optional Dependencies

### Development Tools

```bash
pip install shadai[dev]
```

Includes:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `black` - Code formatter
- `mypy` - Type checker
- `ruff` - Fast linter

## System Dependencies

Shadai has minimal system dependencies - only `aiohttp` and `pydantic` are required. No heavy ML libraries needed!

## Troubleshooting

### ImportError: No module named 'shadai'

Make sure you're in the correct Python environment:

```bash
which python
pip list | grep shadai
```

### SSL Certificate Error

If you encounter SSL errors:

```bash
pip install --upgrade certifi
```

### Permission Denied

On Linux/Mac, you might need to use `--user`:

```bash
pip install --user shadai
```

## Next Steps

✅ Installation complete! Now let's set up authentication.

→ [Authentication Guide](authentication.md)
