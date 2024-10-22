import jwt
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta

# Clave secreta para firmar los tokens JWT
SECRET_KEY = "tu_clave_secreta_aqui"  # Cambia esto por una clave secreta más segura

def generate_token(service_name):
    """
    Genera un token JWT para un servicio específico.
    El token es válido por 1 hora.
    """
    payload = {
        "service": service_name,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    """
    Verifica si el token JWT es válido y no ha expirado.
    Retorna el nombre del servicio si el token es válido, de lo contrario, None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["service"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """
    Decorador para proteger rutas que requieren autenticación.
    Verifica que el token JWT esté presente y sea válido.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token faltante"}), 401
        
        # El token puede venir como "Bearer <token>", entonces separamos la palabra "Bearer"
        token = token.split()[1] if " " in token else token
        service = verify_token(token)
        
        if not service:
            return jsonify({"error": "Token inválido o expirado"}), 401
        
        return f(*args, **kwargs)
    
    return decorated
