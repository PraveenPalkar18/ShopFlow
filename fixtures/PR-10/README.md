# PR-10: Fix product search query whitespace

Trim leading and trailing whitespace from catalogue search terms so user queries return expected matches.

Expected risk: **medium**. See `expected_results.json` for the evaluation labels, impacted modules, and regression test identifiers. Ground truth is for evaluator use only; do not supply it to ChangeGuard.
