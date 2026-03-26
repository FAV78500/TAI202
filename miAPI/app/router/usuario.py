
from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from app.models.usuario import crear_usuario    
from app.security.auth import verificar_peticion

from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.usuario import usuario as UsuarioDB

router = APIRouter(
    prefix="/v1/usuarios", 
    tags=["HTTP CRUD"]
)

# GET - Obtener todos los usuarios
@router.get("/")
async def leer_usuarios(db: Session = Depends(get_db)):
    queryUsuarios = db.query(UsuarioDB).all()
    return {"status": "200",
            "total": len(queryUsuarios),
            "usuarios": queryUsuarios
            }

# GET - Obtener usuario por ID
@router.get("/{id}")
async def obtener_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"status": "200", "usuario": usuario}

# POST - Crear nuevo usuario
@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario_endpoint(usuarioP: crear_usuario, db: Session = Depends(get_db)):
    nuevoU = UsuarioDB(nombre=usuarioP.nombre, edad=usuarioP.edad)
    db.add(nuevoU)
    db.commit()
    db.refresh(nuevoU)
    return {
        "mensaje": "Usuario Creado",
        "datos_nuevos": nuevoU,
    }

# PUT - Actualizar usuario completamente
@router.put("/{id}")
async def actualizar_usuario(id: int, usuario_actualizado: crear_usuario, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.nombre = usuario_actualizado.nombre
    usuario.edad = usuario_actualizado.edad
    db.commit()
    db.refresh(usuario)
    return {"mensaje": "Usuario actualizado", "usuario": usuario}

# PATCH - Actualizar usuario parcialmente
@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def actualizar_parcial_usuario(id: int, usuario_actualizado: dict, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if "nombre" in usuario_actualizado:
        usuario.nombre = usuario_actualizado["nombre"]
    if "edad" in usuario_actualizado:
        usuario.edad = usuario_actualizado["edad"]
    db.commit()
    db.refresh(usuario)
    return {"mensaje": "Usuario actualizado parcialmente", "usuario": usuario}

# DELETE - Eliminar usuario
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, db: Session = Depends(get_db), usuarioAuth: str = Depends(verificar_peticion)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": f"Usuario eliminado por {usuarioAuth}"}