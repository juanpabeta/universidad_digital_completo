"""Meaningful role, enrollment and grade workflow checks."""

from datetime import date, timedelta
from decimal import Decimal


def auth(http, role: str) -> dict[str, str]:
    response = http.post(
        "/api/v1/auth/token",
        data={"username": f"{role.lower()}@example.com", "password": "ClaveSegura123!"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_university_workflow_and_access(client):
    http, ids = client
    admin = auth(http, "ADMINISTRADOR")
    teacher = auth(http, "DOCENTE")
    student = auth(http, "ESTUDIANTE")

    user = http.get("/api/v1/users/me", headers=student)
    assert user.status_code == 200
    assert "password_hash" not in user.text
    assert http.get("/api/v1/users", headers=student).status_code == 403

    subject = http.post(
        "/api/v1/subjects", headers=admin,
        json={"nombre": "Bases de datos", "codigo": "BD101", "creditos": 3,
              "id_docente": ids["DOCENTE"]},
    )
    assert subject.status_code == 201, subject.text
    subject_id = subject.json()["id_materia"]

    today = date.today()
    period = http.post(
        "/api/v1/periods", headers=admin,
        json={"nombre": "ACTUAL", "fecha_inicio": str(today - timedelta(days=2)),
              "fecha_fin": str(today + timedelta(days=30)), "estado": "ABIERTO"},
    )
    assert period.status_code == 201, period.text
    period_id = period.json()["id_periodo"]

    payload = {"id_materia": subject_id, "id_periodo": period_id}
    enrollment = http.post("/api/v1/enrollments", headers=student, json=payload)
    assert enrollment.status_code == 201, enrollment.text
    enrollment_id = enrollment.json()["id_inscripcion"]
    assert enrollment.json()["id_usuario"] == ids["ESTUDIANTE"]
    assert http.post("/api/v1/enrollments", headers=student, json=payload).status_code == 409

    grade = http.post(
        "/api/v1/grades", headers=teacher,
        json={"id_inscripcion": enrollment_id, "nota": "87.50", "tipo": "PARCIAL"},
    )
    assert grade.status_code == 201, grade.text
    assert http.get("/api/v1/grades", headers=student).json()[0]["nota"] == "87.50"
    assert http.post(
        "/api/v1/grades", headers=student,
        json={"id_inscripcion": enrollment_id, "nota": "100", "tipo": "FINAL"},
    ).status_code == 403
    assert http.post(
        "/api/v1/grades", headers=teacher,
        json={"id_inscripcion": enrollment_id, "nota": "101", "tipo": "FINAL"},
    ).status_code == 422

    report = http.get(f"/api/v1/reports/periods/{period_id}/subjects", headers=teacher)
    assert report.status_code == 200, report.text
    assert report.json()[0]["inscripciones_activas"] == 1
    assert Decimal(report.json()[0]["promedio_calificaciones"]) == Decimal("87.50")


def test_invalid_token_and_period_dates(client):
    http, _ids = client
    assert http.get("/api/v1/users/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
    admin = auth(http, "ADMINISTRADOR")
    invalid = http.post(
        "/api/v1/periods", headers=admin,
        json={"nombre": "INV", "fecha_inicio": "2026-10-10", "fecha_fin": "2026-10-01"},
    )
    assert invalid.status_code == 422
