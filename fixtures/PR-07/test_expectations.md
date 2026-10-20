# Expected behavior for PR-07

Treat the coordinated validation, pricing, order, persistence, and checkout test changes as justified by the feature description; verify discount validation precedes mock charging.

Risk: **medium**

Relevant regression tests:
- `tests/test_orders.py::test_valid_discount_applies_to_checkout`
- `tests/test_orders.py::test_unknown_discount_is_rejected`
