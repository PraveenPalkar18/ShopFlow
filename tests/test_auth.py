from tests.helpers import register_and_login


def test_registration_login_and_authenticated_profile(client):
    headers = register_and_login(client)
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "buyer@example.com"
    assert response.json()["is_admin"] is False


def test_protected_cart_requires_authentication(client):
    assert client.get("/cart").status_code == 401
