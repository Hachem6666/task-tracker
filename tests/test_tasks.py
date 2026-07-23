def test_create_task_valid_returns_201_with_full_body(client):
    payload = {
        "title": "Buy milk",
        "description": "Remember the milk",
        "status": "InProgress",
        "priority": "High",
        "assignee": "alice",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]
    assert body["description"] == payload["description"]
    assert body["status"] == payload["status"]
    assert body["priority"] == payload["priority"]
    assert body["assignee"] == payload["assignee"]
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})

    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "priority": "Urgent"})

    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "unexpected": True})

    assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
    response = client.get("/tasks", params={"status": "Done"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "First", "priority": "High"})
    client.post("/tasks", json={"title": "Second", "priority": "Low"})

    response = client.get("/tasks", params={"priority": "High"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "First"
    assert body[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "fixture task"


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id missing-id not found"


def test_patch_partial_update_keeps_other_fields(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Original",
            "description": "Initial description",
            "status": "ToDo",
            "priority": "Medium",
            "assignee": "alice",
        },
    )
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"title": "Updated"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["title"] == "Updated"
    assert body["description"] == "Initial description"
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"
    assert body["assignee"] == "alice"


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/missing-id", json={"title": "Updated"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id missing-id not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(client):
    create_response = client.post("/tasks", json={"title": "Transition"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})

    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client):
    create_response = client.post("/tasks", json={"title": "Transition"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    assert response.status_code == 422


def test_patch_same_status_returns_422(client):
    create_response = client.post("/tasks", json={"title": "Transition"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})

    assert response.status_code == 422


def test_delete_existing_returns_204_no_body(client):
    create_response = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id missing-id not found"
