def test_create_image(client):
    # Setup park first
    park_res = client.post(
        "/api/parks/",
        json={
            "name": "Image Park",
            "description": "Park for images",
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
        "/api/images/",
        json={
            "park_id": park_id,
            "image_url": "http://example.com/image.jpg",
            "thumbnail_url": "http://example.com/thumb.jpg",
            "alt_text": "A nice park"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["park_id"] == park_id
    assert data["image_url"] == "http://example.com/image.jpg"

def test_get_images_by_park(client):
    # Setup park
    park_res = client.post(
        "/api/parks/",
        json={
            "name": "Image Park",
            "description": "Park for images",
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

    # Create image
    client.post(
        "/api/images/",
        json={
            "park_id": park_id,
            "image_url": "http://example.com/image.jpg",
            "thumbnail_url": "http://example.com/thumb.jpg",
            "alt_text": "A nice park"
        },
    )

    response = client.get(f"/api/images/park/{park_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

