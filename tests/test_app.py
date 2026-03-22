from copy import deepcopy

from fastapi.testclient import TestClient
from src import app as app_module

client = TestClient(app_module.app)

ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


def setup_function(function):
    # Arrange: reset in-memory activities before each test for isolation
    app_module.activities = deepcopy(ORIGINAL_ACTIVITIES)


def test_get_activities():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # Act (verify state change)
    response2 = client.get("/activities")
    assert response2.status_code == 200
    assert email in response2.json()[activity_name]["participants"]


def test_signup_duplicate_fails():
    # Arrange
    email = "duplicate@mergington.edu"
    activity_name = "Programming Class"

    # Act
    first = client.post(f"/activities/{activity_name}/signup?email={email}")
    duplicate = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert first.status_code == 200
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Participant already signed up"


def test_delete_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "remove_me@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    # Act
    delete_response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert delete_response.status_code == 200
    assert "Unregistered" in delete_response.json()["message"]

    response_after = client.get("/activities")
    assert email not in response_after.json()[activity_name]["participants"]


def test_delete_nonexistent_participant():
    # Arrange
    activity_name = "Gym Class"
    missing_email = "notfound@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={missing_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
