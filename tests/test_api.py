"""
Pruebas para la API principal
"""
import os
import pytest
from fastapi.testclient import TestClient
from app.main_updated import app
from app.database.create_db import create_database
from app.database.db_manager import DatabaseManager

# Cliente de prueba
client = TestClient(app)

# Configuración de prueba
@pytest.fixture(scope="module")
def setup_test_db():
    """Configura una base de datos de prueba"""
    # Crear base de datos de prueba
    test_db_path = os.path.join(os.path.dirname(__file__), "test_migration.db")
    
    # Si la base de datos ya existe, eliminarla
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Crear nueva base de datos de prueba
    create_database(test_db_path)
    
    # Configurar el gestor de base de datos para usar la base de datos de prueba
    db_manager = DatabaseManager(test_db_path)
    
    yield db_manager
    
    # Limpiar después de las pruebas
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_root_endpoint():
    """Prueba el endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API de Migración CSV activa", "status": "OK"}

def test_batch_insert_departments(setup_test_db):
    """Prueba la inserción por lotes de departamentos"""
    # Usar IDs aleatorios para evitar conflictos
    import random
    random_id1 = random.randint(1000, 9999)
    random_id2 = random.randint(10000, 99999)
    
    departments_batch = [
        {"id": random_id1, "department": "Product Management Test"},
        {"id": random_id2, "department": "Sales Test"}
    ]
    
    response = client.post(
        "/batch/departments",
        json=departments_batch
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")
    
    assert response.status_code == 201
    assert response.json()["records_inserted"] == 2

def test_batch_insert_jobs(setup_test_db):
    """Prueba la inserción por lotes de trabajos"""
    # Usar IDs aleatorios para evitar conflictos
    import random
    random_id1 = random.randint(1000, 9999)
    random_id2 = random.randint(10000, 99999)

    jobs_batch = [
        {"id": random_id1, "job": "Marketing Assistant"},
        {"id": random_id2, "job": "VP Sales"}
    ]
    
    response = client.post(
        "/batch/jobs",
        json=jobs_batch
    )
    
    assert response.status_code == 201
    assert response.json()["records_inserted"] == 2

def test_batch_insert_employees(setup_test_db):
    """Prueba la inserción por lotes de empleados"""
    # Usar IDs aleatorios para evitar conflictos
    import random
    random_idd1 = random.randint(1000, 9999)
    random_idd2 = random.randint(10000, 99999)

    random_idj1 = random.randint(1000, 9999)
    random_idj2 = random.randint(10000, 99999)

    random_ide1 = random.randint(1000, 9999)
    random_ide2 = random.randint(10000, 99999)

    # Primero, insertar departamentos y trabajos necesarios
    departments_batch = [
        {"id": random_idd1, "department": "Product Management"},
        {"id": random_idd2, "department": "Sales"}
    ]
    
    jobs_batch = [
        {"id": random_idj1, "job": "Marketing Assistant"},
        {"id": random_idj2, "job": "VP Sales"}
    ]
    
    client.post("/batch/departments", json=departments_batch)
    client.post("/batch/jobs", json=jobs_batch)
    
    # Ahora, insertar empleados
    employees_batch = [
        {
            "id": random_ide1,
            "name": "John Doe",
            "datetime": "2021-01-15T10:00:00Z",
            "department_id": random_idd1,
            "job_id": random_idj1
        },
        {
            "id": random_ide2,
            "name": "Jane Smith",
            "datetime": "2021-02-20T11:30:00Z",
            "department_id": random_idd2,
            "job_id": random_idj2
        }
    ]
    
    response = client.post(
        "/batch/hired_employees",
        json=employees_batch
    )
    
    assert response.status_code == 201
    assert response.json()["records_inserted"] == 2

def test_invalid_table_name():
    """Prueba con un nombre de tabla inválido"""
    response = client.post(
        "/batch/invalid_table",
        json=[{"id": 1, "name": "Test"}]
    )
    
    assert response.status_code == 400
    assert "Tabla no válida" in response.json()["detail"]

def test_batch_size_validation():
    """Prueba la validación del tamaño del lote"""
    # Crear un lote vacío (debería fallar)
    response = client.post(
        "/batch/departments",
        json=[]
    )
    
    assert response.status_code == 400
    assert "tamaño del lote" in response.json()["detail"]
