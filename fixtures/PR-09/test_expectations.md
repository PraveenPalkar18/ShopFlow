# Expected behavior for PR-09

The endpoint changes order status but omits restocking reserved units. Recommend verifying state transition and stock restoration atomically.

Risk: **high**

Relevant regression tests:
- `tests/test_orders.py::test_order_cancellation_restores_inventory`
