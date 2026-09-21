def test_create_prediction_persisted_to_db(client, auth_headers, test_user):
    payload = {
        "product_name": "Noise Cancelling Headphones",
        "rating": 5,
        "review_title": "Outstanding sound quality",
        "review_text": "These headphones have incredible clarity and block out all subway noise. Highly satisfied."
    }
    response = client.post("/api/predictions/", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["product_name"] == payload["product_name"]
    assert data["rating"] == payload["rating"]
    assert data["review_title"] == payload["review_title"]
    assert data["review_text"] == payload["review_text"]
    assert data["user_id"] == test_user.id
    assert "id" in data
    assert data["predicted_label"] in ("Genuine", "Deceptive")
    assert data["threshold_used"] == 0.40
    assert 0.0 <= data["probability_deceptive"] <= 1.0
    assert 0.0 <= data["probability_genuine"] <= 1.0


def test_get_predictions_history(client, auth_headers):
    # Post two predictions
    for i in range(2):
        client.post(
            "/api/predictions/",
            json={
                "product_name": f"Product {i}",
                "rating": 4,
                "review_title": f"Title {i}",
                "review_text": f"Review content number {i} with sufficient text."
            },
            headers=auth_headers
        )

    response = client.get("/api/predictions/", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2


def test_get_prediction_by_id(client, auth_headers):
    create_res = client.post(
        "/api/predictions/",
        json={
            "product_name": "Test Watch",
            "rating": 3,
            "review_title": "Decent watch",
            "review_text": "Battery lasts a day, looks nice."
        },
        headers=auth_headers
    )
    pred_id = create_res.json()["id"]

    get_res = client.get(f"/api/predictions/{pred_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == pred_id


def test_delete_prediction(client, auth_headers):
    create_res = client.post(
        "/api/predictions/",
        json={
            "product_name": "Temporary Item",
            "rating": 1,
            "review_title": "Broke immediately",
            "review_text": "Stopped working within ten minutes."
        },
        headers=auth_headers
    )
    pred_id = create_res.json()["id"]

    del_res = client.delete(f"/api/predictions/{pred_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # Ensure it is now gone
    get_res = client.get(f"/api/predictions/{pred_id}", headers=auth_headers)
    assert get_res.status_code == 404
