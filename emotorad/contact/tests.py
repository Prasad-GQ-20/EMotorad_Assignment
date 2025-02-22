import pytest
import random
import time
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from contact.models import Contact
from contact.exceptions import ContactMergeConflict, DatabaseConnectionError

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def mock_session():
    with patch("contact.views.Session") as mock:
        yield mock()

@pytest.fixture
def mock_contact_query(mock_session):
    return mock_session.query.return_value

@pytest.mark.django_db
def test_identify_valid_email(api_client, mock_session, mock_contact_query):
    mock_contact_query.filter.return_value.all.return_value = []
    mock_session.commit.return_value = None
    response = api_client.post("/identify/", {"email": "test@example.com"})
    
    assert response.status_code == status.HTTP_200_OK
    assert "primaryContactId" in response.data
    assert "emails" in response.data
    assert "phoneNumbers" in response.data
    assert "secondaryContactIds" in response.data

@pytest.mark.django_db
def test_identify_existing_contact(api_client, mock_session, mock_contact_query):
    existing_contact = Contact(id=1, email="test@example.com", phoneNumber="1234567890")
    mock_contact_query.filter.return_value.all.return_value = [existing_contact]
    response = api_client.post("/identify/", {"email": "test@example.com"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["primaryContactId"] == 1
    assert "test@example.com" in response.data["emails"]

@pytest.mark.django_db
def test_identify_invalid_request(api_client):
    response = api_client.post("/identify/", {"invalid_field": "value"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data

@pytest.mark.django_db
def test_contact_merge_conflict(api_client, mock_session):
    mock_session.commit.side_effect = ContactMergeConflict()
    response = api_client.post("/identify/", {"email": "conflict@example.com"})
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "error" in response.data

@pytest.mark.django_db
def test_database_connection_error(api_client, mock_session):
    mock_session.commit.side_effect = DatabaseConnectionError()
    response = api_client.post("/identify/", {"email": "db_fail@example.com"})
    
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "error" in response.data

@pytest.mark.django_db
def test_identify_with_cache(api_client, mock_session, mock_contact_query):
    cache_key = "contact_1"
    cached_data = {
        "emails": ["cached@example.com"],
        "phones": ["9999999999"],
        "secondary_ids": [2, 3]
    }
    cache.set(cache_key, cached_data, 3600)
    
    response = api_client.post("/identify/", {"email": "cached@example.com"})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["emails"] == cached_data["emails"]
    assert response.data["phoneNumbers"] == cached_data["phones"]
    assert response.data["secondaryContactIds"] == cached_data["secondary_ids"]
