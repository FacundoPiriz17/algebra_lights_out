"""Modelo lineal de Lights Out y escalerización propia con suma binaria."""


def validar_tablero(tablero: list[list[int]]) -> int:
    """Valida una matriz cuadrada binaria no vacía y devuelve su tamaño."""
    if not isinstance(tablero, list) or not tablero:
        raise ValueError("El tablero debe ser una lista no vacía de filas.")
    n = len(tablero)
    if any(not isinstance(fila, list) or len(fila) != n for fila in tablero):
        raise ValueError(
            "El tablero debe ser cuadrado, con filas de igual longitud."
        )
    if any(type(valor) is not int or valor not in (0, 1)
           for fila in tablero for valor in fila):
        raise ValueError("Todas las luces deben ser enteros 0 o 1.")
    return n


def validar_tamano(n: int) -> None:
    """Exige un tamaño entero positivo para construir un tablero o sistema."""
    if type(n) is not int or n < 1:
        raise ValueError("El tamaño debe ser un entero positivo.")


def vectorizar_tablero(tablero: list[list[int]]) -> list[int]:
    """Devuelve b en orden por filas: índice = fila * n + columna."""
    validar_tablero(tablero)
    return [valor for fila in tablero for valor in fila]


# -----------------------------------------------------------------------------
# Construcción del sistema binario
# -----------------------------------------------------------------------------


def construir_matriz_coeficientes(n: int) -> list[list[int]]:
    """Construye A: cada columna es una pulsación y cada fila una luz."""
    validar_tamano(n)
    A = [[0] * (n * n) for _ in range(n * n)]
    for fila in range(n):
        for columna in range(n):
            pulsacion = fila * n + columna
            for df, dc in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                vecina_fila, vecina_columna = fila + df, columna + dc
                if 0 <= vecina_fila < n and 0 <= vecina_columna < n:
                    luz = vecina_fila * n + vecina_columna
                    A[luz][pulsacion] = 1
    return A


def construir_matriz_aumentada(tablero: list[list[int]]) -> list[list[int]]:
    """Construye [A | b] para exigir b + A x = 0 módulo 2."""
    n = validar_tablero(tablero)
    A = construir_matriz_coeficientes(n)
    b = vectorizar_tablero(tablero)
    return [fila + [valor] for fila, valor in zip(A, b)]


# -----------------------------------------------------------------------------
# Escalerización y sustitución hacia atrás
# -----------------------------------------------------------------------------


def escalerizar_binaria(
    aumentada: list[list[int]],
) -> tuple[list[list[int]], list[int]]:
    """Copia y escalona [A | b] usando solo Fi <- Fi + Fj; indica pivotes."""
    if not isinstance(aumentada, list) or not aumentada:
        raise ValueError("La matriz aumentada no puede estar vacía.")
    if not isinstance(aumentada[0], list) or len(aumentada[0]) < 2:
        raise ValueError(
            "La matriz aumentada debe incluir coeficientes "
            "y término independiente."
        )
    ancho = len(aumentada[0])
    if any(not isinstance(fila, list) or len(fila) != ancho
           for fila in aumentada):
        raise ValueError(
            "Las filas de la matriz aumentada deben tener igual longitud."
        )
    if any(type(valor) is not int or valor not in (0, 1)
           for fila in aumentada for valor in fila):
        raise ValueError("La matriz aumentada solo admite enteros 0 y 1.")

    reducida = [fila[:] for fila in aumentada]
    pivotes: list[int] = []
    fila_pivote = 0
    for columna in range(ancho - 1):
        if fila_pivote == len(reducida):
            break
        if reducida[fila_pivote][columna] == 0:
            donante = next((i for i in range(fila_pivote + 1, len(reducida))
                            if reducida[i][columna] == 1), None)
            if donante is None:
                continue  # Columna sin pivote: su variable queda libre.
            # XOR es suma módulo 2. Creamos un 1 sin intercambiar filas.
            reducida[fila_pivote] = [
                a ^ b for a, b in zip(reducida[fila_pivote], reducida[donante])
            ]
        for i in range(fila_pivote + 1, len(reducida)):
            if reducida[i][columna] == 1:
                reducida[i] = [
                    a ^ b for a, b in zip(reducida[i], reducida[fila_pivote])
                ]
        # Todo pivote no nulo vale 1: no requiere normalización.
        pivotes.append(columna)
        fila_pivote += 1
    return reducida, pivotes


def resolver_lights_out(tablero: list[list[int]]) -> list[int] | None:
    """Devuelve pulsaciones por filas, o None si no existe solución."""
    aumentada = construir_matriz_aumentada(tablero)
    reducida, pivotes = escalerizar_binaria(aumentada)
    if any(not any(fila[:-1]) and fila[-1] == 1 for fila in reducida):
        return None

    # Las variables libres valen 0; no se minimiza el total de pulsaciones.
    x = [0] * (len(tablero) ** 2)
    for fila, columna in reversed(list(enumerate(pivotes))):
        valor = reducida[fila][-1]
        for j in range(columna + 1, len(x)):
            if reducida[fila][j] == 1:
                valor ^= x[j]
        x[columna] = valor
    return x
