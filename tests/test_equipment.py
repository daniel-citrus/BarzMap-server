def test_create_equipment(client):
    response = client.post(
        "/api/equipment/",
        json={
            "name": "Pull-up Bar",
            "description": "Standard bar",
            "icon_name": "pullup"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pull-up Bar"
    assert "id" in data

def test_get_equipment(client):
    client.post(
        "/api/equipment/",
        json={
            "name": "Pull-up Bar",
            "description": "Standard bar",
            "icon_name": "pullup"
        },
    )
    response = client.get("/api/equipment/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

