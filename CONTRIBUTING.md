# Contributing to EvalCI

Thanks for your interest in contributing! EvalCI is a GitHub Action built on [SynapseKit](https://github.com/SynapseKit/SynapseKit).

## Ways to contribute

- Report bugs via [Issues](https://github.com/SynapseKit/evalci/issues/new?template=bug_report.yml)
- Request features via [Issues](https://github.com/SynapseKit/evalci/issues/new?template=feature_request.yml)
- Start a discussion via [Discussions](https://github.com/SynapseKit/evalci/discussions)
- Submit a pull request (see below)

## Development setup

```bash
git clone https://github.com/SynapseKit/evalci.git
cd evalci
pip install synapsekit[openai]
```

The Action has two files to work with:
- `action.yml` — composite Action definition (inputs, outputs, steps)
- `entrypoint.py` — pure stdlib Python runner (no extra deps)

## Running the entrypoint locally

```bash
INPUT_PATH=. \
INPUT_THRESHOLD=0.7 \
INPUT_FAIL_ON_REGRESSION=false \
INPUT_GITHUB_TOKEN="" \
GITHUB_REF="refs/heads/main" \
GITHUB_REPOSITORY="owner/repo" \
python entrypoint.py
```

## Running tests

```bash
python -m pytest tests/ -v
# or without pytest:
python tests/test_entrypoint.py
```

## Submitting a PR

1. Fork the repo and create a branch: `git checkout -b fix/my-fix`
2. Make your changes
3. Test locally (see above)
4. Open a PR — the template will guide you

## Guidelines

- `entrypoint.py` must stay pure stdlib — no new dependencies
- Keep `action.yml` inputs backwards-compatible
- One concern per PR

## License

By contributing, you agree your contributions are licensed under the [Apache 2.0 License](LICENSE).
