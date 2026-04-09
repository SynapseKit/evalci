#!/usr/bin/env python3
"""EvalCI entrypoint — runs synapsekit test, posts PR comment, sets Action outputs."""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request


def get_input(name: str, default: str = "") -> str:
    """Read an Action input from INPUT_* env var."""
    return os.environ.get(f"INPUT_{name.upper().replace('-', '_')}", default).strip()


def set_output(name: str, value: str) -> None:
    """Write an Action output to GITHUB_OUTPUT file."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{name}={value}\n")
    else:
        # Fallback for older runners
        print(f"::set-output name={name}::{value}")


def get_pr_number() -> str | None:
    """Extract PR number from GITHUB_REF (refs/pull/123/merge)."""
    ref = os.environ.get("GITHUB_REF", "")
    match = re.match(r"refs/pull/(\d+)/", ref)
    return match.group(1) if match else None


def post_pr_comment(token: str, repo: str, pr_number: str, body: str) -> None:
    """Post a comment on a GitHub PR via REST API."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    payload = json.dumps({"body": body}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status not in (200, 201):
                print(f"Warning: PR comment returned status {resp.status}", file=sys.stderr)
    except urllib.error.HTTPError as e:
        print(f"Warning: failed to post PR comment: {e}", file=sys.stderr)


def build_comment(results: list[dict], threshold: float) -> str:
    """Build a markdown PR comment table from eval results."""
    rows = []
    for r in results:
        icon = "✅" if r.get("passed") else "❌"
        name = r.get("name", "unknown")
        score = r.get("score")
        cost = r.get("cost_usd")
        latency = r.get("latency_ms")

        score_str = f"{score:.3f}" if score is not None else "—"
        cost_str = f"${cost:.4f}" if cost is not None else "—"
        latency_str = f"{int(latency)}ms" if latency is not None else "—"

        rows.append(f"| {icon} | {name} | {score_str} | {cost_str} | {latency_str} |")

    passed = sum(1 for r in results if r.get("passed"))
    total = len(results)
    table = "\n".join(rows)

    return f"""## EvalCI Results

| | Test | Score | Cost | Latency |
|---|---|---|---|---|
{table}

**{passed}/{total} passed** · Threshold: `{threshold:.2f}` · [SynapseKit EvalCI](https://synapsekit.github.io/synapsekit-docs/)"""


def main() -> int:
    path = get_input("path", ".")
    threshold = get_input("threshold", "0.7")
    fail_on_regression = get_input("fail_on_regression", "false").lower() == "true"
    github_token = get_input("github_token") or os.environ.get("GITHUB_TOKEN", "")

    # Build synapsekit test command
    cmd = [
        "synapsekit", "test", path,
        "--format", "json",
        "--threshold", threshold,
    ]
    if fail_on_regression:
        cmd.append("--fail-on-regression")

    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    raw_output = result.stdout.strip()
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Parse JSON output
    try:
        # synapsekit test may mix log lines with JSON — find the JSON array
        json_match = re.search(r"(\[.*\])", raw_output, re.DOTALL)
        if json_match:
            results = json.loads(json_match.group(1))
        else:
            results = json.loads(raw_output)
    except json.JSONDecodeError:
        print(f"Error: could not parse JSON output:\n{raw_output}", file=sys.stderr)
        return 1

    # Compute summary stats
    passed_count = sum(1 for r in results if r.get("passed"))
    failed_count = sum(1 for r in results if not r.get("passed"))
    total_count = len(results)
    scores = [r["score"] for r in results if r.get("score") is not None]
    mean_score = sum(scores) / len(scores) if scores else 0.0

    # Set Action outputs
    set_output("passed", str(passed_count))
    set_output("failed", str(failed_count))
    set_output("total", str(total_count))
    set_output("mean-score", f"{mean_score:.4f}")

    # Print summary to logs
    print(f"\nEvalCI Summary: {passed_count}/{total_count} passed · mean score: {mean_score:.3f}")
    for r in results:
        icon = "✅" if r.get("passed") else "❌"
        print(f"  {icon} {r.get('name', 'unknown')} — score: {r.get('score', '—')}")

    # Post PR comment
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    pr_number = get_pr_number()

    if github_token and repo and pr_number:
        comment = build_comment(results, float(threshold))
        post_pr_comment(github_token, repo, pr_number, comment)
        print(f"\nPosted PR comment on {repo}#{pr_number}")
    else:
        if not pr_number:
            print("\nNot a PR context — skipping comment")
        elif not github_token:
            print("\nWarning: no GITHUB_TOKEN — skipping comment", file=sys.stderr)

    # Exit code mirrors synapsekit test exit code
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
