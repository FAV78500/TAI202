
from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from flask import app
from app.models.usuario import crear_usuario    
from app.data.database import usuarios
from app.security.auth import verificar_peticion

router = APIRouter(
    prefix="/v1/usuarios", 
    tags=["HTTP CRUD"]
)

@router.get("/")
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@router.post("/", status_code=status.HTTP_201_CREATED)
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

@router.put("/")
async def actualizar_usuario(id: int, usuario_actualizado: dict):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuarios[index] = usuario_actualizado
            return usuarios[index]
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.patch("/", status_code=status.HTTP_200_OK)
async def actualizar_parcial_usuario(id: int, usuario_actualizado: dict):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usr.update(usuario_actualizado)
            return usr
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, usuarioAuth: str = Depends(verificar_peticion)):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuarios.pop(index)
            return {"mensaje": f"Usuario eliminado por {usuarioAuth}"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")