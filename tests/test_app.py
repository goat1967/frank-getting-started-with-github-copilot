import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Test client fixture for FastAPI app"""
    return TestClient(app)


def test_get_activities(client):
    """Test GET /activities returns all activities"""
    # Arrange - no special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Check that some known activities are present
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Ensure student is not already signed up (clean state)
    response = client.get("/activities")
    initial_participants = response.json()[activity_name]["participants"]
    if email in initial_participants:
        # Clean up if already there
        client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]
    
    # Verify student was added to participants
    response = client.get("/activities")
    updated_participants = response.json()[activity_name]["participants"]
    assert email in updated_participants


def test_signup_for_activity_already_signed_up(client):
    """Test signup when student is already signed up"""
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already in participants
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]


def test_signup_for_activity_not_found(client):
    """Test signup for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity_success(client):
    """Test successful unregistration from an activity"""
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"  # Already in participants
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity_name}" in data["message"]
    
    # Verify student was removed from participants
    response = client.get("/activities")
    updated_participants = response.json()[activity_name]["participants"]
    assert email not in updated_participants


def test_unregister_from_activity_not_signed_up(client):
    """Test unregistration when student is not signed up"""
    # Arrange
    activity_name = "Soccer Team"
    email = "notsignedup@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up for this activity" in data["detail"]


def test_unregister_from_activity_not_found(client):
    """Test unregistration from non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]