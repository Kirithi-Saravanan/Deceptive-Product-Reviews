def test_dashboard_summary_and_trends(client, auth_headers):
    # Add a genuine and a deceptive prediction
    client.post(
        "/api/predictions/",
        json={
            "product_name": "Product A",
            "rating": 5,
            "review_title": "Great",
            "review_text": "I really enjoyed using this product daily."
        },
        headers=auth_headers
    )
    client.post(
        "/api/predictions/",
        json={
            "product_name": "Product B",
            "rating": 1,
            "review_title": "Awful",
            "review_text": "Complete fake scam product do not buy under any circumstance."
        },
        headers=auth_headers
    )

    summary_res = client.get("/api/dashboard/summary", headers=auth_headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_reviews"] == 2
    assert summary["deceptive_reviews"] + summary["genuine_reviews"] == 2
    assert "average_rating" in summary
    assert len(summary["recent_analyses"]) == 2

    trends_res = client.get("/api/dashboard/trends", headers=auth_headers)
    assert trends_res.status_code == 200
    trends = trends_res.json()
    assert "ratings_distribution" in trends
    assert "prediction_trends" in trends
    assert len(trends["ratings_distribution"]) == 5  # 1★ through 5★
