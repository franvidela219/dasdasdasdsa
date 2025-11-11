import requests

# --- Configuración IGDB ---
CLIENT_ID = "aio0y5syf7jlxq20qoy7768korw1me"
ACCESS_TOKEN = "pps4h1dpxrcyiuz04m725vf653obzw"
HEADERS = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {ACCESS_TOKEN}"}

# --- Funciones API ---
def buscar_juego(nombre, limit=8):
    url = "https://api.igdb.com/v4/games"
    query = f'''
    search "{nombre}";
    fields name, cover.image_id, summary, rating, platforms.name, screenshots.image_id, genres.name;
    limit {limit};
    '''
    response = requests.post(url, headers=HEADERS, data=query)
    if response.status_code == 200:
        juegos = response.json()
        juegos.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return juegos
    else:
        raise ValueError(f"Error API: {response.status_code}")

def obtener_url_cover(image_id, size="cover_big"):
    """Construye la URL de la portada.

    Acepta como entrada:
    - None -> devuelve None
    - str (image_id) -> construye la URL
    - dict que contiene la clave 'image_id' -> extrae el valor y construye la URL
    - lista/tuple cuyo primer elemento es un dict con 'image_id' -> extrae y construye la URL
    """
    if not image_id:
        return None

    # Si se pasa un dict con la forma {'image_id': 'co1abc'}, extraerlo
    if isinstance(image_id, dict):
        image_id = image_id.get("image_id")

    # Si se pasa una lista/tuple de capturas u objetos, intentar extraer del primero
    if isinstance(image_id, (list, tuple)) and len(image_id) > 0:
        first = image_id[0]
        if isinstance(first, dict):
            image_id = first.get("image_id")

    if not image_id:
        return None

    return f"https://images.igdb.com/igdb/image/upload/t_{size}/{image_id}.jpg"

def obtener_url_screenshot(image_id, size="original"):
    """Construye la URL de una captura.

    Igual que `obtener_url_cover`, acepta None, str, dict o lista/tuple.
    """
    if not image_id:
        return None

    if isinstance(image_id, dict):
        image_id = image_id.get("image_id")

    if isinstance(image_id, (list, tuple)) and len(image_id) > 0:
        first = image_id[0]
        if isinstance(first, dict):
            image_id = first.get("image_id")

    if not image_id:
        return None

    return f"https://images.igdb.com/igdb/image/upload/t_{size}/{image_id}.jpg"
