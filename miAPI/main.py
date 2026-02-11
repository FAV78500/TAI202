#Importaciones
from fastapi import FastAPI
import asyncio

#Instancia del servidor
app= FastAPI() 

#Endpoints 
@app.get("/")
async def holamundo():
    return {"mensaje":"Hola Mundo desde FastAPI"}

@app.get("/bienvenido")
async def bienvenido():
    await asyncio.sleep(5)
    return{
        "mensaje":"Bienvenido a FastAPI",
        "estatus":"200",
    }

# Endpoint de parametros obligatorios
@app.get("/saludo/{nombre}")
async def saludo(nombre: str):
    return {"mensaje": f"Hola {nombre},bienvenido"}

# Endpoint de parametros opcionales
@app.get("/buscar/")
async def buscar(q: str = None):
    if q:
        return {"mensaje": f"resultados para: {q}"}
    return {"mensaje": "no hay termino de busqueda"}