# Importación de FastAPI y gestores para manejar peticiones, rutas y estados HTTP
from fastapi import FastAPI, status, HTTPException, Depends
# Dependencias exclusivas para manejar la seguridad OAuth2 con contraseña (Bearer token)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# Permite denotar datos opcionales en definiciones de tipo
from typing import Optional 
# Módulo para ejecutar métodos asíncronos (await, sleep)
import asyncio
# Pydantic y Field nos permiten modelar esquemas con comprobación de tipos
from pydantic import BaseModel, Field
# Ayuda en la gestión de tiempos y cálculos requeridos para determinar la vigencia del token JWT
from datetime import datetime, timedelta, timezone
# Librería PyJWT para generar, codificar y decodificar tokens web JSON seguros
import jwt

# Declaración de variables clave para funcionamiento de JWT
SECRET_KEY = "my_super_secret_key" # Llave/secreto (debería ocultarse y ser seguro) para evitar firmas falsas
ALGORITHM = "HS256" # Algoritmo de hash para aplicar la llave (HMAC con SHA-256)
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Minutos que debe durar activamente un token para operar en el sistema

# Inicializa el esquema Oauth2 que buscará automáticamente un token en cabeceras de autorización de clientes apuntando a la ruta '/token'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Se crea la aplicación FastAPI
app = FastAPI()

# Base de datos simulada para almacenar perfiles de administración (quienes pueden obtener tokens)
usuarios_db = {
    "admin": {
        "username": "admin",
        "password": "password123" 
    }
}

# Base de datos simulada (memoria local) para pruebas API con entidades/registros de los usuarios guardados
usuarios=[
    {"id":1,"nombre":"Fany","edad":21},
    {"id":2,"nombre":"Ali","edad":21},
    {"id":3,"nombre":"Dulce","edad":21},
]

# Definición del esquema Pydantic para el payload (cuerpo JSON) al consumir la API e insertar un usuario
class crear_usuario(BaseModel):
    # Múltiples validaciones como longitud y tipos requeridos
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=1, max_length=50, example="piloi")
    edad: int = Field(..., ge=1,le=123, description="Edad del usuario entre 1 y 123 años")

# Función encargada de crear (firmar) un nuevo token JWT inyectando el tiempo de vigencia
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Se hace un diccionario paralelo clonando los datos emitidos por el sistema (ej. login)
    to_encode = data.copy()
    # Si ingresa una solicitud de tiempo específico por el sistema, se lo suma a la hora acutal (UTC)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    # En caso contrario ocupa el default global (30 mins de aquí general en local)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Se inserta en el payload a firmar la key 'exp' (reservada para timestamps de tiempo final en los JWTs oficiales)
    to_encode.update({"exp": expire})
    # Efectúa propiamente el proceso de firma a binario utilizando el string to_encode y las preconfiguraciones
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Devuelve el token en texto
    return encoded_jwt


# Función middleware para comprobar cada vez que una petición mande un header token a áreas exclusivas
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        # Se trata de desempaquetar y validar desde la libreria jwt proviendo la misma llave base. Si fue suplantada o no sirve falla aquí.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Buscamos el nombre de usuario previamente cargado por 'create_access_token' guardado en sub
        username: str = payload.get("sub")
        # Si de todos modos esto esta nulo y escapa se descarta
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        # El middleware de dependencias propaga en el resto de la subfunción este nombre string resultante
        return username
    except jwt.ExpiredSignatureError: # Disparado si 'exp' ya venció 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError: # Disparado en cualquier adulteración física extraña del código
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

# Esta es una operación POST clave donde los "administradores" pueden ingresar nombre y la clave a form_data para obtener su JWT. 
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Busca en usuarios_db locales según el nombre administrado 
    usuario = usuarios_db.get(form_data.username)
    # Si dictó mal un dato de usuario o erró en clave salta error 401 pidiendo que envíen sus datos form otra vez. 
    if not usuario or usuario["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Declara el factor tiempo configurado previamente
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Requerimos crear token y empaqueta en sub su nombre del dict de bd, guardado para futuros verify
    access_token = create_access_token(
        data={"sub": usuario["username"]}, expires_delta=access_token_expires
    )
    # Entrega al cliente el string serializado emito para el Header estándar y tipo Bearer (El default usado globalmente antes del espacio e inserción del JWT)
    return {"access_token": access_token, "token_type": "bearer"}


# Rutas sencillas GET públicas de respuesta
@app.get("/")
async def holamundo(): 
    return {"mensaje": "Hola mundo FastAPI"} # Devuelve solo un test JSON visible de la Web

@app.get("/bienvenido")
async def bienvenido(): 
    await asyncio.sleep(5) # Simula retraso asíncrono
    return {"mensaje": "Bienvenido a FastAPI"}

# --- A PARTIR DE AQUI SE EJECUTAN MÉTODOS CRUD, ALGUNOS ENCAPSULADOS CON SEGURIDAD TIPO DEPENDS ---

@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    # Retorna lista de elementos dentro del sistema local manipulado (no admins)
    return {"total": len(usuarios), "usuarios": usuarios}

@app.post("/v1/usuarios/", tags=['HTTP CRUD'], status_code=status.HTTP_201_CREATED)
async def crear_usuario_endpoint(usuario: crear_usuario): # Usa Pydantic (schema "crear_usuario")
    for usr in usuarios:
        # Se chequea evitar sobreescrituras en las IDs que ya circulan.
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El id ya existe")
    # Es convertido acá el model a un dictionary directamente por dict() a diferencia de otras versiones
    usuarios.append(usuario.dict())
    return{
        "mensaje":"Usuario Creado",
        "Datos nuevos": usuario,
    }

# Método restringido al inicio, solo pasa si trae un bearer validado por 'verify_token'. En caso exitoso la str username resultante es asignado a current_user
@app.put("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_usuario(id: int, usuario_actualizado: dict, current_user: str = Depends(verify_token)):
    for index, usr in enumerate(usuarios):
        # Utiliza get por ser mas seguro con diccionarios de variables imprecisas que acceder nativamente []
        if usr.get("id") == id:
            usuarios[index] = usuario_actualizado # Al encontrar id, reemplaza todo el indice iterado por el del usuario introducido
            return usuarios[index]
    raise HTTPException(status_code=404, detail="Usuario no encontrado") # De otra forma cae acá
 
@app.patch("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_parcial_usuario(id: int, usuario_actualizado: dict):
    # En este metodo (Update parcial) esta sin proteger globalmente
    for index, usr in enumerate(usuarios):
        if usr.get("id") == id:
            # Re-escribe un solo dato con update al modelo
            usr.update(usuario_actualizado)
            return usr
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

# Protegido por validación en Depends de verificación por token. Retorna 401 si no lo tiene.
@app.delete("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def eliminar_usuario(id: int, current_user: str = Depends(verify_token)):
    for index, usr in enumerate(usuarios):
        if usr.get("id") == id:
            usuarios.pop(index) # Expulsa un valor de la iteracion si ve su ID pedida
            return {"mensaje": "Usuario eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado") # Avisa que no sirve si la ID erró
