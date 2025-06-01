"""
Utilidades para procesar archivos CSV
"""
import csv
import os
from typing import List, Dict, Any

def parse_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Lee un archivo CSV y lo convierte en una lista de diccionarios.
    
    Args:
        file_path: Ruta al archivo CSV.
        
    Returns:
        Lista de diccionarios con los datos del CSV.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe")
    
    data = []
    
    # Detectar el tipo de archivo por su nombre
    file_name = os.path.basename(file_path).lower()
    
    if 'department' in file_name:
        # Estructura para departments.csv: id, department
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) >= 2:
                    data.append({
                        'id': int(row[0]),
                        'department': row[1]
                    })
    
    elif 'job' in file_name:
        # Estructura para jobs.csv: id, job
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) >= 2:
                    data.append({
                        'id': int(row[0]),
                        'job': row[1]
                    })
    
    elif 'employee' in file_name or 'hired' in file_name:
        # Estructura para hired_employees.csv: id, name, datetime, department_id, job_id
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) >= 5:
                    # Manejar posibles valores nulos en department_id y job_id
                    department_id = int(row[3]) if row[3].strip() else None
                    job_id = int(row[4]) if row[4].strip() else None
                    
                    data.append({
                        'id': int(row[0]),
                        'name': row[1],
                        'datetime': row[2],
                        'department_id': department_id,
                        'job_id': job_id
                    })
    
    else:
        # Formato genérico para otros archivos CSV
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader, None)
            
            if headers:
                for row in csv_reader:
                    if len(row) == len(headers):
                        record = {}
                        for i, header in enumerate(headers):
                            record[header] = row[i]
                        data.append(record)
    
    return data

def validate_batch_size(data: List[Dict[str, Any]]) -> bool:
    """
    Valida que el tamaño del lote esté dentro del rango permitido (1-1000).
    
    Args:
        data: Lista de diccionarios con los datos a validar.
        
    Returns:
        True si el tamaño es válido, False en caso contrario.
    """
    return 1 <= len(data) <= 1000
