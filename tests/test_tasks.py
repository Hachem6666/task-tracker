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


def test_patch_empty_json_object_returns_existing_task_unchanged(client):
    create_response = client.post("/tasks", json={"title": "Original", "description": "Initial description"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == task_id
    assert body["title"] == "Original"
    assert body["description"] == "Initial description"


def test_create_task_with_due_date_and_tags_returns_201(client):
    response = client.post("/tasks", json={
        "title": "Plan launch",
        "due_date": "2026-08-01T00:00:00Z",
        "tags": ["backend", "urgent"],
    })

    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] is not None
    assert body["tags"] == ["backend", "urgent"]


def test_create_task_with_blank_tag_returns_422(client):
    response = client.post("/tasks", json={
        "title": "Bad tags",
        "tags": ["valid", "   "],
    })

    assert response.status_code == 422


def test_create_task_with_too_many_tags_returns_422(client):
    response = client.post("/tasks", json={
        "title": "Too many tags",
        "tags": [f"tag{i}" for i in range(11)],
    })

    assert response.status_code == 422


def test_list_tasks_filter_overdue_returns_only_overdue_tasks(client):
    client.post("/tasks", json={
        "title": "Overdue task",
        "due_date": "2020-01-01T00:00:00Z",
    })
    client.post("/tasks", json={
        "title": "Future task",
        "due_date": "2099-01-01T00:00:00Z",
    })

    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Overdue task"


def test_done_task_with_past_due_date_is_not_overdue(client):
    create_response = client.post("/tasks", json={
        "title": "Finished task",
        "due_date": "2020-01-01T00:00:00Z",
    })
    task_id = create_response.json()["id"]

    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    response = client.get("/tasks", params={"overdue": True})

    assert response.status_code == 200
    body = response.json()
    assert all(t["id"] != task_id for t in body)


def test_list_tasks_filter_by_tag_case_insensitive(client):
    client.post("/tasks", json={"title": "Tagged task", "tags": ["Backend"]})
    client.post("/tasks", json={"title": "Other task", "tags": ["frontend"]})

    response = client.get("/tasks", params={"tag": "backend"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Tagged task"

def test_patch_null_title_returns_422(client):
    create_response = client.post("/tasks", json={"title": "Original title"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"title": None})

    assert response.status_code == 422

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.json()["title"] == "Original title"