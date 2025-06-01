import sqlite3
import os

def create_database():
    """
    Crea la base de datos SQLite con las tablas necesarias para la migración de datos.
    Si la base de datos ya existe, la función no hace nada.
    """
    # Obtener la ruta del directorio actual
    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(db_dir, 'migration.db')
    
    # Verificar si la base de datos ya existe
    if os.path.exists(db_path):
        print(f"La base de datos ya existe en: {db_path}")
        return db_path
    
    # Crear la conexión a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear las tablas
    cursor.execute('''
    CREATE TABLE departments (
        id INTEGER PRIMARY KEY,
        department VARCHAR(100) NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY,
        job VARCHAR(100) NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE hired_employees (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        datetime TIMESTAMP NOT NULL,
        department_id INTEGER,
        job_id INTEGER,
        FOREIGN KEY (department_id) REFERENCES departments(id),
        FOREIGN KEY (job_id) REFERENCES jobs(id)
    )
    ''')
    
    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()
    
    print(f"Base de datos creada exitosamente en: {db_path}")
    return db_path

if __name__ == "__main__":
    create_database()
