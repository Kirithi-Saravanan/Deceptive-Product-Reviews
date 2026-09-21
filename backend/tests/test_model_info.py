def test_model_info_returns_real_artifacts_data(client):
    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["selected_model"] == "Combined Features + LogisticRegression"
    assert data["selected_threshold"] == 0.40
    assert "test_metrics" in data
    metrics = data["test_metrics"]
    assert "accuracy" in metrics
    assert "f1_macro" in metrics
    assert "roc_auc" in metrics
    assert "deceptive" in metrics
    assert "genuine" in metrics
