# Importación de librerías de FastAPI y módulos estándar de Python
from fastapi import FastAPI, status, HTTPException, Depends # Herramientas principales de FastAPI
from typing import Optional # Permite indicar que un tipo de dato puede ser opcional
import asyncio # Librería para operaciones asíncronas
from pydantic import BaseModel, Field # Pydantic se usa para validación de datos
from fastapi.security import HTTPBasic, HTTPBasicCredentials # Módulos para seguridad HTTP Basic (aunque no se usan aquí)

# Creación de la instancia principal de la aplicación FastAPI
app = FastAPI()

# Lista de diccionarios que simula una base de datos en memoria para almacenar usuarios
usuarios=[
    {"id":1,"nombre":"Fany","edad":21},
    {"id":2,"nombre":"Ali","edad":21},
    {"id":3,"nombre":"Dulce","edad":21},
]

# Definición de un modelo Pydantic para validar los datos al crear un usuario
class crear_usuario(BaseModel):
    # Campo id: debe ser entero, mayor a 0 (gt=0)
    id: int = Field(..., gt=0, description="Identificador de usuario")
    # Campo nombre: string con longitud entre 1 y 50 caracteres
    nombre: str = Field(..., min_length=1, max_length=50, example="piloi")
    # Campo edad: entero entre 1 y 123 años (ge=1, le=123)
    edad: int = Field(..., ge=1,le=123, description="Edad del usuario entre 1 y 123 años")

# Ruta raíz de la API (por método GET)
@app.get("/")
async def holamundo(): 
    # Retorna un pequeño mensaje JSON de bienvenida
    return {"mensaje": "Hola mundo FastAPI"}

# Ruta adicional para saludar, simula una operación que toma tiempo
@app.get("/bienvenido")
async def bienvenido(): 
    # Espera 5 segundos de forma asíncrona sin bloquear la app
    await asyncio.sleep(5)
    # Retorna el mensaje de bienvenida
    return {"mensaje": "Bienvenido a FastAPI"}

# Ruta para obtener todos los usuarios de la "base de datos"
@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    # Retorna el total de usuarios y la lista completa
    return {"total": len(usuarios), "usuarios": usuarios}

# Ruta para registrar un nuevo usuario (método POST)
@app.post("/v1/usuarios/", tags=['HTTP CRUD'], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: crear_usuario):
    # Itera sobre la lista actual de usuarios
    for usr in usuarios:
        # Si el id del usuario ingresado ya existe, se lanza una excepción HTTP 400
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El id ya existe")
        # El bloque for aquí tiene una lógica particular, que añade a la primera iteración
        usuarios.append(usuario)
        return{
            "mensaje":"Usuario Creado",
            "Usuario": usuario
        }
        
    usuarios.append(usuario)
    return{
        "mensaje":"Usuario Creado",
        "Datos nuevos": usuario,
    }


# Ruta para actualizar TODOS los campos de un usuario por id (método PUT)
@app.put("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_usuario(id: int, usuario_actualizado: dict):
    # Itera sobre la lista buscando el índice y los datos del usuario
    for index, usr in enumerate(usuarios):
        # Si encuentra el id buscado
        if usr["id"] == id:
            # Reemplaza todo el diccionario en ese índice con los nuevos datos recibidos
            usuarios[index] = usuario_actualizado
            # Retorna el usuario actualizado
            return usuarios[index]
    # Si termina el ciclo y no encuentra el id, lanza error 404
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
 
# Ruta para actualizar ALGUNOS campos de un usuario por id (método PATCH)
@app.patch("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_parcial_usuario(id: int, usuario_actualizado: dict):
    # Itera sobre la lista buscando el usuario por id
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            # .update() añade o modifica en el diccionario solo las claves enviadas en la petición
            usr.update(usuario_actualizado)
            # Retorna el usuario con la modificación parcial
            return usr
    # Lanza error HTTP 404 si no encuentra el ID
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

# Ruta para eliminar un usuario por id (método DELETE)
@app.delete("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def eliminar_usuario(id: int):
    # Busca por índice y usuario
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            # Elimina el elemento de la lista en la posición 'index'
            usuarios.pop(index)
            # Retorna mensaje de éxito
            return {"mensaje": "Usuario eliminado exitosamente"}
    # Lanza excepción 404 si el id no fue encontrado
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
