def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "strongpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Duplicate User",
            "email": test_user.email,
            "password": "somepassword123",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nobody@example.com",
            "password": "somepassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400


def test_get_me_authenticated(client, auth_headers, test_user):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert data["id"] == test_user.id


def test_get_me_unauthenticated(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
