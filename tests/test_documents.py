from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


def _mock_db_empty():
    db = MagicMock()
    db.query.return_value.all.return_value = []
    db.query.return_value.filter.return_value.first.return_value = None
    yield db


@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = _mock_db_empty
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_list_documents_empty(client):
    response = client.get("/documents/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_get_document_not_found(client):
    response = client.get("/documents/999/summarise")
    assert response.status_code == HTTPStatus.NOT_FOUND
