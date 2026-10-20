# PR-02: Correct order total rounding

Round each line item to the currency precision before aggregating the order total. Add a regression test for fractional-cent prices.

Expected risk: **low-medium**. See `expected_results.json` for the evaluation labels, impacted modules, and regression test identifiers. Ground truth is for evaluator use only; do not supply it to ChangeGuard.
