import requests
from jwt_auth import generate_token

BASE_URL_PRODUCTOS = "http://localhost:5000"

def llamar_a_productos(endpoint, method='GET', data=None):
    token = generate_token("inventario")
    headers = {'Authorization': token}
    url = f"{BASE_URL_PRODUCTOS}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=20)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error en la llamada al servicio de productos: {e}")
        return None