def test_create_park(client):
    response = client.post(
        "/api/parks/",
        json={
            "name": "Central Park",
            "description": "Big park",
            "latitude": 40.785091,
            "longitude": -73.968285,
            "address": "New York, NY",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10024"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Central Park"
    assert "id" in data

def test_get_parks(client):
    client.post(
        "/api/parks/",
        json={
            "name": "Central Park",
            "description": "Big park",
            "latitude": 40.785091,
            "longitude": -73.968285,
            "address": "New York, NY",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10024"
        },
    )
    response = client.get("/api/parks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_get_park_by_id(client):
    create_res = client.post(
        "/api/parks/",
        json={
            "name": "Central Park",
            "description": "Big park",
            "latitude": 40.785091,
            "longitude": -73.968285,
            "address": "New York, NY",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10024"
        },
    )
    park_id = create_res.json()["id"]
    
    response = client.get(f"/api/parks/{park_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Central Park"

