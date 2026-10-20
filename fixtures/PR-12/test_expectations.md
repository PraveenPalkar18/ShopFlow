# Expected behavior for PR-12

Treat the shared helper extraction as a behavior-preserving refactor. Existing registration and login tests are sufficient; avoid inflated risk or unnecessary new warnings.

Risk: **low**

Relevant regression tests:
- `tests/test_auth.py::test_registration_login_and_authenticated_profile`
