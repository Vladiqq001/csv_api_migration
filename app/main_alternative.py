"""
Configuración principal de la API REST (versión alternativa sin python-multipart)
"""
# Incluir nueva libreria con rutas
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import json
import shutil
from typing import List, Dict, Any

# Importar módulos propios
from app.database.create_db import create_database
from app.database.db_manager import DatabaseManager
from app.utils.csv_processor import parse_csv_file, validate_batch_size
from app.routes.sql_routes import router as sql_router

# Crear la aplicación FastAPI
app = FastAPI(
    title="API de Migración CSV",
    description="API REST para migrar datos desde archivos CSV a una base de datos SQL y realizar consultas analíticas",
    version="2.0.0"
)

# Asociamos el router de SQL
app.include_router(sql_router)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar la base de datos al iniciar la aplicación
@app.on_event("startup")
async def startup_event():
    db_path = create_database()
    print(f"Base de datos inicializada en: {db_path}")

# Endpoint para verificar el estado de la API
@app.get("/")
async def root():
    return {"message": "API de Migración CSV activa", "status": "OK"}

# Endpoint para cargar datos desde una ruta de archivo CSV
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
        db_manager = DatabaseManager()
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
        db_manager = DatabaseManager()
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
