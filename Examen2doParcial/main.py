from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal, Optional
from datetime import datetime
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import asyncio   
import secrets

app = FastAPI()
security = HTTPBasic()

def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(security)):
    usuario_correcto = secrets.compare_digest(credenciales.username, "admin")
    contrasena_correcta = secrets.compare_digest(credenciales.password, "rest123")
    
    if not(usuario_correcto and contrasena_correcta):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no validas"
        )
    return credenciales.username

class User(BaseModel):
    nombre: str = Field(..., min_length=6)
#reserva de 8 am a 10 pm
class Reserva(BaseModel):
    id: int
    fecha_reserva: datetime

users_db: List[User] = []
reservas_db: List[Reserva] = []
user_id_counter = 1
reserva_id_counter = 1

#endpoint registrar reserva (con nombre de cliente no menor a 6 caracteres, solo de 8 am a 10 pm, minimo 1 persona maximo 10 personas, No reservas en domingo)
@app.post("/reservas", response_model=Reserva)
def registrar_reserva(reserva: Reserva):
    global reserva_id_counter
     if len(reserva.usuario.nombre) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre del cliente debe tener al menos 6 letras")
    if reserva.fecha_reserva.weekday() == 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se permiten reservas los domingos")
    if reserva.fecha_reserva.hour < 8 or reserva.fecha_reserva.hour >= 22:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Las reservas solo se permiten de 8 am a 10 pm")
    
    reserva.id = reserva_id_counter
    reservas_db.append(reserva)
    reserva_id_counter += 1
    return reserva


#endpoint listar reservas (endpoint protegido por HTTPBASIC)
@app.get("/reservas", response_model=List[Reserva])
async def listar_reservas(usuarioAuth: str = Depends(verificar_peticion)):
    return reservas_db     

#endpoint consultar reserva por id
@app.get("/reservas/{reserva_id}", response_model=Reserva)
def consultar_reserva(reserva_id: int):
    for reserva in reservas_db:
        if reserva.id == reserva_id:
            return reserva
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

#endpoint para confirmar reserva
@app.post("/reservas/{reserva_id}/confirmar")
def confirmar_reserva(reserva_id: int):
    for reserva in reservas_db:
        if reserva.id == reserva_id:
            # Aquí podrías agregar lógica adicional para confirmar la reserva
            return {"message": "Reserva confirmada"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

#endpoint para cancelar reserva (Endpoint protegido por HTTPBASIC)
@app.delete("/reservas/{reserva_id}")
def cancelar_reserva(reserva_id: int, usuarioAuth: str = Depends(verificar_peticion)):
    for reserva in reservas_db:
        if reserva.id == reserva_id:
            reservas_db.remove(reserva)
            return {"message": "Reserva cancelada"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    

