# API Integration Guide

This guide is for tool builders who want to integrate with the caniollama registry API to query model compatibility data.

## Overview

The caniollama registry provides a read-only HTTP API for querying tool-calling compatibility results across models. This is useful for:

- Model selection tools (like localgate) that want to show compatibility badges
- CLI tools that recommend models based on tool-calling support
- Dashboards and monitoring systems
- Research and analysis tools

## Base URL

Production registry (once deployed): `TBD`

For local development: `http://localhost:8000`

## Authentication

None required for read-only endpoints. All GET endpoints are public.

## Endpoints

### GET /models

Returns a list of all models with submitted compatibility data.

**Response:** `200 OK`

```json
{
  "models": [
    {
      "model_name": "qwen2.5-coder:7b",
      "total_reports": 15,
      "pass_rate": 0.93
    },
    {
      "model_name": "llama3:8b",
      "total_reports": 8,
      "pass_rate": 0.75
    }
  ]
}
```

**Fields:**
- `model_name`: Full model name as it appears in Ollama
- `total_reports`: Number of compatibility reports submitted for this model
- `pass_rate`: Fraction of test cases that passed (0.0-1.0)

### GET /models/{model_name}

Returns detailed compatibility summary for a specific model.

**Response:** `200 OK` if model has data, `404 Not Found` if no reports exist

```json
{
  "model_name": "qwen2.5-coder:7b",
  "total_reports": 15,
  "pass_rate": 0.93,
  "case_breakdown": {
    "structured_tool_call": {
      "structured_pass": 14,
      "json_fallback": 1,
      "rejected": 0,
      "error": 0
    },
    "json_in_content": {
      "structured_pass": 12,
      "json_fallback": 3,
      "rejected": 0,
      "error": 0
    }
  }
}
```

**Fields:**
- `model_name`: The model identifier
- `total_reports`: Total number of reports aggregated
- `pass_rate`: Overall pass rate across all test cases
- `case_breakdown`: Per-test-case outcome distribution
  - Each test case maps to outcome counts
  - Outcomes: `structured_pass`, `json_fallback`, `rejected`, `error`

**404 Handling:** A `404` response means no compatibility data exists yet for this model. Your integration should treat this as "unknown compatibility" rather than an error.

### GET /stats

Returns global registry statistics.

**Response:** `200 OK`

```json
{
  "total_models": 23,
  "total_reports": 156,
  "distinct_contributors": 12
}
```

### GET /health

Health check endpoint.

**Response:** `200 OK`

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Integration Examples

### Python with httpx

```python
import httpx

REGISTRY_URL = "https://registry.caniollama.ghimireanjal.com.np"

def get_model_compatibility(model_name: str) -> dict | None:
    """Fetch compatibility data for a model, return None if no data exists."""
    response = httpx.get(f"{REGISTRY_URL}/models/{model_name}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

# Usage
result = get_model_compatibility("qwen2.5-coder:7b")
if result:
    print(f"Pass rate: {result['pass_rate']:.0%}")
else:
    print("No compatibility data available")
```

### JavaScript/TypeScript with fetch

```typescript
const REGISTRY_URL = "https://registry.caniollama.ghimireanjal.com.np";

interface ModelSummary {
  model_name: string;
  total_reports: number;
  pass_rate: number;
  case_breakdown?: Record<string, Record<string, number>>;
}

async function getModelCompatibility(
  modelName: string
): Promise<ModelSummary | null> {
  const response = await fetch(`${REGISTRY_URL}/models/${modelName}`);
  
  if (response.status === 404) {
    return null;
  }
  
  if (!response.ok) {
    throw new Error(`Registry error: ${response.statusText}`);
  }
  
  return response.json();
}
```

### curl

```bash
# List all models
curl https://registry.caniollama.ghimireanjal.com.np/models

# Get specific model details
curl https://registry.caniollama.ghimireanjal.com.np/models/qwen2.5-coder:7b

# Check if model has data (returns 404 if not)
curl -I https://registry.caniollama.ghimireanjal.com.np/models/unknown-model:latest
```

## Rate Limiting

Current rate limit: **10 requests per minute per IP** for read endpoints.

If you need higher limits for production use, please open an issue at https://github.com/AnjalLLL/caniollama/issues

## Interpreting Results

### Pass Rate Thresholds

Suggested interpretation:
- `>= 0.9`: Excellent tool-calling support
- `0.7 - 0.9`: Good support with occasional fallbacks
- `0.5 - 0.7`: Partial support, may require workarounds
- `< 0.5`: Poor tool-calling support

### Outcome Types

1. **`structured_pass`**: Model properly used the tool_calls field (best)
2. **`json_fallback`**: Model generated tool call JSON but in content field (acceptable fallback)
3. **`rejected`**: Backend rejected the tools parameter (incompatible)
4. **`error`**: Timeout or other error (needs investigation)

### Sample Size

Always check `total_reports` before making decisions. A model with 2 reports is less reliable than one with 50 reports.

## API Stability

**Current status:** Pre-1.0, but response schemas are stable

- Field names and types will not change in minor versions
- New fields may be added (safe to ignore)
- Endpoint paths will not change
- 404 behavior for unknown models is guaranteed

## Error Handling

All error responses follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

Common status codes:
- `200`: Success
- `404`: Model not found (no data exists)
- `422`: Invalid request (malformed model name)
- `429`: Rate limit exceeded
- `500`: Server error

## Support

- Issues: https://github.com/AnjalLLL/caniollama/issues
- Documentation: https://github.com/AnjalLLL/caniollama
- Registry source: https://github.com/AnjalLLL/caniollama/tree/main/compat-registry
