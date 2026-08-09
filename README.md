# caniollama

[![PyPI version](https://badge.fury.io/py/caniollama.svg)](https://pypi.org/project/caniollama/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Standardized compatibility checker for local Ollama model tool-calling support.**

Does your local LLM actually support function calling? Run `caniollama check` to find out.

## What is this?

A CLI tool that tests whether Ollama models properly support tool/function calling. It runs a standardized test suite and categorizes models into:

1. ✅ **Native support** - Uses proper `tool_calls` field
2. 🟡 **Fallback mode** - Generates tool JSON in content
3. ❌ **Rejected** - Backend refuses tools parameter
4. ⚠️ **Error** - Timeouts or other failures

Results can be optionally submitted to a public registry for community benefit.

## Quick Start

```bash
# No installation needed - use uvx (recommended)
uvx caniollama check

# Or with pipx
pipx run caniollama check

# Or install permanently
pip install caniollama
```

### Check a specific model

```bash
caniollama check qwen2.5-coder:7b
```

### Submit results to public registry

```bash
caniollama check --submit
```

**Privacy:** Only metadata is submitted (model name, Ollama version, pass/fail outcomes). Never prompts or model outputs. See [docs/privacy.md](docs/privacy.md).

## Why?

Not all models that claim tool-calling support actually work with your local Ollama setup. This tool:

- **Tests real behavior** - Not based on model cards or documentation
- **Standardized suite** - Same tests across all models for fair comparison  
- **Community data** - Public registry helps everyone make informed choices
- **Integration-ready** - API for tools to query compatibility

## Repository Structure

This monorepo contains:

- **`compat-check/`** - CLI tool (published to PyPI as `caniollama`)
- **`compat-registry/`** - Public registry backend (FastAPI service)
- **`docs/`** - Documentation and guides
- **`tests/`** - Cross-package integration tests

## Documentation

- 📖 [CLI Usage Guide](compat-check/README.md)
- 🔌 [API Integration Guide](docs/api-integration.md) - For tool builders
- 🚀 [Deployment Guide](compat-registry/DEPLOYMENT.md) - For hosting the registry
- 🌍 [Cross-Platform Support](docs/cross-platform-support.md)
- 🔒 [Privacy Policy](docs/privacy.md)

### For Developers

- [Architecture Overview](COMPAT_REGISTRY_PROJECT_ARCHITECTURE.md)
- [Design Proposal](TOOL_CALLING_REGISTRY_PROPOSAL.md)
- [Release Checklist](RELEASE_CHECKLIST.md)

## Requirements

- **Ollama** running locally (or accessible via `OLLAMA_HOST`)
- **Python 3.10+** (automatically handled by uvx/pipx)
- At least one model pulled in Ollama

## Example Output

```
🔍 Discovered 3 models locally:
  • qwen2.5-coder:7b
  • llama3:8b  
  • mistral:7b

Running compatibility checks...

✓ qwen2.5-coder:7b - Pass rate: 100% (4/4 passed)
  ✓ structured_tool_call: PASS
  ✓ json_in_content: PASS
  ✓ control_no_tools: PASS
  ✓ multiple_tools: PASS

⚠ llama3:8b - Pass rate: 75% (3/4 passed)
  ✓ structured_tool_call: PASS
  ⚠ json_in_content: FALLBACK (JSON in content field)
  ✓ control_no_tools: PASS
  ✓ multiple_tools: PASS

❌ mistral:7b - Pass rate: 0% (0/4 passed)
  ❌ structured_tool_call: REJECTED (backend refused tools)
  ❌ json_in_content: REJECTED
  ✓ control_no_tools: PASS
  ❌ multiple_tools: REJECTED
```

## API Integration

Query the public registry programmatically (once deployed):

```python
import httpx

response = httpx.get("https://registry.caniollama.dev/models/qwen2.5-coder:7b")
data = response.json()
print(f"Pass rate: {data['pass_rate']:.0%}")
```

See [API Integration Guide](docs/api-integration.md) for full documentation.

## Quick Development Setup

```bash
# CLI
cd compat-check && uv sync && uv run pytest

# Registry backend
cd compat-registry && uv sync && uv run pytest
uv run uvicorn compat_registry.main:app --reload   # http://localhost:8000/docs
```

## Contributing

Contributions welcome! Ways to help:

- 🧪 Run tests on your models and submit results
- 🐛 Report bugs or compatibility issues  
- 📝 Improve documentation
- 🎯 Suggest new test cases for the suite
- 🔧 Submit PRs for bug fixes or features

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- [Ollama](https://ollama.ai) - Run LLMs locally

## Support

- 📫 [Open an issue](https://github.com/AnjalLLL/caniollama/issues)

---

**Status:** Pre-1.0 (v0.1.0 ready for release)  
**Stars appreciated!** ⭐
