def test_create_fast_job(client):
    payload = {"type": "fast", "payload": {"x": 1}}

    response = client.post("/api/jobs/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["type"] == "fast"
    assert data["status"] == "PENDING"
    assert data["payload"]["x"] == 1


def test_list_jobs(client):
    # create job
    client.post("/api/jobs/", json={"type": "fast"})

    response = client.get("/api/jobs/")
    assert response.status_code == 200

    jobs = response.json()
    assert len(jobs) >= 1
