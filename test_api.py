"""
Script para probar la API REST
"""
import os
import requests
import json

# Configuración
API_URL = "http://localhost:8001"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def test_api_status():
    """Prueba el estado de la API"""
    print("\n=== Probando estado de la API ===")
    response = requests.get(f"{API_URL}/")
    print(f"Respuesta: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_upload_csv(table_name, file_path):
    """Prueba la carga de un archivo CSV"""
    print(f"\n=== Probando carga de CSV para {table_name} ===")
    response = requests.post(
        f"{API_URL}/upload-from-path/{table_name}",
        json={"file_path": file_path},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Respuesta: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 201

def test_batch_insert(table_name, data):
    """Prueba la inserción por lotes"""
    print(f"\n=== Probando inserción por lotes para {table_name} ===")
    response = requests.post(
        f"{API_URL}/batch/{table_name}",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Respuesta: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 201

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("Iniciando pruebas de la API REST...")
    
    # Probar estado de la API
    if not test_api_status():
        print("Error: La API no está disponible. Asegúrate de que esté en ejecución.")
        return
    
    # Probar carga de CSV
    departments_csv = os.path.join(DATA_DIR, "departments.csv")
    jobs_csv = os.path.join(DATA_DIR, "jobs.csv")
    employees_csv = os.path.join(DATA_DIR, "hired_employees.csv")
    
    test_upload_csv("departments", departments_csv)
    test_upload_csv("jobs", jobs_csv)
    test_upload_csv("hired_employees", employees_csv)
    
    # Probar inserción por lotes
    departments_batch = [
        {"id": 12, "department": "Quality Assurance"},
        {"id": 13, "department": "Customer Support"}
    ]
    
    jobs_batch = [
        {"id": 183, "job": "Data Scientist"},
        {"id": 184, "job": "DevOps Engineer"}
    ]
    
    employees_batch = [
        {
            "id": 2000,
            "name": "John Doe",
            "datetime": "2022-01-01T10:00:00Z",
            "department_id": 5,
            "job_id": 10
        },
        {
            "id": 2001,
            "name": "Jane Smith",
            "datetime": "2022-01-02T11:30:00Z",
            "department_id": 3,
            "job_id": 15
        }
    ]
    
    test_batch_insert("departments", departments_batch)
    test_batch_insert("jobs", jobs_batch)
    test_batch_insert("hired_employees", employees_batch)
    
    print("\n=== Pruebas completadas ===")

if __name__ == "__main__":
    main()
