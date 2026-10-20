# Expected behavior for PR-04

Accept the clearer error message but flag the unrelated SQLAlchemy version-range change and its runtime/database impact.

Risk: **medium**

Relevant regression tests:
- `tests/test_orders.py::test_checkout_rejects_insufficient_stock`
