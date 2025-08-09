# Práctica 3: GPS

## Introducción

Este proyecto está organizado alrededor del módulo `gps.py`, que consiste en un sistema de navegación capaz de, dadas dos direcciones de la ciudad de Madrid, construir una ruta óptima en función de la preferencia del usuario (ruta más corta, más rápida o más rápida considerando semáforos).

El módulo `gps.py` utiliza dos librerías adicionales:  
- `grafo_pesado.py`, que implementa algoritmos de grafos como Dijkstra, Kruskal y Prim.  
- `callejero.py`, que contiene funciones para trabajar con el fichero de calles de Madrid y convertir la red de calles en un digrafo.

Se identificaron 441 componentes fuertemente conexas en el grafo dirigido de Madrid, siendo la componente más grande de 30,481 nodos. Esto garantiza accesibilidad entre nodos dentro de esa componente principal.

![Captura del sistema GPS](images/captura_gps.png)

---

## Librería Callejero (`callejero.py`)

Esta librería proporciona herramientas para modelar y analizar el callejero urbano de Madrid usando datos de OpenStreetMap, representado mediante grafos dirigidos.

### Funciones principales

- `carga_callejero`: carga el archivo `direcciones.csv` y procesa las coordenadas en formato decimal.
- `busca_direccion`: busca coordenadas específicas de una dirección en el DataFrame procesado.
- `convertir_a_decimal_regex`: convierte coordenadas geográficas en grados, minutos y segundos a formato decimal usando expresiones regulares.
- `procesar_latitud_y_longitud`: normaliza las coordenadas de latitud y longitud en el archivo `direcciones.csv`.
- `coordenadas_particulares`: localiza una dirección concreta en el DataFrame y devuelve sus coordenadas.
- `carga_grafo`: descarga o carga un grafo multidirigido de las calles de Madrid desde OpenStreetMap, almacenándolo localmente para futuras reutilizaciones.
- `procesa_grafo`: convierte el grafo multidirigido en un grafo dirigido sin bucles, optimizando su estructura para análisis.

---

## Librería Grafo Pesado (`grafo_pesado.py`)

Esta librería implementa algoritmos clásicos para trabajar con grafos pesados, útiles para rutas óptimas y árboles abarcadores mínimos.

### Algoritmos implementados

- **Dijkstra**: calcula el árbol de caminos mínimos desde un nodo origen a todos los demás.
- **Camino Mínimo**: calcula el camino más corto entre dos nodos usando el árbol de caminos mínimos generado por Dijkstra.
- **Prim**: construye un árbol abarcador mínimo conectando todos los nodos con el menor coste posible.
- **Kruskal**: construye un árbol abarcador mínimo ordenando y añadiendo aristas evitando ciclos, basado en la estructura de componentes conexas.

---

## Módulo Principal GPS (`gps.py`)

El módulo `gps.py` organiza la estructura principal del sistema GPS y utiliza las librerías anteriores para construir rutas optimizadas.

### Funciones destacadas

- `inicializar_datos()`: carga y procesa el callejero y el grafo de Madrid.
- `encontrar_nodo_mas_cercano()`: calcula el nodo más cercano a unas coordenadas usando distancia Manhattan.
- Funciones de coste para las rutas:
  - `mi_peso_distancia()`: retorna la longitud de la arista.
  - `mi_peso_tiempo()`: calcula el tiempo estimado para recorrer una arista basado en la velocidad máxima permitida.
  - `mi_peso_semaforos()`: añade a la función de tiempo un tiempo esperado por semáforos (24 segundos por cruce).
- `calcular_camino_segun_peso()`: calcula el camino óptimo usando la función de coste elegida.
- `calcula_giro()`: determina la dirección del giro (izquierda, derecha o recto) basado en tres nodos consecutivos.
- `crear_indicaciones()`: genera instrucciones paso a paso para la ruta, incluyendo distancias y giros, evitando redundancias.
- `dibujar()`: visualiza el grafo dirigido destacando la ruta calculada y señalando inicio y fin.

### Ejemplo de uso

Se puede obtener la ruta entre, por ejemplo, `Calle de Alberto Aguilera, 25` y `Calle de Leonardo Prieto Castro, 6`, obteniendo instrucciones detalladas y visualización de la ruta.

---

## Conclusión

Este proyecto integra el procesamiento de datos geográficos, modelado de grafos y algoritmos de caminos mínimos para construir un sistema GPS funcional y adaptable a distintos criterios de optimización (distancia, tiempo y tiempo con semáforos). La modularidad y reutilización de código facilitan la ampliación y mantenimiento del sistema.

---

## Requisitos

- Python 3.x
- Bibliotecas: `pandas`, `networkx`, `osmnx`, `heapq` (y otras según el entorno)

---

## Archivos

- `gps.py`: módulo principal del sistema GPS.
- `grafo_pesado.py`: implementación de algoritmos sobre grafos pesados.
- `callejero.py`: funciones para procesamiento y modelado del callejero de Madrid.

