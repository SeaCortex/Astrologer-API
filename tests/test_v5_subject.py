"""
Test per l'endpoint soggetto v5.

Obiettivi:
- Caso base OK con soggetto valido.
- Errore 422 quando mancano campi di localizzazione e non si fornisce geonames_username.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict

from fastapi.testclient import TestClient


# Soggetto d'esempio: Roma
ROME_SUBJECT: Dict[str, object] = {
    "name": "FastAPI Unit Test",
    "year": 1946,
    "month": 6,
    "day": 16,
    "hour": 10,
    "minute": 10,
    "longitude": 12.4963655,
    "latitude": 41.9027835,
    "city": "Roma",
    "nation": "IT",
    "timezone": "Europe/Rome",
}


def test_subject_ok(client: TestClient):
    resp = client.post("/api/v5/subject", json={"subject": deepcopy(ROME_SUBJECT)})
    assert resp.status_code == 200
    payload = resp.json()

    # Struttura di risposta chiara
    assert payload["status"] == "OK"
    subject = payload["subject"]

    # Campi salienti presenti e tipizzati
    for key in ("name", "city", "nation", "sun", "moon", "active_points", "lunar_phase"):
        assert key in subject
    assert subject["nation"] == "IT"
    assert isinstance(subject["sun"], dict)
    assert isinstance(subject["moon"], dict)
    assert isinstance(subject["active_points"], list) and subject["active_points"]


def test_subject_missing_location_returns_422(client: TestClient):
    # Rimuoviamo lat/lon/tz per forzare la validazione Pydantic
    invalid = deepcopy(ROME_SUBJECT)
    invalid.pop("latitude")
    invalid.pop("longitude")
    invalid.pop("timezone")

    resp = client.post("/api/v5/subject", json={"subject": invalid})
    assert resp.status_code == 422
    # Dettagli di validazione presenti
    body = resp.json()
    assert isinstance(body.get("detail"), list) and body["detail"]

