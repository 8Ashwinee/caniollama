# Cross-Platform Support

## Supported Platforms

caniollama is tested and supported on:

- **macOS** (darwin) - Intel and Apple Silicon
- **Linux** - x86_64 and ARM64
- **Windows** - via WSL (Windows Subsystem for Linux)

## Platform Detection

The CLI automatically detects the host OS using Python's `platform.system()` and normalizes it:

```python
def current_os() -> str:
    system = platform.system().lower()
    return {"darwin": "macos", "linux": "linux", "windows": "windows"}.get(system, system)
```

This value is included in all compatibility reports submitted to the registry.

## Ollama Discovery

The CLI discovers Ollama installations through the Ollama API at `http://localhost:11434` by default. This works consistently across all platforms because:

1. **Ollama runs as a service** on all platforms (macOS daemon, Linux systemd, Windows service in WSL)
2. **Standard API endpoint** is always `localhost:11434`
3. **No filesystem scanning** - we query the API, not the model storage directories

### Custom Ollama Host

If you're running Ollama on a non-standard port or remote host:

```bash
export OLLAMA_HOST=http://remote-host:11434
caniollama check
```

## Model Discovery

Models are discovered via `GET /api/tags` from the Ollama API:

```python
async def discover_models(client: OllamaClient) -> list[DiscoveredModel]:
    raw = await client.list_models()
    return [
        DiscoveredModel(name=m["name"], quantization=_guess_quantization(m))
        for m in raw
        if "name" in m
    ]
```

This works identically on all platforms since Ollama's API contract is platform-independent.

## Known Platform Differences

### macOS
- Ollama typically installs to `/Applications/Ollama.app`
- Models stored in `~/.ollama/models`
- Daemon managed by launchd

### Linux
- Installed via package manager or install script
- Models stored in `~/.ollama/models` or `/usr/share/ollama/.ollama/models`
- Service managed by systemd

### Windows (WSL)
- Ollama runs inside WSL distribution
- Access via `localhost:11434` from within WSL
- Native Windows Ollama support is experimental (use WSL)

## Testing Across Platforms

While the codebase is designed for cross-platform compatibility, **local development testing** has been primarily on macOS. Community testing on Linux and Windows/WSL is welcome.

To verify on your platform:

```bash
# Check Ollama is reachable
curl http://localhost:11434/api/version

# Run the CLI
uvx caniollama check

# Run test suite
cd compat-check
uv run pytest -v
```

If you encounter platform-specific issues, please report them at https://github.com/AnjalLLL/caniollama/issues with:
- Platform details (`uname -a` or `winver`)
- Ollama version (`ollama --version`)
- Error output

## CI Testing

GitHub Actions CI runs tests on:
- Ubuntu latest (linux)
- Python 3.10, 3.11, 3.12

Additional platform coverage (macOS, Windows) can be added to `.github/workflows/ci.yml` if needed.
