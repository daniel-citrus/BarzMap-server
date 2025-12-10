def test_add_equipment_to_park(client):
    # Setup park
    park_res = client.post(
        "/api/parks/",
        json={
            "name": "Equip Park",
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

    # Setup equipment
    equip_res = client.post(
        "/api/equipment/",
        json={
            "name": "Test Bar",
            "description": "Bar",
            "icon_name": "bar"
        }
    )
    equip_id = equip_res.json()["id"]

    # Link them
    response = client.post(
        f"/api/park-equipment/park/{park_id}/equipment/{equip_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["park_id"] == park_id
    assert data["equipment_id"] == equip_id

def test_get_equipment_for_park(client):
    # Setup data
    park_res = client.post("/api/parks/", json={"name": "P", "latitude": 0, "longitude": 0, "address": "a", "city": "c", "state": "s", "country": "c", "postal_code": "p"})
    park_id = park_res.json()["id"]
    equip_res = client.post("/api/equipment/", json={"name": "E", "description": "d", "icon_name": "i"})
    equip_id = equip_res.json()["id"]
    client.post(f"/api/park-equipment/park/{park_id}/equipment/{equip_id}")

    response = client.get(f"/api/park-equipment/park/{park_id}/equipment")
    assert response.status_code == 200
    data = response.json()
    # Depending on response format, might be list of equipment or junction objects
    assert isinstance(data, list)
    assert len(data) >= 1

