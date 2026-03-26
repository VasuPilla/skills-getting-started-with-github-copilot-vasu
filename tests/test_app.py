import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture(autouse=True)
def reset_activities():
    original_state = {
        activity_name: {
            'description': details['description'],
            'schedule': details['schedule'],
            'max_participants': details['max_participants'],
            'participants': list(details['participants']),
        }
        for activity_name, details in activities.items()
    }
    yield
    activities.clear()
    activities.update({
        activity_name: {
            'description': details['description'],
            'schedule': details['schedule'],
            'max_participants': details['max_participants'],
            'participants': list(details['participants']),
        }
        for activity_name, details in original_state.items()
    })


def test_root_redirect():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get('/', follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers['location'] == '/static/index.html'


def test_get_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get('/activities')

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert 'Chess Club' in data
    assert 'participants' in data['Chess Club']


def test_signup_for_activity_success():
    # Arrange
    client = TestClient(app)
    email = 'test.user@mergington.edu'

    # Act
    response = client.post(f'/activities/Chess Club/signup?email={email}')

    # Assert
    assert response.status_code == 200
    assert 'Signed up' in response.json()['message']

    response = client.get('/activities')
    assert email in response.json()['Chess Club']['participants']


def test_signup_for_activity_duplicate():
    # Arrange
    client = TestClient(app)
    email = 'duplicate.test@mergington.edu'
    client.post(f'/activities/Chess Club/signup?email={email}')

    # Act
    response = client.post(f'/activities/Chess Club/signup?email={email}')

    # Assert
    assert response.status_code == 400
    assert 'already signed up' in response.json()['detail']


def test_remove_participant_success():
    # Arrange
    client = TestClient(app)
    email = 'remove.test@mergington.edu'
    client.post(f'/activities/Chess Club/signup?email={email}')

    # Act
    response = client.delete(f'/activities/Chess Club/participants?email={email}')

    # Assert
    assert response.status_code == 200
    assert 'Removed' in response.json()['message']

    response = client.get('/activities')
    assert email not in response.json()['Chess Club']['participants']


def test_remove_participant_not_found():
    # Arrange
    client = TestClient(app)
    email = 'nonexistent@mergington.edu'

    # Act
    response = client.delete(f'/activities/Chess Club/participants?email={email}')

    # Assert
    assert response.status_code == 404
    assert 'Participant not found' in response.json()['detail']
