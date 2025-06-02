"""
Utilidades para la gestión de base de datos
"""
# Variables globales para modo de prueba
test_mode = False
test_db_manager = None

def get_db_manager():
    """
    Obtiene una instancia del gestor de base de datos.
    En modo de prueba, devuelve la instancia configurada para pruebas.
    """
    from app.database.db_manager import DatabaseManager
    
    global test_mode, test_db_manager
    if test_mode and test_db_manager:
        return test_db_manager
    return DatabaseManager()
