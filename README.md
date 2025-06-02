# API REST para Migración CSV a SQL y Análisis de Datos

Este proyecto implementa una solución completa para migrar datos desde archivos CSV a una base de datos SQL y realizar análisis sobre estos datos mediante endpoints específicos.

## Resumen de Secciones

### Sección 1: API REST para Migración de Datos

En esta sección se desarrolló una API REST que permite:

- **Recibir datos históricos desde archivos CSV**
  - Carga de archivos mediante formulario web
  - Carga desde rutas de archivos locales
  
- **Cargar estos archivos en una base de datos SQLite**
  - Estructura de tablas para departments, jobs y hired_employees
  - Validación de datos y manejo de errores
  
- **Insertar transacciones por lotes**
  - Soporte para lotes de 1 hasta 1000 filas en una sola solicitud
  - Validación del tamaño del lote

### Sección 2: Consultas SQL y Funcionalidades Avanzadas

En esta sección se implementaron:

- **Endpoints analíticos para métricas específicas**
  - Número de empleados contratados por trabajo y departamento en 2021, dividido por trimestres
  - Departamentos que contrataron más empleados que la media en 2021
  
- **Pruebas automatizadas**
  - Tests unitarios para todos los endpoints
  - Configuración de entornos de prueba aislados
  
- **Containerización con Docker**
  - Dockerfile para empaquetar la aplicación
  - Configuración para despliegue en contenedores
  
- **Guía para despliegue en la nube (Se trabajó sobre AZURE)** 
  - Instrucciones para AWS, Google Cloud, Azure y Heroku
  - Consideraciones para entornos de producción

## Estructura del Proyecto

```
csv_api_migration/
│
├── app/
│   ├── database/
│   │   ├── create_db.py       # Creación de la base de datos
│   │   ├── db_manager.py      # Gestor de operaciones de base de datos
│   │   └── migration.db       # Base de datos SQLite (generada automáticamente)
│   │
│   ├── routes/
│   │   └── sql_routes.py      # Endpoints para consultas SQL analíticas
│   │
│   ├── utils/
│   │   ├── csv_processor.py   # Procesamiento de archivos CSV
│   │   └── db_utils.py        # Utilidades para gestión de base de datos
│   │
│   ├── main.py               # Punto de entrada original
│   ├── main_alternative.py   # Versión alternativa sin python-multipart
│   └── main_updated.py       # Versión unificada con todas las funcionalidades
│
├── data/                     # Directorio para archivos CSV
│
├── tests/                    # Pruebas automatizadas
│   ├── test_api.py           # Pruebas para la API principal
│   └── test_sql_routes.py    # Pruebas para las rutas SQL
│
├── Dockerfile                # Configuración para Docker
├── .dockerignore             # Archivos a ignorar en la imagen Docker
├── requirements.txt          # Dependencias del proyecto
├── cloud_deployment_guide.md # Guía para despliegue en la nube
└── README.md                 # Este archivo
```

## Endpoints Principales

### Endpoints de Migración (Sección 1)

- `GET /` - Verificar estado de la API
- `POST /upload/{table_name}` - Cargar archivo CSV (requiere python-multipart)
- `POST /upload-from-path/{table_name}` - Cargar CSV desde ruta (alternativa)
- `POST /batch/{table_name}` - Insertar lote de registros
- `POST /truncate/{table_name}` - Truncar tabla (eliminar todos los registros)

### Endpoints Analíticos (Sección 2)

- `GET /sql/employees-by-quarter` - Empleados por trimestre, trabajo y departamento
- `GET /sql/departments-above-mean` - Departamentos con contrataciones sobre la media

## Tecnologías Utilizadas

- **Backend**: FastAPI, Python 3.9+
- **Base de datos**: SQLite
- **Pruebas**: Pytest, TestClient
- **Containerización**: Docker
- **Despliegue**: AWS/Azure/GCP/Heroku (según guía)

## Ejecución del Proyecto

### Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Iniciar la API

```bash
# Versión completa unificada
uvicorn app.main_updated:app --host 127.0.0.1 --port 8001
```

### Ejecutar Pruebas

```bash
pytest -v tests/
```

### Construir y Ejecutar con Docker

```bash
# Construir imagen
docker build -t csv-api-migration .

# Ejecutar contenedor
docker run -p 8001:8001 csv-api-migration
```

## Ejemplos de Uso

### Cargar un archivo CSV

```bash
curl -X POST "http://localhost:8001/upload/departments" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@/ruta/a/departments.csv"
```

### Consultar empleados por trimestre

```bash
curl -X GET "http://localhost:8001/sql/employees-by-quarter" -H "accept: application/json"
```

## Despliegue en la Nube

Consulta el archivo `cloud_deployment_guide.md` para instrucciones detalladas sobre cómo desplegar la aplicación en diferentes plataformas de nube.
