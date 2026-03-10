from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import List, Literal, Optional
from datetime import datetime
import modelvalidator 

app = FastAPI()

class User(BaseModel):
    nombre: str = Field(..., min_length=6)

#reserva de 8 am a 10 pm
class Reserva(BaseModel):
    id: int
    usuario: User
    fecha_reserva: datetime


users_db: List[User] = []
reservas_db: List[Reserva] = []
user_id_counter = 1
reserva_id_counter = 1


#endpoint registrar reserva (con nombre de cliente, solo de 8 am a 10 pm)
@app.post("/reservas", status_code=status.HTTP_201_CREATED)
def creareserva(reserva: Reserva):
    global reserva_id_counter
    reserva.id = reserva_id_counter
    reserva_id_counter += 1
    reservas_db.append(reserva)

    return reserva

#endpoint listar reservas
@app.get("/reservas", response_model=List[Reserva])
def listar_reservas():
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

#endpoint para cancelar reserva
@app.delete("/reservas/{reserva_id}")
def borrar_reserva(reserva_id: int):
    for reserva in reservas_db:
        if reserva.id == reserva_id:
            reservas_db.remove(reserva)
            return {"message": "Reserva cancelada"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")


