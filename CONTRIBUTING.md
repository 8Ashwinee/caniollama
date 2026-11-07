# Contributing to caniollama

Thank you for considering contributing to caniollama! This document provides guidelines and information for contributors.

## Ways to Contribute

### 1. Submit Compatibility Results

The easiest way to help is by running tests on your models:

```bash
uvx caniollama check --submit
```

This populates the public registry and helps the community make informed model choices.

### 2. Report Issues

Found a bug or compatibility problem? [Open an issue](https://github.com/AnjalLLL/caniollama/issues/new) with:

- caniollama version (`caniollama --version`)
- Ollama version (`ollama --version`)
- OS and Python version
- Full error output
- Model name if relevant

### 3. Improve Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples
- Improve installation instructions
- Translate to other languages

### 4. Add Test Cases

Want to expand the test suite? Great! But note:

**Important:** The test suite version (`SUITE_VERSION`) must be bumped whenever test cases change. This ensures compatibility results remain comparable over time.

Process:
1. Propose new test case in an issue first (discuss before implementing)
2. Add test case to `compat-check/src/compat_check/suite/cases.py`
3. Bump `SUITE_VERSION` in `compat-check/src/compat_check/suite/version.py`
4. Update tests and documentation
5. CI will enforce that version was bumped

### 5. Code Contributions

#### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/AnjalLLL/caniollama.git
cd caniollama

# Set up CLI package
cd compat-check
uv sync --dev
uv run pytest -v

# Set up registry package
cd ../compat-registry
uv sync --dev
uv run pytest -v

# Run schema compatibility tests
cd ..
uv run python -m pytest tests/test_e2e_schema_compat.py -v
```

#### Code Standards

- **Python 3.10+** minimum
- **Type hints** required for new code
- **Tests** required for new features
- **Black/Ruff** for formatting (run `uv run ruff format .`)
- **Mypy** for type checking (run `uv run mypy src`)

#### Running Checks

```bash
# In compat-check/ or compat-registry/
uv run ruff check .        # Linting
uv run mypy src            # Type checking
uv run pytest -v           # Tests
```

All checks must pass before PR approval.

#### Commit Messages

Use conventional commits format:

```
feat: add new test case for parallel tool calls
fix: handle timeout errors gracefully
docs: improve API integration examples
test: add test for cross-platform discovery
chore: update dependencies
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### 6. Registry Deployment Improvements

Know how to optimize the registry deployment? Contributions welcome:

- Performance improvements
- Better caching strategies
- Additional storage backends
- Monitoring and observability
- Cost optimization

## Pull Request Process

1. **Fork and branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes:**
   - Write code
   - Add tests
   - Update documentation

3. **Test locally:**
   ```bash
   uv run pytest -v
   uv run ruff check .
   uv run mypy src
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: describe your change"
   git push origin feature/my-new-feature
   ```

5. **Open PR:**
   - Describe what changed and why
   - Link related issues
   - Add screenshots if UI changes

6. **Code review:**
   - Address review feedback
   - Keep PR focused (one feature per PR)
   - Squash commits if requested

## Project Structure

```
caniollama/
├── compat-check/          # CLI package (PyPI: caniollama)
│   ├── src/
│   │   └── compat_check/
│   │       ├── cli.py     # Typer CLI entry point
│   │       ├── suite/     # Test cases and scoring
│   │       └── ...
│   └── tests/
├── compat-registry/       # FastAPI registry backend
│   ├── src/
│   │   └── compat_registry/
│   │       ├── main.py    # FastAPI app
│   │       ├── api/       # Route handlers
│   │       └── storage/   # Backend implementations
│   └── tests/
├── docs/                  # Documentation
└── tests/                 # Cross-package integration tests
```

## Key Design Principles

1. **Privacy-first:** Never submit prompts or model outputs
2. **Standardized:** Test suite must be reproducible
3. **Decoupled:** CLI and registry are independent
4. **Simple:** Prefer boring, proven solutions
5. **Documented:** Code should be self-explanatory

## Schema Changes

**Important:** The CLI and registry use hand-mirrored schemas (not shared code).

If you change `SubmissionPayload` or `SubmissionIn`:

1. Update both schemas in lockstep:
   - `compat-check/src/compat_check/models.py`
   - `compat-registry/src/compat_registry/schemas/submission.py`

2. Update `docs/registry/data-format.md` (source of truth)

3. Verify with integration test:
   ```bash
   uv run pytest tests/test_e2e_schema_compat.py -v
   ```

## Security

Found a security issue? **Do not open a public issue.**

Email [your-security-email] with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We'll respond within 48 hours.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- 💬 [Open a discussion](https://github.com/AnjalLLL/caniollama/discussions) (once enabled)
- 📫 [Create an issue](https://github.com/AnjalLLL/caniollama/issues/new)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards others

Unacceptable behavior will not be tolerated.

---

Thank you for contributing! 🎉
