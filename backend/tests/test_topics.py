def test_create_topic(client, auth_token):
    topic_data = {
        "name": "Test Topic",
        "description": "Test Description",
        "lessons": []
    }
    
    response = client.post(
        "/topics",
        json=topic_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_topics(client, auth_token):
    response = client.get(
        "/topics",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)