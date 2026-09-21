def test_user_cannot_access_other_users_prediction(
    client, auth_headers, second_auth_headers, test_user, second_user
):
    # User 1 creates a prediction
    res1 = client.post(
        "/api/predictions/",
        json={
            "product_name": "User 1 Secret Product",
            "rating": 5,
            "review_title": "Private review",
            "review_text": "This review belongs solely to User 1."
        },
        headers=auth_headers
    )
    assert res1.status_code == 200
    user1_pred_id = res1.json()["id"]

    # User 2 attempts to get User 1's prediction by ID -> must receive 404
    res2_get = client.get(f"/api/predictions/{user1_pred_id}", headers=second_auth_headers)
    assert res2_get.status_code == 404
    assert res2_get.json()["detail"] == "Prediction not found"

    # User 2 attempts to delete User 1's prediction by ID -> must receive 404
    res2_del = client.delete(f"/api/predictions/{user1_pred_id}", headers=second_auth_headers)
    assert res2_del.status_code == 404

    # Verify User 1's prediction was NOT deleted
    res1_verify = client.get(f"/api/predictions/{user1_pred_id}", headers=auth_headers)
    assert res1_verify.status_code == 200
    assert res1_verify.json()["id"] == user1_pred_id

    # User 2's prediction list must NOT contain User 1's prediction
    res2_list = client.get("/api/predictions/", headers=second_auth_headers)
    assert res2_list.status_code == 200
    user2_items = res2_list.json()
    assert all(item["id"] != user1_pred_id for item in user2_items)

    # User 2's dashboard summary must show 0 reviews despite User 1 having reviews
    res2_dash = client.get("/api/dashboard/summary", headers=second_auth_headers)
    assert res2_dash.status_code == 200
    assert res2_dash.json()["total_reviews"] == 0
