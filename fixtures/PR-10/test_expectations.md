# Expected behavior for PR-10

Preserve the useful search fix while separately identifying the unrelated change that permits zero-value mock charges.

Risk: **medium**

Relevant regression tests:
- `tests/test_products.py::test_search_trims_query`
- `tests/test_payments.py::test_mock_payment_rejects_zero_amount`
