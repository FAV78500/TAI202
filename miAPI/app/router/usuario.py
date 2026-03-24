
from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from app.models.usuario import crear_usuario    
from app.data.database import usuarios
from app.security.auth import verificar_peticion

from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data import usuario as dbUsuario

router = APIRouter(
    prefix="/v1/usuarios", 
    tags=["HTTP CRUD"]
)

@router.get("/")
async def leer_usuarios(db: Session = Depends(get_db)):
    queryUsuarios= db.query(dbUsuario).all()
    return {"status":"200",
            "total": len(queryUsuarios),
              "usuarios": queryUsuarios
              }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuarioP:crear_usuario, db:Session= Depends(get_db)):
    nuevoU=dbUsuario(nombre= usuarioP.nombre, edad=usuarioP.edad)
    db.add(nuevoU)
    db.commit()
    db.refresh(nuevoU)
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