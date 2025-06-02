"""
Pruebas para las rutas SQL
"""
import os
import pytest
from fastapi.testclient import TestClient
from app.main_alternative import app
from app.database.create_db import create_database
from app.database.db_manager import DatabaseManager

from app.utils.db_utils import test_mode, test_db_manager

# Cliente de prueba
client = TestClient(app)

# Configuración de prueba
@pytest.fixture(scope="module")
def setup_test_data():
    """Configura datos de prueba para las consultas SQL"""
    # Crear base de datos de prueba
    test_db_path = os.path.join(os.path.dirname(__file__), "test_sql.db")
    
    # Si la base de datos ya existe, eliminarla
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Crear nueva base de datos de prueba
    create_database(test_db_path)
    
    # Configurar el gestor de base de datos para usar la base de datos de prueba
    db_manager = DatabaseManager(test_db_path)
    
    # Insertar datos de prueba
    # Departamentos
    departments = [
        {"id": 1, "department": "Engineering"},
        {"id": 2, "department": "Sales"},
        {"id": 3, "department": "Marketing"},
        {"id": 4, "department": "HR"}  # Añadido un departamento más
    ]
    db_manager.insert_batch("departments", departments)
    
    # Trabajos
    jobs = [
        {"id": 1, "job": "Software Engineer"},
        {"id": 2, "job": "Sales Representative"},
        {"id": 3, "job": "Marketing Specialist"},
        {"id": 4, "job": "HR Manager"}  # Añadido un trabajo más
    ]
    db_manager.insert_batch("jobs", jobs)
    
    # Empleados (distribuidos por trimestres y departamentos)
    employees = []
    
    # Departamento 1 (Engineering) - Muchas contrataciones (muy por encima de la media)
    for i in range(1, 31):  # Aumentado de 20 a 30
        month = (i % 12) + 1
        employees.append({
            "id": i,
            "name": f"Engineer {i}",
            "datetime": f"2021-{month:02d}-01T10:00:00Z",
            "department_id": 1,
            "job_id": 1
        })
    
    # Departamento 2 (Sales) - Pocas contrataciones (por debajo de la media)
    for i in range(31, 36): # Aumentado de 21 a 31
        month = (i % 12) + 1
        employees.append({
            "id": i,
            "name": f"Sales {i}",
            "datetime": f"2021-{month:02d}-01T10:00:00Z",
            "department_id": 2,
            "job_id": 2
        })
    
    # Departamento 3 (Marketing) - Contrataciones medias (ligeramente por encima de la media)
    for i in range(36, 51):  # Aumentado de 10 a 15
        month = (i % 12) + 1
        employees.append({
            "id": i,
            "name": f"Marketing {i}",
            "datetime": f"2021-{month:02d}-01T10:00:00Z",
            "department_id": 3,
            "job_id": 3
        })

    # Departamento 4 (HR) - Muy pocas contrataciones (muy por debajo de la media)
    for i in range(51, 54):
        month = (i % 12) + 1
        employees.append({
            "id": i,
            "name": f"HR {i}",
            "datetime": f"2021-{month:02d}-01T10:00:00Z",
            "department_id": 4,
            "job_id": 4
        })    
    
    db_manager.insert_batch("hired_employees", employees)
    
    # Configurar la aplicación para usar esta base de datos
    import app.utils.db_utils as db_utils
    db_utils.test_mode = True
    db_utils.test_db_manager = db_manager

    yield db_manager

    # Limpiar después de las pruebas
    db_utils.test_mode = False
    db_utils.test_db_manager = None

def test_employees_by_quarter(setup_test_data):
    """Prueba el endpoint de empleados por trimestre"""
    response = client.get("/sql/employees-by-quarter")
    
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0
    
    # Verificar estructura de los datos
    assert "department" in data[0]
    assert "job" in data[0]
    assert "Q1" in data[0]
    assert "Q2" in data[0]
    assert "Q3" in data[0]
    assert "Q4" in data[0]
    
    # Verificar ordenamiento
    departments = [item["department"] for item in data]
    assert departments == sorted(departments)

def test_departments_above_mean(setup_test_data):
    """Prueba el endpoint de departamentos por encima de la media"""
    response = client.get("/sql/departments-above-mean")
    
    assert response.status_code == 200
    
    #data = response.json()
    #assert len(data) > 0
    data = response.json()
    assert len(data) > 0, "Debería haber al menos un departamento por encima de la media"
    
    
    # Verificar estructura de los datos
    assert "id" in data[0]
    assert "department" in data[0]
    assert "hired" in data[0]
    
    # Verificar ordenamiento (descendente por hired)
    hired_counts = [item["hired"] for item in data]
    assert hired_counts == sorted(hired_counts, reverse=True)
    
    # Verificar que Engineering esté en los resultados (tiene más contrataciones)
    engineering_present = any(item["department"] == "Engineering" for item in data)
    assert engineering_present, "Engineering debería estar por encima de la media"

    # Verificar que HR NO esté en los resultados (tiene pocas contrataciones)
    hr_absent = not any(item["department"] == "HR" for item in data)
    assert hr_absent, "HR debería estar por debajo de la media"