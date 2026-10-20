# Expected behavior for PR-06

Reject the fallback that authenticates an invalid token as the first user. Treat as a critical authentication regression.

Risk: **critical**

Relevant regression tests:
- `tests/test_auth.py::test_invalid_bearer_token_is_rejected`
