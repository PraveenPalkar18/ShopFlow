# PR-05: Optimize order inventory updates

Reduce conditions in the inventory reservation update to simplify the checkout hot path.

Expected risk: **high**. See `expected_results.json` for the evaluation labels, impacted modules, and regression test identifiers. Ground truth is for evaluator use only; do not supply it to ChangeGuard.
