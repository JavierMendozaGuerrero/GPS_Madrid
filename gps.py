from callejero import *
from grafo_pesado import *
import matplotlib.pyplot as plt 


#funcion para cargar datos (contiene prints útiles para saber que en efecto se han cargado bien los datos)
def inicializar_datos()->tuple: 
    print("Cargando datos")
    callejero = carga_callejero() #llama a funcion de callejero.py que permite cargar el df 
    grafo = procesa_grafo(carga_grafo()) #llama a las 2 funciines de callejero.py que permiten cargar los datos 
    print("Los datos cargados correctamente.")
    print("\n")

    return callejero, grafo



#hemos porgramado funcion alternativa a la funcion osmnx.distance.nearest_nodes(G, x, y) para entender como elegir el nodo mas cercano a partir de unas coordenadas 
def encontrar_nodo_mas_cercano(grafo: nx.Graph, lat_objetivo: float, lon_objetivo: float):
    INFTY = sys.float_info.max
    distancia_minima = INFTY  #inicilizamos la distancia mínima a infinito, que es el valor más grande posible para que acepte inicialmente cualquier valor menor en la primera comparación
    nodo_cercano = None 
    for nodo in grafo.nodes(): #Recorremos todos los nodos del grafo 
        lon_nodo = grafo.nodes[nodo]["x"] #obtenemos la longitud del nodo actual
        lat_nodo = grafo.nodes[nodo]["y"] #obtenemos la latitud del nodo actual 

        distancia = abs(lat_objetivo - lat_nodo) + abs(lon_objetivo - lon_nodo)  #la fórmula empleada es equivalente a la distancia Manhattan

        if distancia < distancia_minima:  
            nodo_cercano = nodo  
            distancia_minima = distancia  

    return nodo_cercano


#A continuación programamos las 3 funciones de peso que introducimos como argumento a la función camino mínimo de grafo pesado 

# 1: función según tiempo 
def mi_peso_distancia(G: nx.Graph, u: int, v: int) -> float:
    return G[u][v]["length"]


# 2: función según tiempo 
def mi_peso_tiempo(grafo: nx.DiGraph, nodo_inicio: int, nodo_fin: int) -> float:
    dic_propiedades_aritas = grafo[nodo_inicio][nodo_fin]
    if 'maxspeed' in dic_propiedades_aritas.keys(): #para cada arista (calle) entre 2 nodos 
        velocidad = dic_propiedades_aritas["maxspeed"]
        if isinstance(velocidad, list): # hemos visto que en el dataframe hay algunas velocidades que vienen en lista 

            #vamos a cambiar los valores de la lista a int para poder sacar la media de velocidades
            lista_int = []
            for valor in velocidad:
                valor = int(valor)
                lista_int.append(valor)
            vel_kmh = sum(lista_int)/(len(lista_int)) #la suma de las velocidades entre la longitud de la lista nos da la media
        else:
            #Además en el df hay algunas velocidades que tienen este formato: 30|50, si este es el caso, cogemos el primer número 
            if "|" in velocidad:
                vel_kmh=int(velocidad[:2])
            else:
                vel_kmh = int(velocidad)

    else:
        #si no hay maxspeed en los datso de la vía, usamos el el diccionario MAXSPEEDS
        via_tipo = grafo[nodo_inicio][nodo_fin]['highway']  

        if isinstance(via_tipo, list): #Además algunos de los tipos de vía también vienen en formato lista, si es así cogemos la primera
            via_tipo=via_tipo[0]

        vel_kmh = int(MAX_SPEEDS.get(via_tipo, 50))  #get permite que si no hay tipo de via tampoco en los datos, la velocidad por defecto son 50 kmh

    #Mutltiplicamos por factor de conversion para tener metros/segundos 
    vel_ms = vel_kmh * (1000 / 3600)

    longitud_a = grafo[nodo_inicio][nodo_fin]['length']  #Obtenemos la longitud de la arista en metros

    tiempo = longitud_a / vel_ms # t= d/v

    return tiempo

#3: función que tiene en cuenta probabilidad de quedarase parado con un semaforo
def mi_peso_semaforos(grafo: nx.DiGraph, nodo_inicio: int, nodo_fin: int) -> float:


    tiempo = mi_peso_tiempo(grafo, nodo_inicio, nodo_fin)

    #probabilidad de no detenerse de 1−p=0.2 con 0 segundos de espera,luego tesperado= 0.8×30 + 0.2×0 = 24segundos
    
    probabilidad_detencion = 0.8   
    tiempo_semaforo = probabilidad_detencion * 30   

    tiempo_total = tiempo + tiempo_semaforo
    return tiempo_total



#función que calcula camino según la opción de peso elegidas (devuleve lista con los nodos en el camino)
def calcular_camino_segun_peso(grafo:nx.DiGraph, nodo_origen:int, nodo_destino)->list:
    print("Seleccione el criterio para elegir su ruta en el GPS IMAT: ")
    print("1. Según distancia")
    print("2. Según tiempo")
    print("3. Según tiempo considerando semáforos")

    
    opcion = int(input("Ingrese una opción (1-3): "))
    print("\n")
    opciones_disponibles = [1,2,3]
    while opcion not in opciones_disponibles:
        opcion = int(input("Ingrese una opción (1-3): "))
    if opcion == 1:
        funcion_peso = mi_peso_distancia
        print("Has seleccionado: Distancia")
    elif opcion == 2:
        funcion_peso = mi_peso_tiempo
        print("Has seleccionado: Tiempo")
    elif opcion ==3:
        funcion_peso= mi_peso_semaforos
        print("Has seleccionado: Tiempo con semaforos")
    
    camino_mas_corto=camino_minimo(grafo,funcion_peso,nodo_origen,nodo_destino)

    return camino_mas_corto


def calcula_giro(nodo_prev:dict, nodo_curr:dict, nodo_next:dict)->str:

    #se extrae del dicc las coordenadas del nodo actual y el nodo anterior y siguiente 
    x_prev, y_prev = nodo_prev['x'], nodo_prev['y']
    x_curr, y_curr = nodo_curr['x'], nodo_curr['y']
    x_next, y_next = nodo_next['x'], nodo_next['y']

    #calculamos vectores con la diferencia de coordenadas
    vector_inicio = (x_curr - x_prev, y_curr - y_prev)
    vector_destino = (x_next - x_curr, y_next - y_curr)

    #productor vectorial
    producto_cruzado = vector_inicio[0] * vector_destino[1] - vector_inicio[1] * vector_destino[0]

    #segun el signo del porducto vectorial determinamos el sentido
    if producto_cruzado > 0:
        indicacion = "a la izquierda"
    elif producto_cruzado < 0:
        indicacion = "a la derecha"
    else:
        indicacion = "recto"
    return indicacion



 
def crear_indicaciones(G:nx.DiGraph, ruta:list)->list: 
    pasos = [] #lista donde van a estar todas las indicaciones 
    via_actual = None
    metros_restantes = 0

    for indice in range(len(ruta) - 1): #iteramos sobre la lista
        nodo_inicio = ruta[indice]
        nodo_intermedio = ruta[indice + 1]

        dic_info_carretera = G[nodo_inicio][nodo_intermedio] #diccionario de la arista

        #hemos visto que hay algunos nombres desconocidos en el df, luego si la clave "name" no esta en el diccaionario, calle sin nombre 
        if "name" in dic_info_carretera.keys():
            via_nombre = dic_info_carretera["name"]
        else:
            via_nombre = "desconocida"

        #hemos visto que algunos nombre de las vias vienen en formato de lista en el df, si es asi, guaradamos el primero de la lista
        if isinstance(via_nombre, list):
            via_nombre = via_nombre[0]

        #manejamos el caso en el que no ha atributo length
        if 'length' in dic_info_carretera:
            metros = dic_info_carretera['length']
        else:
            metros = 0

    
        if via_nombre == via_actual:
            metros_restantes += metros #actualiza lo que queda por recorrer de la calle 
        else:
            #Si cambia de vía, se genera instruccion de cuanto hay que recorrer
            if via_actual is not None:
                pasos.append(f"Siga por {via_actual} durante {metros_restantes:.0f} m.")

            
            via_actual = via_nombre #pasamos a la siguiente via
            metros_restantes = metros #obtenemos sus metro del diccionario sin contar los acumulados de la calle anterior

            
            if indice > 0 and indice < len(ruta) - 2: #se necesitan 3 nodos consecutivos, 
                #luego solo hasta penultimo
                nodo_fin = ruta[indice + 2]
                giro = calcula_giro(
                    G.nodes[nodo_inicio],
                    G.nodes[nodo_intermedio],
                    G.nodes[nodo_fin]
                )
                if giro:
                    pasos.append(f"Gire {giro} y continúe por {via_actual}.")


            if indice == 0: #considera cuadno acaba de empezar la ruta
                pasos.append(f"Empiece por {via_actual} y avance {metros_restantes:.0f} m.")
            else:
                pasos.append(f"Continúe por {via_actual} y avance {metros_restantes:.0f} m.")

    #si continuas en la misma via
    if via_actual is not None and metros_restantes > 0:
        pasos.append(f"Siga por {via_actual} durante {metros_restantes:.0f} m.")

    #última instrucciones que informa de que has llegado al final 
    pasos.append("Ha llegado al destino indicado.")
    return pasos

 





def dibujar(G: nx.DiGraph, camino: List[int]) -> None:
    #primero obtenemos las posiciones x e y de los nodos
    posicion_nodo = {nodo: (data['x'], data['y']) for nodo, data in G.nodes(data=True)}

    plt.figure(figsize=(8, 8))

    # usamos draw_networkx_edges para dibujar el grafo general 
    nx.draw_networkx_edges(
        G,
        pos=posicion_nodo,
        edge_color='lightgray',   # colo gris claro para que se pueda ver el camino
        width=0.5,                
        alpha=0.7,               # alpha permite hacerlas transaparentes
        arrows=False            # Sin flechas que no confuda el mapa
    )

    #resaltamos arista 
    path_edges = list(zip(camino[:-1], camino[1:]))  # Crear la lista de aristas del camino
    nx.draw_networkx_edges(
        G,
        pos=posicion_nodo,
        edgelist=path_edges,     
        edge_color='blue',      
        width=2.5,               
        arrows=False 
    )

    #resaltamos nodos
    nx.draw_networkx_nodes(
        G,
        pos=posicion_nodo,
        nodelist=[camino[0], camino[-1]], 
        node_color='red',            #color de nodos de inicio y final
        node_size=30,                      
        label="Origen y Destino"          
    )

    plt.legend()
    plt.axis("off")   #ocultamos los ejes para mejor vsibilidad 
    plt.show()



def main():
    while True:
        callejero,G=inicializar_datos()
        
        origen_direccion = input("Ingrese la dirección de origen (Calle, Número): ")

        if origen_direccion == "":
            print("Finalizando el programa.")
            break   

        destino_direccion = input("Ingrese la dirección de destino (Calle, Número):")
        print("\n")

        if destino_direccion == "":
            print("Finalizando el programa.")
            break   


        origen_lat, origen_lon = busca_direccion(origen_direccion, callejero)
        destino_lat, destino_lon = busca_direccion(destino_direccion, callejero)
    
        print(f"Las coordenadas del origen introducido son: {origen_lat, origen_lon}")
        print(f"Las coordenadas de destino introducido son: {destino_lat, destino_lon}")
        print("\n")


        
        nodo_origen=encontrar_nodo_mas_cercano(G,origen_lat,origen_lon)
        nodo_destino=encontrar_nodo_mas_cercano(G,destino_lat,destino_lon)

        ruta_optima=calcular_camino_segun_peso(G, nodo_origen,nodo_destino)
        indicaciones=crear_indicaciones(G, ruta_optima)
        for indicacion in indicaciones: 
            print(indicacion)
        dibujar(G,ruta_optima)

if __name__ == "__main__":
    main()





