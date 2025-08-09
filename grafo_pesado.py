"""
grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP03B
Integrantes:
    - Lucia Tamarit Barberan
    - Javier Mendoza Guerrero

Descripción:
Librería para el análisis de grafos pesados.
"""

from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys

import heapq #Librería para la creación de colas de prioridad
from heapq import heappush, heappop

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""


def dijkstra(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]], origen:object)-> Dict[object,object]:
    """ Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".
    
    Args:
        origen (object): vértice del grafo de origen
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice alcanzable
            desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    Raises:
        TypeError: Si origen no es "hashable".
    Example:
        Si G.dijksra(1)={2:1, 3:2, 4:1} entonces 1 es padre de 2 y de 4 y 2 es padre de 3.
        En particular, un camino mínimo desde 1 hasta 3 sería 1->2->3.
    """

    if not isinstance(origen, (int, str, tuple)):
        raise TypeError("El origen  debe ser hashable ")
    
    padre = {v: None for v in G.nodes}  
    distancias = {v: INFTY for v in G.nodes}  # diccionario donde cdaa nodo v del grafo G tiene un valor que representa la distancia infinita
    distancias[origen] = 0  # la distancia desde el nodo de origen a sí mismo es cero.
    visitado = {v: False for v in G.nodes} 

    Q = [(0, 0, origen)] 

    indice=0
    while Q:
        _,_, nodo_actual = heapq.heappop(Q)
        #hemos hecho una lista, porque la funcion de python heappop actua sobre listas
        if visitado[nodo_actual]:
            continue   
        visitado[nodo_actual] = True  
       

        for x in G.neighbors(nodo_actual):#x es cada nodo adyacente o vecino al nodo actual
            
            if visitado[x]:
                continue  #pasamos a la siguiente iteracion del bucle
            
            peso_arista = peso(G, nodo_actual, x)
            distancia_nueva=distancias[nodo_actual] + peso_arista
            #vemos si el camino a ese vecino a través del nodo_actual es más corto que la distancia registrada en el diccionario distancias[vecino]
            if distancias[x] > distancia_nueva:
                distancias[x] = distancia_nueva
                #esto guarda el nodo padre de x en el diccionario padre, por lo tanto, estamos diciendo que para llegar a x de la forma mas corta hay que pasar por nodo actual
                padre[x] = nodo_actual
                indice+=1
                #  inserta una tupla (distancia,indice, nodo) en la cola de prioridad Q, distancias[x] es la distancia actualizada a x, y x es el nodo vecino que se inserta
                heapq.heappush(Q, (distancias[x], indice, x))
                
    
    return padre


def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->List[object]:
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
    
    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".

    """

    if not isinstance(origen, (int, str, tuple)) or not isinstance(destino, (int, str, tuple)):
        raise TypeError("El origen y el destino deben ser hashable ")


    padres = dijkstra(G, peso, origen)

    camino = []
    nodo = destino
    if nodo not in padres or padres[nodo] is None and nodo != origen:
        raise ValueError(f"No hay camino entre {origen} y {destino}.")

    while nodo is not None:
        camino.append(nodo)
        nodo = padres[nodo]
    camino.reverse()
    return camino





def prim(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> Dict[object,object]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo pesado
    usando el algoritmo de Prim.
    
    Args: None
    Returns:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises: None
    Example:
        Si prim(G,peso)={1: None, 2:1, 3:2, 4:1} entonces en un árbol abarcador mínimo tenemos que:
            1 es una raíz (no tiene padre)
            1 es padre de 2 y de 4
            2 es padre de 3
    """
    padre = {v: None for v in G.nodes} 
    coste_minimo = {v: float('inf') for v in G.nodes} 
    visitado = {v: False for v in G.nodes} 
    cola = []  

    inicio = next(iter(G.nodes))
    coste_minimo[inicio] = 0
    indice=0
    heappush(cola, (0, indice, inicio))  


    while cola:
        coste,_, v = heappop(cola)
        
        if visitado[v]:
            continue  
        visitado[v] = True  


        for x in G.neighbors(v):
            if visitado[x]:
                continue  

            peso_arista = peso(G, v, x)#esto es el peso de la arista
            if not visitado[x] and peso_arista < coste_minimo[x]:
                coste_minimo[x] = peso_arista
                padre[x] = v
                indice += 1
                heappush(cola, (peso_arista, indice, x))

    return padre

       

def kruskal(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> List[Tuple[object,object]]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo
    usando el algoritmo de Kruskal.
    
    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        List[Tuple[object,object]]: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
            de los pares de vértices del grafo que forman las aristas
            del arbol abarcador mínimo.
    Raises: None
    Example:
        En el ejemplo anterior en que prim(G,peso)={1:None, 2:1, 3:2, 4:1} podríamos tener, por ejemplo,
        kruskal(G,peso)=[(1,2),(1,4),(3,2)]
    """
    
    aristas = []  
    
    indice=0
    for edge in G.edges(): 
        u, v = edge  
        indice+=1
        peso_arista = peso(G, u, v)  
        aristas.append((peso_arista,indice,u,v)) 
        #Agrupamos los datos de las aritas en este orden para que ordene, primero en base al peso, y en caso de empate en base al orden
    aristas = sorted(aristas)

    componentes = {v: v for v in G.nodes}  # Representantes de las componentes (Cada nodo empieza en su propia componente porque inicialmente ningún nodo está conectado a ningún nodo)

    aristas_aam = []
  

    for _, _, u, v in aristas:
# busca los representantes de las componentes de u y v (las componentes a las que pertenecen)

        comp_u = u
        while componentes[comp_u] != comp_u:  # representante de u
            comp_u = componentes[comp_u]

        comp_v = v
        while componentes[comp_v] != comp_v:  #  representante de v
            comp_v = componentes[comp_v]


        # si los nodos están en diferentes componentes, unimos las componentes
        if comp_u != comp_v:
            aristas_aam.append((u, v))  # añadimos la arista al árbol

            for nodo in G.nodes:

# Para cada nodo, verificamos si su representante actual es comp_v.
# si es asi, actualizamos su representante a comp_u.

                if componentes[nodo] == comp_v:
                    componentes[nodo] = comp_u

    return aristas_aam






