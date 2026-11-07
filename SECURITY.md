# Security Policy

## Supported versions

Only the latest release of `caniollama` and the `caniollama-registry` image receive security fixes.

## Reporting a vulnerability

**Do not open a public issue.** Use GitHub's [private vulnerability reporting](https://github.com/AnjalLLL/caniollama/security/advisories/new), or email **anjalghimire890@gmail.com**.

Include steps to reproduce and the affected version. You should get a reply within 7 days. Once a fix ships, the advisory is published with credit unless you ask otherwise.

## Verifying releases

PyPI packages and container images are built in GitHub Actions with signed build provenance:

```bash
gh attestation verify caniollama-*.whl --repo AnjalLLL/caniollama
gh attestation verify oci://ghcr.io/anjallll/caniollama-registry:latest --repo AnjalLLL/caniollama
```
