"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP03B
Integrantes:
    - Lucia Tamarit Barberan
    - Javier Mendoza Guerrero

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import os
from typing import Tuple
import re 

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100'}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AdressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass



def convertir_a_decimal_regex(coordenada:str)->int:
    
    patron = r"(\d+)[^\d]*(\d+)[^\d]*(\d+(\.\d+)?)[^\d]*([NSWE])"
    #regex + es 1 o mas digitos , * es 0 o mas digitos 
    #[^\d] coincide con cualquier carácter que no sea un dígito para que coja los caracteres raros �, es decir º 
    #corchete para clase de caracteres []
    #(\d+(\.\d+)?) para que coincida con numero que sea decimal o no sea decimal
    #clase = [NSEW]

    match = re.match(patron, coordenada)
    
    if not match:
        raise ValueError(f"Formato de coordenada inválido: {coordenada}")
    
    grados = int(match.group(1))
    minutos = int(match.group(2))
    segundos = float(match.group(3))
    orientacion = match.group(5)

    decimal = grados + minutos / 60 + segundos / 3600
    #1 grado se divide en 60 minutos, luego cada minuto es 1/60 dw un grado, esto implica cada segundo es 1/3600 de un grado
    
    
    if orientacion in ['S', 'W']: #según se nos especifica en  del enunciado 
        decimal *= -1
    
    return decimal

def procesar_latitud_y_longitud(archivo_csv):
    df = pd.read_csv("direcciones.csv", encoding='ISO-8859-1', delimiter=';')
    df_direcciones = df[["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NUMERO", "LATITUD", "LONGITUD"]]
    
    df_direcciones.loc[:, 'LATITUD'] = df_direcciones['LATITUD'].apply(convertir_a_decimal_regex)
    df_direcciones.loc[:, 'LONGITUD'] = df_direcciones['LONGITUD'].apply(convertir_a_decimal_regex)

    return df_direcciones




def coordenadas_particulares(direccion, df):
    particulas = ["de los", "de las", "de la", "del", "de", "de ", " a la ", "al"]
    #con un drop_duplicates hemos podido ver todas las particulas distintas que había para añadíselas a la lista partículas 
    #además con este drop_duplicates hemos podido comprobar que VIA_CLASE nunca es más largo que una palabra 
    """
    df = pd.read_csv("direcciones.csv", encoding='ISO-8859-1', delimiter=';')
    filas_unicas = df.drop_duplicates(subset='VIA_PAR')
    print(filas_unicas)
    
    """
    try:
        nombre_via , numero = direccion.split(',')
        nombre_via = nombre_via.strip()  
        numero = int(numero.strip())
    except (ValueError, IndexError):
        raise ValueError("Formato de dirección inválido. Debe ser 'VIA_CLASE VIA_PAR VIA_NOMBRE, NUMERO'")
    
    nombre_via_palabras = nombre_via.split()
    
    # Asumir que la primera palabra es el VIA_CLASE (Calle o Paseo)
    via_clase = nombre_via_palabras[0]  
    
    
    
    # Encontrar la coincidencia más larga para VIA_PAR en la lista de partículas
    via_par = ""
    via_nombre = ""
    for i in range(1, len(nombre_via_palabras)):
        posible_via_par = ' '.join(nombre_via_palabras[1:i + 1]).lower()
        
        if posible_via_par in particulas:
            via_par = posible_via_par
            via_nombre = ' '.join(nombre_via_palabras[i + 1:]).upper()  # Nombre en mayúsculas
            
    via_clase = via_clase.upper()
    via_par = via_par.upper()
    via_nombre = via_nombre.upper()

    if not via_par:
        via_nombre = ' '.join(nombre_via_palabras[1:]).upper()
    
    #FILTRADO
    resultado = df[(df['VIA_CLASE'] == via_clase) & 
                   (df['VIA_PAR'] == via_par) & 
                   (df['VIA_NOMBRE'] == via_nombre) & 
                   (df['NUMERO'] == numero)]
    
    if not resultado.empty:
        return resultado.iloc[0]['LATITUD'], resultado.iloc[0]['LONGITUD']
    else:
        raise ValueError("Dirección no encontrada en el dataset.")



def carga_callejero() -> pd.DataFrame:
    try:
        df = procesar_latitud_y_longitud("direcciones.csv")  
        return df
    except FileNotFoundError:
        raise FileNotFoundError("El archivo 'direcciones.csv' no fue encontrado.")  




def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:

    try:
        #busca las coordenadas de la dirección en el df llamando a la funcion del apartado2 
        coordenadas = coordenadas_particulares(direccion, callejero)
        return coordenadas
    except ValueError:
        # Manejar el caso donde las coordenadas no se encuentren
        raise AdressNotFoundError(f"La dirección '{direccion}' no fue encontrada en la base de datos.") 



def carga_grafo() -> nx.MultiDiGraph:
    network_type="drive"
    #path="madrid.graphml"
    try:
        if os.path.exists(MAP_FILE_NAME):# Si existe,debera leer la informacion del grafo del fichero.
            G=ox.load_graphml(MAP_FILE_NAME)#carga un grafo desde un archivo en formato GraphML
        else:#si no existe,  debera descargar la informacion, crear el grafo y guardarlo
            G=ox.graph_from_place(PLACE_NAME,network_type)
            ox.save_graphml(G,MAP_FILE_NAME)
        #     Descarga los datos de OpenStreetMap usando ox.graph_from_place con los parámetros query y network_type.
        #     Guarda el grafo descargado en el archivo madrid.graphml usando ox.save_graphml, para que pueda reutilizarse en el futuro sin necesidad de descargarlo nuevamente.
        return G
    except Exception:
        raise ServiceNotAvailableError("No se pudo recuperar el grafo de OpenStreetMap.")  





def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    G=multidigrafo
    G_digrafo=ox.convert.to_digraph(G, weight='length')
    bucles=list(nx.selfloop_edges(G_digrafo))
    #selfloop_edges Devuelve una lista de aristas que son bucles. Si data=False, las aristas se devuelven como tuplas de nodos (u, u). Si data=True, las aristas se devuelven como tuplas (u, u, data).
    G_digrafo.remove_edges_from(bucles)
    #usamos la funcion remove_edges_from de la libreria nx
    return G_digrafo


