import os
import json
from fastapi import HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from pydantic import BaseModel

# Crea un router para las rutas en este archivo
router = APIRouter()
DATA_FOLDER = "Economy"


class Item(BaseModel):
  name: str
  value: int = 0
  description: str = "None"
  inventory: str = "None"
  duration: str = "None"
  stock: str = "None"
  role_required: str = "None"
  role_given: str = "None"
  role_removed: str = "None"
  required_balance: str = "None"
  reply: str = "None"

def save_server_data(server_id: str, data: dict):
  folder_path = f"{DATA_FOLDER}/{server_id}"
  file_path = f"{folder_path}/data.json"
  with open(file_path, "w") as file:
    json.dump(data, file, indent=4)


def load_server_data(server_id: str):
  folder_path = f"{DATA_FOLDER}/{server_id}"
  file_path = f"{folder_path}/data.json"
  if os.path.exists(file_path):
    with open(file_path, "r") as file:
      return json.load(file)
  else:
    raise HTTPException(status_code=400,
                        detail="El servidor ya está inicializado.")


@router.post("/api/add_item/{server_id}/")
async def add_item_to_server(server_id: str, item: Item):
    data = load_server_data(server_id)

    # Agregar el nuevo item a la lista de items en los datos del servidor
    data["items"].append(item.dict())

    # Guardar los datos actualizados en el archivo
    folder_path = f"{DATA_FOLDER}/{server_id}"
    file_path = f"{folder_path}/data.json"
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    return JSONResponse(content={"message": "Item agregado correctamente."}, status_code=201)


