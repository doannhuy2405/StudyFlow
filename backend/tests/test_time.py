import time

def test_time_tracking(client, auth_token):
    # Start session
    start_res = client.post(
        "/timetracking/start",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert start_res.status_code == 200
    assert start_res.json()["is_running"] is True

    # Wait 1 second
    time.sleep(1)

    # Stop session
    stop_res = client.post(
        "/timetracking/stop",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert stop_res.status_code == 200
    assert stop_res.json()["duration"] >= 1