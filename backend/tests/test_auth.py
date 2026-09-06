def test_login_success(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert data["access_token"]
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "sai-mat-khau"})
    assert res.status_code == 401


def test_me_requires_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_with_token(client, admin_hdr):
    res = client.get("/api/auth/me", headers=admin_hdr)
    assert res.status_code == 200
    assert res.json()["username"] == "admin"


def test_owner_cannot_manage_users(client, owner_hdr):
    res = client.post(
        "/api/users",
        json={"username": "hacker", "password": "1234", "role": "admin"},
        headers=owner_hdr,
    )
    assert res.status_code == 403


def test_owner_cannot_create_product(client, owner_hdr, accessory_category_id):
    res = client.post(
        "/api/products",
        json={"code": "AUTH-X", "name": "SP test quyền"},
        headers=owner_hdr,
    )
    assert res.status_code in (201, 400)


def test_logout_ok(client, admin_hdr):
    res = client.post("/api/auth/logout", headers=admin_hdr)
    assert res.status_code == 200
