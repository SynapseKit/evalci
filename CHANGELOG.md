# Changelog

All notable changes to EvalCI will be documented here.

## [v1.0.0] — 2026-04-09

### Added
- Initial release of EvalCI GitHub Action
- Composite Action with `path`, `threshold`, `extras`, `synapsekit-version`, `github-token`, `fail-on-regression`, `token` inputs
- Outputs: `passed`, `failed`, `total`, `mean-score`
- Automatic PR comment with results table (score, cost, latency per eval case)
- Exit code 0 on pass, 1 on failure or regression
- Works with any LLM provider supported by SynapseKit (30+)
