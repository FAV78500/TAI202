from fastapi import FastAPI, status, HTTPException, Depends
from typing import Optional 
import asyncio
from pydantic import BaseModel, Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials   

app = FastAPI()
usuarios=[
    {"id":1,"nombre":"Fany","edad":21},
    {"id":2,"nombre":"Ali","edad":21},
    {"id":3,"nombre":"Dulce","edad":21},
]

class crear_usuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=1, max_length=50, example="piloi")
    edad: int = Field(..., ge=1,le=123, description="Edad del usuario entre 1 y 123 años")

@app.get("/")
async def holamundo(): 
    return {"mensaje": "Hola mundo FastAPI"}

@app.get("/bienvenido")
async def bienvenido(): 
    await asyncio.sleep(5)
    return {"mensaje": "Bienvenido a FastAPI"}

@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@app.post("/v1/usuarios/", tags=['HTTP CRUD'], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: crear_usuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El id ya existe")
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


@app.put("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_usuario(id: int, usuario_actualizado: dict):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuarios[index] = usuario_actualizado
            return usuarios[index]
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
 
@app.patch("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_parcial_usuario(id: int, usuario_actualizado: dict):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usr.update(usuario_actualizado)
            return usr
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def eliminar_usuario(id: int):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuarios.pop(index)
            return {"mensaje": "Usuario eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
