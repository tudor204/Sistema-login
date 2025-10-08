from functools import wraps
from flask import make_response

def nocache(view):
    """
    Decorador que añade encabezados para deshabilitar la caché en el navegador.
    """
    @wraps(view)
    def decorated_view(*args, **kwargs):
        # Ejecuta la función de vista original para obtener la respuesta
        response = make_response(view(*args, **kwargs))
        
        # Añade los encabezados de seguridad de caché
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_view