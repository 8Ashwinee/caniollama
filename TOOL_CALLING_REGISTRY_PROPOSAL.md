# Project Proposal: A Living Compatibility Registry for Local Model Tool-Calling

## The problem, stated precisely

"Does this model support tool calling?" has three different true answers that all look identical from the outside:

1. **Yes, natively** — the model was trained on structured function-calling and reliably returns a proper `tool_calls` field.
2. **Sort of** — the model knows tool-calling exists (from training data about the format) but *decides independently* whether to use it, or emits the intent as JSON-shaped text inside `content` instead of the structured field.
3. **No, and Ollama tells you so** — the backend rejects the request outright (a 400) the moment `tools` is included, before any generation even happens.

You hit all three of these first-hand while building `localgate code`: `llama3` fell into category 3, `qwen2.5-coder` fell into category 1/2 depending on the exact turn, and the only way you found out was by testing it yourself, live, with no prior source of truth to check.

**What exists today to answer this question:** one-time blog-post benchmarks ("Best Ollama Model for Tool Calling 2026," etc.) that are accurate on the day they're published and stale the moment Ollama ships a new version, a model gets re-quantized, or a new model drops. There is no continuously-updated, community-sourced answer to "does *this* model, at *this* quantization, on *this* Ollama version, actually call tools reliably?" — every builder is left rediscovering this the hard way, individually, over and over.

## The idea

A small, focused open-source project with two halves:

1. **A CLI tool** (`compat-check` or similar — naming below) that runs a **standardized test suite** against whatever model is currently pulled locally: a handful of fixed prompts designed to distinguish the three categories above (does it return structured `tool_calls`? does it fall back to JSON-in-content? does the backend reject the request entirely? how does it behave with 1 tool vs. 5? does it handle multi-turn tool results correctly?).
2. **An opt-in, privacy-respecting submission mechanism**: after running the suite, the tool asks — not assumes — whether to submit the *result* (model name, quantization, Ollama version, pass/fail per test category) to a public aggregated registry. **Never the prompts, never the model's actual output content** — just the compatibility signal itself.

The registry becomes a public, browsable, continuously-current answer — the same role [caniuse.com](https://caniuse.com) plays for browser feature support, but for "can this local model actually call tools."

## Final goal / what success looks like

Someone deciding which model to pull for an agentic project should be able to check one place and get a current, real answer — not read a six-month-old blog post, not discover it themselves through a failed request in production. Concretely, success looks like:

- A live dashboard: search "qwen2.5-coder," see pass/fail rates across quantizations and recent Ollama versions, sourced from real runs, updated continuously as the community runs the tool.
- Tool builders (localgate included, but this should work for *anyone* building on Ollama — Cline, Continue.dev, custom agents) can query the registry's data programmatically, so a `/model` picker can surface a real compatibility signal instead of guessing.
- The project becomes the de facto reference the community points to instead of re-litigating "which model actually supports tools" in every Discord/GitHub issue thread.

## Principles (the boundaries that keep this trustworthy)

- **Opt-in, always.** No telemetry is submitted without an explicit prompt at the end of a run, every time — not a one-time consent buried in a config file.
- **Metadata only, never content.** Model name, Ollama version, quantization level, and pass/fail per test category — never the actual prompts or model outputs. This isn't a benchmark-quality/leaderboard project; it's narrowly about "does the plumbing work," which needs far less data than people might assume, and should ask for even less than it could.
- **Vendor-neutral.** Not a localgate feature — a standalone project localgate (and everyone else) can optionally integrate with. Tying it to one tool's brand would undermine the "authoritative shared reference" goal.
- **Open data.** The aggregated registry itself should be freely queryable/exportable, not locked behind an account or a paid tier — the entire value proposition is being the trusted, open answer.

## Explicit non-goals

- **Not a general model-quality benchmark.** This says nothing about how *good* a model's tool-calling reasoning is, only whether the plumbing (structured output, request handling) works at all. Quality benchmarking is a much bigger, more subjective project already being done elsewhere.
- **Not a replacement for Ollama's own documentation.** It's a live, empirical supplement to it — Ollama's docs say what's *supposed* to work; this tracks what actually does, in practice, across versions.
- **Not scoped to localgate.** If this only ever serves localgate's own users, it's not worth building as a separate project — fold it into `/model` and stop there. The point of standing it up separately is that it's useful to the whole Ollama-building community, which is also what makes people willing to contribute data to it.

## Suggested name candidates (verify availability before committing, same as before)

- `toolcallwatch` — descriptive, available-sounding
- `caniollama` — deliberately evokes caniuse.com's role, memorable
- `localtoolcheck` — plain and clear, if you'd rather undersell than oversell

## Where this connects back to localgate (optional, not required)

Once this exists as its own project with real data, localgate's `/model` picker (from `UPDATE_EXISTING_FEATURES.md`) becomes a natural first consumer: instead of just listing locally pulled models, it could annotate each one with a live compatibility signal pulled from this registry — "qwen2.5-coder:7b — tool calling: reliable (94% pass, 1.2k reports)" right in the picker. That's a good forcing function for validating the registry's API design early, but the registry itself should be built and useful standing alone first.
