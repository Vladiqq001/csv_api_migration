"""
Rutas para consultas SQL específicas
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.db_utils import get_db_manager  # Importar desde db_utils en lugar de main_updated

router = APIRouter(
    prefix="/sql",
    tags=["sql"],
    responses={404: {"description": "Not found"}},
)

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.database.db_manager import DatabaseManager

router = APIRouter(
    prefix="/sql",
    tags=["sql"],
    responses={404: {"description": "Not found"}},
)

@router.get("/employees-by-quarter")
async def get_employees_by_quarter():
    """
    Obtiene el número de empleados contratados para cada trabajo y departamento en 2021,
    dividido por trimestres. La tabla está ordenada alfabéticamente por departamento y trabajo.
    """
    try:
        db_manager = get_db_manager() #DatabaseManager()
        query = """
        SELECT 
            d.department,
            j.job,
            SUM(CASE WHEN strftime('%m', datetime) BETWEEN '01' AND '03' THEN 1 ELSE 0 END) AS Q1,
            SUM(CASE WHEN strftime('%m', datetime) BETWEEN '04' AND '06' THEN 1 ELSE 0 END) AS Q2,
            SUM(CASE WHEN strftime('%m', datetime) BETWEEN '07' AND '09' THEN 1 ELSE 0 END) AS Q3,
            SUM(CASE WHEN strftime('%m', datetime) BETWEEN '10' AND '12' THEN 1 ELSE 0 END) AS Q4
        FROM 
            hired_employees he
        JOIN 
            departments d ON he.department_id = d.id
        JOIN 
            jobs j ON he.job_id = j.id
        WHERE 
            strftime('%Y', datetime) = '2021'
        GROUP BY 
            d.department, j.job
        ORDER BY 
            d.department, j.job
        """
        
        result = db_manager.execute_query(query)
        
        # Convertir el resultado a un formato JSON adecuado
        formatted_result = []
        for row in result:
            formatted_result.append({
                "department": row[0],
                "job": row[1],
                "Q1": row[2],
                "Q2": row[3],
                "Q3": row[4],
                "Q4": row[5]
            })
        
        return JSONResponse(
            status_code=200,
            content=formatted_result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/departments-above-mean")
async def get_departments_above_mean():
    """
    Obtiene la lista de IDs, nombres y número de empleados contratados de cada departamento
    que contrató más empleados que la media de empleados contratados en 2021 para todos los departamentos,
    ordenada por el número de empleados contratados (descendente).
    """
    try:
        db_manager = get_db_manager() #DatabaseManager()
        query = """
        WITH department_hires AS (
            SELECT 
                d.id,
                d.department,
                COUNT(*) AS hired
            FROM 
                hired_employees he
            JOIN 
                departments d ON he.department_id = d.id
            WHERE 
                strftime('%Y', datetime) = '2021'
            GROUP BY 
                d.id, d.department
        ),
        avg_hires AS (
            SELECT 
                AVG(hired) AS mean_hired
            FROM 
                department_hires
        )
        SELECT 
            dh.id,
            dh.department,
            dh.hired
        FROM 
            department_hires dh, 
            avg_hires av
        WHERE 
            dh.hired > av.mean_hired
        ORDER BY 
            dh.hired DESC
        """
        
        result = db_manager.execute_query(query)
        
        # Convertir el resultado a un formato JSON adecuado
        formatted_result = []
        for row in result:
            formatted_result.append({
                "id": row[0],
                "department": row[1],
                "hired": row[2]
            })
        
        return JSONResponse(
            status_code=200,
            content=formatted_result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
