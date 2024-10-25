import requests
from jwt_auth import generate_token

BASE_URL_INVENTARIO = "http://localhost:5001"

def llamar_a_inventario(endpoint, method='GET', data=None):
    token = generate_token("productos")
    headers = {'Authorization': token}
    url = f"{BASE_URL_INVENTARIO}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error en la llamada al servicio de inventario: {e}")
        return None
