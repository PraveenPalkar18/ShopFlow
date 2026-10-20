# Expected behavior for PR-08

Identify that the default disables admin authorization and recommend an explicit secure default plus environment-specific opt-in.

Risk: **high**

Relevant regression tests:
- `tests/test_products.py::test_non_admin_cannot_create_product`
