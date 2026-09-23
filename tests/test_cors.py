def test_cors_preflight_allows_the_vite_origin(client):
    response = client.options(
        "/questions/1",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "http://localhost:5173"
    )
    assert "GET" in response.headers["access-control-allow-methods"]


def test_cors_does_not_allow_an_unknown_origin(client):
    response = client.options(
        "/questions/1",
        headers={
            "Origin": "https://unexpected.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" not in response.headers
