# Importaciones necesarias de FastAPI para crear la app, manejar códigos de estado, excepciones y dependencias
from fastapi import FastAPI, status, HTTPException, Depends
# Importación para tener tipos opcionales
from typing import Optional 
# Librería para operaciones asíncronas
import asyncio
# Pydantic para la validación del esquema de datos
from pydantic import BaseModel, Field
# Módulos para implementar la seguridad de tipo Basic Auth
from fastapi.security import HTTPBasic, HTTPBasicCredentials   
# Librería 'secrets' para comparar cadenas de texto de forma segura
import secrets

# Inicialización de la aplicación FastAPI
app = FastAPI()

# Base de datos simulada de usuarios (una lista de diccionarios)
usuarios=[
    {"id":1,"nombre":"Fany","edad":21},
    {"id":2,"nombre":"Ali","edad":21},
    {"id":3,"nombre":"Dulce","edad":21},
]

# Esquema para validación de entrada cuando se crea un usuario
class crear_usuario(BaseModel):
    # Campo id: entero obligatorio, mayor que 0
    id: int = Field(..., gt=0, description="Identificador de usuario")
    # Campo nombre: texto obligatorio, longitud de 1 a 50
    nombre: str = Field(..., min_length=1, max_length=50, example="piloi")
    # Campo edad: entero obligatorio, en rango de 1 a 123 años
    edad: int = Field(..., ge=1,le=123, description="Edad del usuario entre 1 y 123 años")


# -------------- Seguridad HTTP BASIC --------------
# Crea una instancia para manejar la identificación por HTTP Basic (Header Authorization: Basic <base64>)
security = HTTPBasic()

# Función middleware/dependencia para autenticar el usuario antes de procesar la petición
def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(security)):
    # Compara el nombre de usuario (ej: 'Fernando') provisto en las credenciales asegurando integridad
    usuario_correcto = secrets.compare_digest(credenciales.username, "Fernando")
    # Compara la contraseña (ej: '2254412') asegurando un tiempo constante de comparación para evitar hackeos
    contrasena_correcta = secrets.compare_digest(credenciales.password, "2254412")
    
    # Si alguna de las dos comprobaciones resula ser falsa
    if not(usuario_correcto and contrasena_correcta):
        # Retorna el error 401: Unauthorized (no autorizado), informando al cliente
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no validas"
        )
    # Tras validar exitosamente la identidad, esta función devuelve el nombre de usuario
    return credenciales.username



# Endpoint raíz (home), responde al método GET
@app.get("/")
async def holamundo(): 
    # Muestra un mensaje simple en formato JSON
    return {"mensaje": "Hola mundo FastAPI"}

# Endpoint para saludar con retraso asíncrono
@app.get("/bienvenido")
async def bienvenido(): 
    # Detiene de forma asíncrona la ejecución durante 5 segundos
    await asyncio.sleep(5)
    # Realiza la respuesta una vez pasado el tiempo
    return {"mensaje": "Bienvenido a FastAPI"}

# ----- Operaciones de la API para gestión de usuarios (CRUD) -----

# GET para consultar los usuarios almacenados actualmente (Read)
@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    # Devuelve el arreglo completo y el tamaño de la lista
    return {"total": len(usuarios), "usuarios": usuarios}

# POST para registrar un nuevo usuario (Create), con código 201 en caso de éxito
@app.post("/v1/usuarios/", tags=['HTTP CRUD'], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: crear_usuario):
    # Se itera sobre todos los diccionarios de usuarios
    for usr in usuarios:
        # Se verifica que no exista previamente el ID a insertar
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El id ya existe")
        
        # En esta iteración de prueba se inserta y devuelve una respuesta de éxito de inmediato
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


# PUT para sobreescribir todos los datos de un usuario dado su Id (Update)
@app.put("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_usuario(id: int, usuario_actualizado: dict):
    # Itera tomando posición del índice y elemento de la lista
    for index, usr in enumerate(usuarios):
        # Valida que sea el objeto solicitado por su Id
        if usr["id"] == id:
            # Reemplaza todo el contenido existente en la misma posición de la lista
            usuarios[index] = usuario_actualizado
            return usuarios[index]
    # Arroja 404 No Encontrado si recorre todo y no encaja ningún Id
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
 
# PATCH para combinar/fusionar ciertos datos en un usuario dada si Id (Update parcial)
@app.patch("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_parcial_usuario(id: int, usuario_actualizado: dict):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            # Utiliza la función nativa update de dicts de python para pisar solo lo que haya llegado de parametro
            usr.update(usuario_actualizado)
            return usr
    # Si no localiza la id, retorna 404
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

# DELETE para quitar por completo a un usuario. Requiere que se pase el sistema de `Depends(verificar_peticion)` dictado anteriormente, lo que pide Basic Auth.
@app.delete("/v1/usuarios/{id}", tags=['HTTP CRUD'], status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, usuarioAuth: str = Depends(verificar_peticion)):
    # Recorrer buscando posición a quitar
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            # Elimina en el índice encontrado de la lista
            usuarios.pop(index)
            # Emite un informe confirmando la eliminación, e inyectando la variable `usuarioAuth` (que sería "Fernando" si salió bien la auth)
            return {"mensaje": f"Usuario eliminado por {usuarioAuth}"}
    # En caso de no existir, se emite excepción
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
