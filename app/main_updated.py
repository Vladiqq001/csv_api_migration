"""
Configuración principal de la API REST con integración de rutas SQL
y soporte para ambos métodos de carga (archivo y ruta)
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import shutil
from typing import List, Dict, Any, Optional

# Importar módulos propios
from app.database.create_db import create_database
from app.database.db_manager import DatabaseManager
from app.utils.csv_processor import parse_csv_file, validate_batch_size
from app.routes.sql_routes import router as sql_router

# Variables globales para modo de prueba
test_mode = False
test_db_manager = None

# Crear la aplicación FastAPI
app = FastAPI(
    title="API de Migración CSV",
    description="API REST para migrar datos desde archivos CSV a una base de datos SQL y realizar consultas analíticas",
    version="2.0.0"
)

# Incluir el router de SQL
app.include_router(sql_router)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para obtener el gestor de base de datos
def get_db_manager():
    """
    Obtiene una instancia del gestor de base de datos.
    En modo de prueba, devuelve la instancia configurada para pruebas.
    """
    global test_db_manager
    if test_mode and test_db_manager:
        return test_db_manager
    return DatabaseManager()

# Inicializar la base de datos al iniciar la aplicación
@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio de la aplicación.
    Inicializa la base de datos si no estamos en modo de prueba.
    """
    global test_mode
    if not test_mode:
        db_path = create_database()
        print(f"Base de datos inicializada en: {db_path}")
    else:
        print("Aplicación iniciada en modo de prueba")

# Endpoint para verificar el estado de la API
@app.get("/")
async def root():
    """
    Endpoint para verificar el estado de la API.
    
    Returns:
        Mensaje de estado y versión de la API.
    """
    return {"message": "API de Migración CSV activa", "status": "OK"}

# Endpoint para cargar un archivo CSV
@app.post("/upload/{table_name}")
async def upload_csv(table_name: str, file: UploadFile = File(...)):
    """
    Carga un archivo CSV en la tabla especificada.
    
    Args:
        table_name: Nombre de la tabla donde cargar los datos (departments, jobs, hired_employees).
        file: Archivo CSV a cargar.
        
    Returns:
        Mensaje de éxito y número de registros insertados.
    """
    # Validar el nombre de la tabla
    valid_tables = ["departments", "jobs", "hired_employees"]
    if table_name not in valid_tables:
        raise HTTPException(
            status_code=400, 
            detail=f"Tabla no válida. Debe ser una de: {', '.join(valid_tables)}"
        )
    
    # Guardar el archivo temporalmente
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        
        # Procesar el archivo CSV
        data = parse_csv_file(temp_file.name)
        
        # Validar el tamaño del lote
        if not validate_batch_size(data):
            raise HTTPException(
                status_code=400,
                detail="El tamaño del lote debe estar entre 1 y 1000 registros"
            )
        
        # Insertar los datos en la base de datos
        db_manager = get_db_manager()
        inserted_count = db_manager.insert_batch(table_name, data)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": f"Archivo CSV cargado exitosamente en la tabla {table_name}",
                "records_inserted": inserted_count
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Eliminar el archivo temporal
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

# Endpoint para cargar datos desde una ruta de archivo CSV (alternativa sin python-multipart)
@app.post("/upload-from-path/{table_name}")
async def upload_csv_from_path(table_name: str, file_path: str = Body(..., embed=True)):
    """
    Carga un archivo CSV desde una ruta específica en la tabla especificada.
    
    Args:
        table_name: Nombre de la tabla donde cargar los datos (departments, jobs, hired_employees).
        file_path: Ruta al archivo CSV en el sistema de archivos.
        
    Returns:
        Mensaje de éxito y número de registros insertados.
    """
    # Validar el nombre de la tabla
    valid_tables = ["departments", "jobs", "hired_employees"]
    if table_name not in valid_tables:
        raise HTTPException(
            status_code=400, 
            detail=f"Tabla no válida. Debe ser una de: {', '.join(valid_tables)}"
        )
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"El archivo {file_path} no existe"
            )
        
        # Procesar el archivo CSV
        data = parse_csv_file(file_path)
        
        # Validar el tamaño del lote
        if not validate_batch_size(data):
            raise HTTPException(
                status_code=400,
                detail="El tamaño del lote debe estar entre 1 y 1000 registros"
            )
        
        # Insertar los datos en la base de datos
        db_manager = get_db_manager()
        inserted_count = db_manager.insert_batch(table_name, data)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": f"Archivo CSV cargado exitosamente en la tabla {table_name}",
                "records_inserted": inserted_count
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para insertar un lote de registros
@app.post("/batch/{table_name}")
async def insert_batch(table_name: str, data: List[Dict[str, Any]] = Body(...)):
    """
    Inserta un lote de registros en la tabla especificada.
    
    Args:
        table_name: Nombre de la tabla donde insertar los datos (departments, jobs, hired_employees).
        data: Lista de diccionarios con los datos a insertar.
        
    Returns:
        Mensaje de éxito y número de registros insertados.
    """
    # Validar el nombre de la tabla
    valid_tables = ["departments", "jobs", "hired_employees"]
    if table_name not in valid_tables:
        raise HTTPException(
            status_code=400, 
            detail=f"Tabla no válida. Debe ser una de: {', '.join(valid_tables)}"
        )
    
    # Validar el tamaño del lote
    if not validate_batch_size(data):
        raise HTTPException(
            status_code=400,
            detail="El tamaño del lote debe estar entre 1 y 1000 registros"
        )
    
    try:
        # Insertar los datos en la base de datos
        db_manager = get_db_manager()
        inserted_count = db_manager.insert_batch(table_name, data)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": f"Lote insertado exitosamente en la tabla {table_name}",
                "records_inserted": inserted_count
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para truncar una tabla
@app.post("/truncate/{table_name}")
async def truncate_table(table_name: str):
    """
    Trunca (elimina todos los registros) de la tabla especificada.
    
    Args:
        table_name: Nombre de la tabla a truncar (departments, jobs, hired_employees).
        
    Returns:
        Mensaje de éxito.
    """
    # Validar el nombre de la tabla
    valid_tables = ["departments", "jobs", "hired_employees"]
    if table_name not in valid_tables:
        raise HTTPException(
            status_code=400, 
            detail=f"Tabla no válida. Debe ser una de: {', '.join(valid_tables)}"
        )
    
    try:
        # Truncar la tabla
        db_manager = get_db_manager()
        db_manager.execute_query(f"DELETE FROM {table_name}")
        
        # Reiniciar el contador de autoincremento (si se usa)
        db_manager.execute_query(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Tabla {table_name} truncada exitosamente"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
