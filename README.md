# EvalCI by SynapseKit

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-EvalCI-blue?logo=github)](https://github.com/marketplace/actions/evalci-by-synapsekit)

**LLM quality gates for every PR.** Run your `@eval_case` suites automatically and block merge if quality drops below threshold.

- Zero infrastructure — runs entirely in GitHub Actions
- 2-minute setup
- Works with any LLM provider (OpenAI, Anthropic, Gemini, and [30+ more](https://synapsekit.github.io/synapsekit-docs/))
- Posts a formatted results table as a PR comment
- Sets Action outputs for downstream steps

---

## Quickstart

Add `.github/workflows/eval.yml` to your repo:

```yaml
name: EvalCI

on:
  pull_request:

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: SynapseKit/evalci@v1
        with:
          path: tests/evals
          threshold: "0.80"
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

That's it. EvalCI will:
1. Install `synapsekit` into the runner
2. Discover and run all `@eval_case`-decorated functions under `tests/evals/`
3. Post a results table as a PR comment
4. Fail the check if any case scores below threshold

---

## Example eval file

```python
# tests/evals/test_rag.py
from synapsekit.testing import eval_case

@eval_case(min_score=0.80, max_cost_usd=0.01, max_latency_ms=3000)
def test_rag_relevancy(eval_context):
    result = my_rag_pipeline("What is SynapseKit?")
    return eval_context.score_relevancy(result, reference="SynapseKit is a Python library...")

@eval_case(min_score=0.75)
def test_rag_faithfulness(eval_context):
    result = my_rag_pipeline("How do I install SynapseKit?")
    return eval_context.score_faithfulness(result, context=retrieved_docs)
```

---

## PR Comment

EvalCI posts a comment like this on every PR:

> ## EvalCI Results
>
> | | Test | Score | Cost | Latency |
> |---|---|---|---|---|
> | ✅ | test_rag_relevancy | 0.850 | $0.0050 | 1200ms |
> | ❌ | test_rag_faithfulness | 0.650 | $0.0120 | 2500ms |
>
> **1/2 passed** · Threshold: `0.80` · [SynapseKit EvalCI](https://synapsekit.github.io/synapsekit-docs/)

---

## Inputs

| Input | Description | Default |
|---|---|---|
| `path` | Path to eval files or directory | `.` |
| `threshold` | Global minimum score (0.0–1.0) | `0.7` |
| `extras` | pip extras for synapsekit (e.g. `openai,anthropic`) | `openai` |
| `synapsekit-version` | synapsekit version to install, or `latest` | `latest` |
| `github-token` | Token for posting PR comments | `${{ github.token }}` |
| `fail-on-regression` | Fail if score regresses vs. baseline | `false` |
| `token` | EvalCI backend API token _(future)_ | — |

## Outputs

| Output | Description |
|---|---|
| `passed` | Number of eval cases that passed |
| `failed` | Number of eval cases that failed |
| `total` | Total number of eval cases run |
| `mean-score` | Mean score across all eval cases |

---

## Using outputs in downstream steps

```yaml
- uses: SynapseKit/evalci@v1
  id: eval
  with:
    path: tests/evals
- run: |
    echo "Passed: ${{ steps.eval.outputs.passed }}/${{ steps.eval.outputs.total }}"
    echo "Mean score: ${{ steps.eval.outputs.mean-score }}"
```

---

## Multiple providers

```yaml
- uses: SynapseKit/evalci@v1
  with:
    extras: "openai,anthropic"
    threshold: "0.75"
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Badge

```markdown
[![EvalCI](https://github.com/{owner}/{repo}/actions/workflows/eval.yml/badge.svg)](https://github.com/{owner}/{repo}/actions/workflows/eval.yml)
```

---

## About

EvalCI is built on [SynapseKit](https://synapsekit.github.io/synapsekit-docs/) — a lightweight Python library for building LLM applications with 30+ provider integrations and a built-in evaluation framework.

- [Documentation](https://synapsekit.github.io/synapsekit-docs/)
- [GitHub](https://github.com/SynapseKit/SynapseKit)
- [Issues](https://github.com/SynapseKit/evalci/issues)
