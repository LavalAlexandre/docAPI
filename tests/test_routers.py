from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_patient_name():
    response = client.get("/documents/foo/patient-name")
    assert response.status_code == 200
    assert response.json() == {
        "document_id": "foo",
        "extracted_name": "Jean DUPONT",
    }
