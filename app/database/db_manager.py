"""
Módulo para manejar las operaciones de base de datos
"""
import sqlite3
import os
from typing import List, Dict, Any, Tuple

class DatabaseManager:
    def __init__(self, db_path=None):
        """
        Inicializa el gestor de base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite. Si es None, 
                    se usa la ruta predeterminada.
        """
        if db_path is None:
            db_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(db_dir, 'migration.db')
        else:
            self.db_path = db_path
    
    def get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """
        Obtiene una conexión a la base de datos.
        
        Returns:
            Tupla con la conexión y el cursor.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        return conn, cursor
    
    def close_connection(self, conn: sqlite3.Connection):
        """
        Cierra una conexión a la base de datos.
        
        Args:
            conn: Conexión a cerrar.
        """
        if conn:
            conn.close()
    
    def insert_batch(self, table_name: str, data: List[Dict[str, Any]]) -> int:
        """
        Inserta un lote de registros en la tabla especificada.
        
        Args:
            table_name: Nombre de la tabla donde insertar los datos.
            data: Lista de diccionarios con los datos a insertar.
            
        Returns:
            Número de registros insertados.
        """
        if not data:
            return 0
        
        # Obtener las columnas del primer registro
        columns = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join(columns)
        
        # Preparar la consulta SQL
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # Preparar los valores para la inserción
        values = []
        for record in data:
            row_values = [record.get(column) for column in columns]
            values.append(tuple(row_values))
        
        # Ejecutar la inserción por lotes
        conn, cursor = self.get_connection()
        try:
            cursor.executemany(query, values)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            self.close_connection(conn)
    
    def execute_query(self, query: str, params=None):
        """
        Ejecuta una consulta SQL.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta (opcional).
            
        Returns:
            Resultado de la consulta.
        """
        conn, cursor = self.get_connection()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchall()
            conn.commit()
            return result
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            self.close_connection(conn)
