def test_create_user(client):
    response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "auth0_id": "auth0|123456",
            "role": "user"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_get_users(client):
    # Create a user first
    client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "auth0_id": "auth0|123456",
            "role": "user"
        },
    )
    
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["email"] == "test@example.com"

def test_get_user_by_id(client):
    # Create user
    create_res = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "auth0_id": "auth0|123456",
            "role": "user"
        },
    )
    user_id = create_res.json()["id"]

    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_update_user(client):
    # Create user
    create_res = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "auth0_id": "auth0|123456",
            "role": "user"
        },
    )
    user_id = create_res.json()["id"]

    # Update
    response = client.put(
        f"/api/users/{user_id}",
        json={
            "id": user_id,
            "email": "updated@example.com",
            "name": "Updated Name",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["name"] == "Updated Name"

def test_delete_user(client):
    # Create user
    create_res = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "auth0_id": "auth0|123456",
            "role": "user"
        },
    )
    user_id = create_res.json()["id"]

    # Delete
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 200

    # Verify deleted
    get_res = client.get(f"/api/users/{user_id}")
    assert get_res.status_code == 404

