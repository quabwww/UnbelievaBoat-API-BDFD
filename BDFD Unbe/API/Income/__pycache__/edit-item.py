import os
import json
import requests
from fastapi import HTTPException, APIRouter
from typing import Union

router = APIRouter()
DATA_FOLDER = "Economy"


def role_exists(guild_id: str, role_id: int, bot_token: str) -> bool:
    # Construye los encabezados de la solicitud HTTP
    headers = {
        "Authorization": f"Bot {bot_token}"
    }

    # Realiza una solicitud GET a la API de Discord para obtener la lista de roles en el servidor
    response = requests.get(f"https://discord.com/api/v8/guilds/{guild_id}/roles", headers=headers)

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        # Obtiene la lista de roles del cuerpo de la respuesta en formato JSON
        roles = response.json()

        # Verifica si el ID del rol especificado está en la lista de roles
        for role in roles:
            if role["id"] == str(role_id):
                return True

    # Retorna False si el ID de rol no se encuentra en la lista de roles o si la solicitud falla
    return False


def convertir_a_segundos(solicitud: str) -> int:
    unidades = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'y': 31536000}
    resultado = 0
    cantidad = ''
    for caracter in solicitud:
        if caracter.isdigit():
            cantidad += caracter
        elif caracter in unidades:
            resultado += int(cantidad) * unidades[caracter]
            cantidad = ''
    if resultado == 0:
        raise HTTPException(status_code=400, detail="La duración proporcionada no es válida.")
    else:
        return resultado

@router.post("/api/edit_item/{guild_id}/")
async def edit_item(token_bot: str, guild_id: str, option: str, item_name: str, new_value: Union[str, int, float, bool]):

    if not os.path.exists(f"{DATA_FOLDER}/{guild_id}/data.json"):
        raise HTTPException(status_code=404, detail=f"El servidor con ID {guild_id} no existe.")

    
    VALID_OPTIONS = [
        "name", "value", "description", "inventory", "duration",
        "stock", "role-required", "role-given", "role-removed",
        "required-balance", "reply"
    ]
    if option not in VALID_OPTIONS:
        raise HTTPException(status_code=400, detail="La opción proporcionada no es válida.")

    
    if option in ["value", "stock", "required-balance"]:
        try:
            new_value = int(new_value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"El valor para '{option}' debe ser un número entero.")


    if option.startswith("role-"):
        bot_token = f"{token_bot}"
        if not role_exists(guild_id, int(new_value), bot_token):
            raise HTTPException(status_code=400, detail=f"El rol con ID {new_value} no existe en el servidor.")


    if option == "duration":
        try:
            new_value = convertir_a_segundos(new_value)
        except HTTPException as e:
            raise e


    with open(f"{DATA_FOLDER}/{guild_id}/data.json", "r") as file:
        data = json.load(file)

    item_found = False
    for item in data["items"]:
        if item["name"] == item_name:
            item_found = True
            item[option] = new_value

    if not item_found:
        raise HTTPException(status_code=404, detail=f"No se encontró el item con nombre '{item_name}' en el servidor con ID {guild_id}.")

    with open(f"{DATA_FOLDER}/{guild_id}/data.json", "w") as file:
        json.dump(data, file, indent=4)

    return {"message": f"El item '{item_name}' ha sido actualizado correctamente."}
