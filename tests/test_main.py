import os
import pytest
from main import User

from main import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    os.environ["DATABASE_URL"] = "sqlite:///memory:"
    client = app.test_client()

    db.drop_all()
    db.create_all()

    yield client


def test_no_user(client):
    response = client.get("/profiles/100")

    assert ("This user doesn't exist" in str(response.data))


def test_index_logged_in(client):
    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    response = client.get('/')
    assert ("skrito stevilo" in str(response.data))


def test_result_correct(client):
    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    user = db.query(User).first()

    user.secret_number = 22
    db.add(user)
    db.commit()

    response = client.post('/', data={"ugibanje": 22})

    assert b'Bravo, zadel si' in response.data


def test_result_incorrect_try_bigger(client):
    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    user = db.query(User).first()

    user.secret_number = 22
    db.add(user)
    db.commit()

    response = client.post('/', data={"ugibanje": 13})

    assert ("Number is too small" in str(response.data))

def test_result_incorrect_try_smaller(client):
    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    user = db.query(User).first()

    user.secret_number = 22
    db.add(user)
    db.commit()

    response = client.post('/', data={"ugibanje": 23})

    assert ("Number is too big" in str(response.data))

def test_profile(client):
    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    user = db.query(User).first()
    response = client.get('/profile/')

    assert ("Test User" in str(response.data))

def test_profile_edit(client):
    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    user = db.query(User).first()

    response = client.post('/profile/edit', data={"name": "Aljosa", "email": "Aljosa@lg.com"})

    assert ("Aljosa" in str(response.data))
    assert ("Aljosa@lg.com" in str(response.data))

def test_profile_delete(client):
    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    user = db.query(User).first()

    response = client.post('/profile/delete', follow_redirects=True)

    assert ("name" in str(response.data))

def test_all_users(client):
    response = client.get('/list')
    assert b'<h1>All users</h1>' in response.data
    assert b'Test User' not in response.data

    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    response = client.get('/list')
    assert b'<h1>All users</h1>' in response.data
    assert b'Test User' in response.data


def test_user_details(client):
    client.post('/login', data={"name": "Test User", "email": "test@user.com",
                                "password": "password123"}, follow_redirects=True)

    user = db.query(User).first()

    response = client.get('/profiles/{}'.format(user.uid))
    assert b'test@user.com' in response.data
    assert b'Test User' in response.data




