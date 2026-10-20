# Expected behavior for PR-05

Identify that the stock guard was removed and can allow negative inventory. Recommend checkout, insufficient-stock, and concurrent reservation coverage.

Risk: **high**

Relevant regression tests:
- `tests/test_orders.py::test_checkout_rejects_insufficient_stock`
