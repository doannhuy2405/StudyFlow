import uuid

def test_register(client):
    test_user = {
        "fullname": "Test User",
        "email": f"test_{uuid.uuid4()}@example.com",
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "password": "test123"
    }

    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 200
    assert "token" in response.json()

def test_login(client):
    # Test với user đã đăng ký
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "test123"
    })
    assert response.status_code == 200
    assert "token" in response.json()

def test_invalid_login(client):
    # Test với thông tin sai
    response = client.post("/auth/login", json={
        "username": "wronguser",
        "password": "wrongpass"
    })
    assert response.status_code == 400