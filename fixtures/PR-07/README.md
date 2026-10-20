# PR-07: Add validated discount codes at checkout

Allow a customer to apply an active discount code when creating an order. Validate code format and existence, apply the percentage before charging the mock provider, and cover valid and unknown codes.

Expected risk: **medium**. See `expected_results.json` for the evaluation labels, impacted modules, and regression test identifiers. Ground truth is for evaluator use only; do not supply it to ChangeGuard.
