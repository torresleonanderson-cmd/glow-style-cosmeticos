import pandas as pd
import os

# Ubicación de la carpeta datos dentro de backend
BASE_DIR = os.path.dirname(__file__)
CARPETA_DATOS = os.path.join(BASE_DIR, "datos")

if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

def obtener_ruta(nombre_archivo):
    return os.path.join(CARPETA_DATOS, nombre_archivo)

def cargar_datos(archivo, columnas):
    ruta = obtener_ruta(archivo)
    if os.path.exists(ruta) and os.stat(ruta).st_size > 0:
        return pd.read_csv(ruta)
    return pd.DataFrame(columns=columnas)

def guardar_datos(df, archivo):
    ruta = obtener_ruta(archivo)
    df.to_csv(ruta, index=False)