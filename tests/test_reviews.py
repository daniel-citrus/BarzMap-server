def test_create_review(client):
    # Setup user
    user_res = client.post(
        "/api/users/",
        json={
            "email": "review@example.com",
            "name": "Reviewer",
            "auth0_id": "auth0|rev",
            "role": "user"
        }
    )
    user_id = user_res.json()["id"]

    # Setup park
    park_res = client.post(
        "/api/parks/",
        json={
            "name": "Review Park",
            "description": "Park",
            "latitude": 0,
            "longitude": 0,
            "address": "test",
            "city": "test",
            "state": "test",
            "country": "test",
            "postal_code": "00000"
        }
    )
    park_id = park_res.json()["id"]

    response = client.post(
        "/api/reviews/",
        json={
            "park_id": park_id,
            "user_id": user_id,
            "rating": 5,
            "comment": "Great park!"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Great park!"

def test_get_reviews_by_park(client):
    # Setup data
    user_res = client.post("/api/users/", json={"email": "r@e.com", "name": "R", "auth0_id": "a|r", "role": "user"})
    user_id = user_res.json()["id"]
    park_res = client.post("/api/parks/", json={"name": "P", "latitude": 0, "longitude": 0, "address": "a", "city": "c", "state": "s", "country": "c", "postal_code": "p"})
    park_id = park_res.json()["id"]
    
    client.post("/api/reviews/", json={"park_id": park_id, "user_id": user_id, "rating": 4, "comment": "Good"})

    response = client.get(f"/api/reviews/park/{park_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

