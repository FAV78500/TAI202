import asyncio
from typing import option

from flask import app
from app.data.database import usuarios
from fastapi import APIRouter

misc=APIRouter(tags=["Miscelaneo"])

@misc.get("/")
async def holamundo(): 
    return {"mensaje": "Hola mundo FastAPI"}

@misc.get("/bienvenido")
async def bienvenido(): 
    await asyncio.sleep(5)
    return {"mensaje": "Bienvenido a FastAPI"}
