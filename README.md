# Lights Out: resolución mediante álgebra lineal

Repositorio del proyecto de Álgebra Aplicada 2026.

El objetivo del trabajo es implementar el juego Lights Out y resolver sus
tableros mediante un sistema de ecuaciones lineales con operaciones módulo 2.

## Objetivo del proyecto

El proyecto busca relacionar las reglas de Lights Out con conceptos de álgebra
lineal. Cada luz tiene dos estados: encendida (`1`) o apagada (`0`). Al presionar
una celda se invierte su estado y el de sus vecinas ortogonales: arriba, abajo,
izquierda y derecha, siempre que estén dentro del tablero.

La meta del juego es apagar todas las luces. Para encontrar las pulsaciones
necesarias, la implementación incluye:

- representación del tablero como una matriz binaria;
- construcción del vector de estado `b` y la matriz de coeficientes `A`;
- construcción de la matriz aumentada `[A | b]`;
- escalerización mediante sumas de filas módulo 2;
- resolución por sustitución hacia atrás;
- detección de tableros sin solución;
- generación de partidas resolubles;
- interfaz gráfica para jugar y visualizar una solución;
- demostración por consola del ejemplo 3×3 de la consigna.

## Fundamento algebraico

Para un tablero de tamaño `n × n`, se construye el sistema:

```text
A x = b (mod 2)
```

Los elementos del sistema son:

- `A`: matriz de tamaño `n² × n²`. Cada columna representa una pulsación y
  contiene un `1` en las filas de las luces que esa pulsación modifica.
- `b`: vector de tamaño `n²` con el estado inicial del tablero, recorrido por filas.
- `x`: vector de tamaño `n²` que indica qué celdas presionar. Un `1` significa
  presionar la celda y un `0`, dejarla sin presionar.

El estado final es `b + A x`. Como en módulo 2 se cumple `1 + 1 = 0`, resolver
`A x = b` permite obtener `b + A x = 0`, es decir, apagar todas las luces.
En el código, la suma binaria se implementa con el operador XOR (`^`).

La escalerización utiliza únicamente operaciones de la forma `Fi ← Fi + Fj`
módulo 2. Luego se aplica sustitución hacia atrás, asignando `0` a las variables
libres. Si aparece una fila con todos los coeficientes en `0` y término
independiente `1`, el sistema es incompatible y el solucionador devuelve `None`.

Cuando existen varias soluciones, se obtiene una solución válida; no se busca
necesariamente la que requiere menos pulsaciones.

## Estructura del proyecto

```text
algebra_lights_out/
|-- main.py
|-- solver.py
|-- juego.py
|-- partida.py
|-- interfaz.py
|-- demo_consigna.py
|-- .gitignore
|-- README.md
```

## Descripción de los scripts

### Solucionador algebraico

Archivo principal:

```text
solver.py
```

Este módulo:

- valida que el tablero sea una matriz cuadrada no vacía de enteros `0` y `1`;
- transforma el tablero en el vector `b`;
- construye la matriz de coeficientes `A` y la matriz aumentada `[A | b]`;
- escalona el sistema con suma binaria e identifica las columnas pivote;
- devuelve el vector de pulsaciones mediante `resolver_lights_out(tablero)`;
- devuelve `None` si el tablero no tiene solución.

### Reglas y generación de partidas

Archivo principal:

```text
juego.py
```

Este módulo:

- aplica una pulsación a una celda y sus vecinas ortogonales;
- comprueba si todas las luces están apagadas;
- crea copias independientes de los tableros;
- aplica un vector de pulsaciones sobre una copia del tablero;
- genera partidas resolubles a partir de pulsaciones aleatorias sobre un tablero
  inicialmente apagado.

Si la generación aleatoria deja todas las luces apagadas, se aplica una pulsación
adicional para que la partida comience con luces encendidas.

### Gestión de la partida

Archivo principal:

```text
partida.py
```
Este módulo:

  - encapsula el estado y la lógica de negocio de una partida activa (PartidaLightsOut)

  - administra el tablero actual, el tablero inicial, el contador de movimientos, el tamaño del tablero y los mensajes de estado

  - delega las reglas en juego.py y la resolución matemática en solver.py

  - gestiona las pistas de solución y las actualiza automáticamente tras cada jugada mediante operaciones en Z₂

### Interfaz gráfica

Archivo principal:

```text
interfaz.py
```

Punto de entrada:

```text
main.py
```

La interfaz utiliza Pygame y permite:

- jugar en un tablero inicial de 5×5;
- cambiar el tamaño entre 2×2 y 8×8;
- consultar el contador de movimientos;
- generar una partida nueva o reiniciar la actual;
- mostrar las celdas que deben presionarse para resolver el estado actual;
- mostrar una ventana emergente «¡Ganaste!» al apagar todas las luces, con
  opciones para iniciar otro juego o cerrar la aplicación.

Las luces encendidas se muestran en rojo y las apagadas en verde. Las celdas
indicadas por la solución tienen un borde y un punto amarillo.

### Demostración del ejemplo de la consigna

Archivo principal:

```text
demo_consigna.py
```

Este script trabaja con el siguiente tablero 3×3:

```text
0 1 0
1 1 0
0 0 1
```

Muestra por consola el tablero inicial, el vector `b`, la matriz `A`, la matriz
aumentada, la matriz escalonada, las columnas pivote, el vector solución y el
tablero final.

La solución del ejemplo es:

```text
x = [0, 0, 0, 0, 1, 0, 0, 0, 1]
```

Esto corresponde a presionar las celdas `a22` y `a33`, numerando filas y columnas
desde `1`. El script verifica que el vector coincide con el del ejemplo, que
`A x = b (mod 2)` y que el tablero final queda completamente apagado.

## Dependencias

Se requiere Python 3.10 o superior. Para ejecutar la interfaz gráfica se necesita
Pygame y una sesión gráfica. La demostración algebraica utiliza únicamente la
biblioteca estándar de Python.

La versión de Pygame comprobada en el entorno del proyecto es la 2.6.1.

Instalar la dependencia:

```bash
python -m pip install pygame==2.6.1
```

En Windows, si el comando `python` no apunta a la instalación de Python, puede
utilizarse el lanzador `py`:

```powershell
py -m pip install pygame==2.6.1
```

Opcionalmente, puede crearse un entorno virtual desde la raíz del repositorio:

```bash
python -m venv .venv
```

Activación en Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activación en Linux o macOS:

```bash
source .venv/bin/activate
```

Una vez activado el entorno, ejecutar el comando de instalación de Pygame.

## Cómo ejecutar el proyecto

Ejecutar los scripts desde la raíz del repositorio.

Para iniciar el juego:

```bash
python main.py
```

Para ejecutar la demostración algebraica:

```bash
python demo_consigna.py
```

En Windows también pueden utilizarse los comandos `py main.py` y
`py demo_consigna.py`. Si se utiliza el entorno virtual sin activarlo, ejecutar:

```powershell
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe demo_consigna.py
```

## Controles del juego

- **Clic izquierdo sobre una luz**: aplica una pulsación y suma un movimiento.
- **Nuevo juego**: genera otra partida del tamaño seleccionado.
- **Reiniciar**: restaura el tablero inicial y pone el contador de movimientos en cero.
- **Mostrar solución**: señala las celdas que deben presionarse para apagar el
  tablero actual. Las pistas se actualizan después de cada pulsación.
- **− / +**: disminuye o aumenta el tamaño del tablero e inicia una nueva partida.
- **Escape o cerrar la ventana**: termina la aplicación durante la partida.

Al ganar aparece una ventana emergente que bloquea el tablero y los controles.
No se puede descartar con Escape, el cierre de la ventana ni clics fuera del
cuadro: hay que elegir **Iniciar otro juego**, que genera otra partida del mismo
tamaño y reinicia el contador, o **Cerrar aplicación**, que termina el juego.

Las celdas señaladas pueden presionarse en cualquier orden, porque las
pulsaciones conmutan. Presionar una misma celda dos veces cancela su efecto.

## Reproducibilidad

La demostración utiliza un tablero fijo, por lo que siempre produce el mismo
sistema y la misma solución.

Para reproducir la generación de una partida desde Python, puede pasarse un
generador con semilla a `generar_tablero`:

```python
from random import Random
from juego import generar_tablero

tablero = generar_tablero(5, Random(77))
```

Al crear un generador nuevo con la misma semilla y usar el mismo tamaño, se
obtiene el mismo tablero dentro del mismo entorno de Python. La interfaz genera
partidas aleatorias sin fijar una semilla.

## Resultados esperados

Al ejecutar el proyecto se obtiene:

- una ventana interactiva de Lights Out al ejecutar `main.py`;
- una solución visual para el tablero actual al usar **Mostrar solución**;
- una ventana emergente «¡Ganaste!» cuando todas las luces quedan apagadas;
- el desarrollo algebraico del ejemplo 3×3 por consola al ejecutar
  `demo_consigna.py`;
- la confirmación de que la solución del ejemplo cumple el sistema y apaga el tablero.

Los resultados se muestran en la ventana o por consola; los scripts no generan
archivos de salida.
