from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


TEST_ACTIVITY = "Temporary Activity"
TEST_EMAIL = "student@example.edu"
ACTIVITY_PATH = quote(TEST_ACTIVITY, safe="")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setitem(
        activities,
        TEST_ACTIVITY,
        {
            "description": "Activity used for API tests",
            "schedule": "Mondays, 3:00 PM",
            "max_participants": 2,
            "participants": [],
        },
    )
    return TestClient(app)


def test_root_redirects_to_activity_page(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_includes_test_activity(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[TEST_ACTIVITY]["participants"] == []


def test_signup_adds_participant(client):
    # Arrange

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_PATH}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {TEST_EMAIL} for {TEST_ACTIVITY}"
    }
    assert activities[TEST_ACTIVITY]["participants"] == [TEST_EMAIL]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange

    # Act
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client):
    # Arrange
    activities[TEST_ACTIVITY]["participants"].append(TEST_EMAIL)

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_PATH}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_participant(client):
    # Arrange
    activities[TEST_ACTIVITY]["participants"].append(TEST_EMAIL)

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_PATH}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {TEST_EMAIL} from {TEST_ACTIVITY}"
    }
    assert activities[TEST_ACTIVITY]["participants"] == []


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_unregistered_participant(client):
    # Arrange

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_PATH}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"