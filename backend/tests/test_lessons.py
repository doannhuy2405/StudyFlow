def test_create_lesson(client, auth_token, test_topic_id):
    lesson_data = {
        "name": "Test Lesson",
        "note": "Test Note",
        "status": "not_done"
    }
    
    response = client.post(
        f"/topics/{test_topic_id}/lessons",
        json=lesson_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert "lesson" in response.json()

def test_update_lesson(client, auth_token, test_lesson_id):
    update_data = {
        "status": "done",
        "note": "Updated note"
    }
    
    response = client.put(
        f"/lessons/{test_lesson_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["msg"] == "Lesson updated"