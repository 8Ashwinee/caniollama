# caniollama

**Does your local Ollama model actually support tool calling?** `caniollama` runs a fixed, versioned test suite against your models and tells you.

```bash
uvx caniollama check                    # all local models
uvx caniollama check qwen2.5-coder:7b   # one model
uvx caniollama check --submit           # opt in to share results
```

Each model gets one of four outcomes per case:

| Outcome | Meaning |
|---|---|
| ✅ Native | Uses the proper `tool_calls` field |
| 🟡 Fallback | Emits tool JSON inside message content |
| ❌ Rejected | Backend refuses the `tools` parameter |
| ⚠️ Error | Timeout or other failure |

## Next steps

- [Install](installation.md) the CLI or self-host the registry.
- Read what is (and isn't) sent when you submit: [Privacy](privacy.md).
- Building a tool on top of the results? See [API integration](api-integration.md).
- Want to contribute? See [CONTRIBUTING](https://github.com/AnjalLLL/caniollama/blob/main/CONTRIBUTING.md).
