def charge_mock(amount: float) -> tuple[bool, str]:
    """Simulate an approval; no external payment service is contacted."""
    if amount <= 0:
        return False, "invalid_amount"
    return True, "mock-approved"
