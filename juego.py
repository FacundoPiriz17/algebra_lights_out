"""Reglas, aplicación de pulsaciones y generación de partidas de Lights Out."""

from random import Random

from solver import validar_tablero, validar_tamano


def copiar_tablero(tablero: list[list[int]]) -> list[list[int]]:
    """Devuelve una copia independiente del tablero validado."""
    validar_tablero(tablero)
    return [fila[:] for fila in tablero]


def aplicar_pulsacion(
    tablero: list[list[int]], fila: int, columna: int,
) -> None:
    """Alterna una celda y sus vecinos ortogonales en el tablero."""
    n = validar_tablero(tablero)
    if (type(fila) is not int or type(columna) is not int
            or not 0 <= fila < n or not 0 <= columna < n):
        raise ValueError(
            "La pulsación debe indicar una celda dentro del tablero."
        )
    for df, dc in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        vecina_fila, vecina_columna = fila + df, columna + dc
        if 0 <= vecina_fila < n and 0 <= vecina_columna < n:
            # Sumar 1 módulo 2 invierte la luz; dos pulsaciones se cancelan.
            tablero[vecina_fila][vecina_columna] ^= 1


def esta_resuelto(tablero: list[list[int]]) -> bool:
    """Indica si todas las luces del tablero están apagadas."""
    validar_tablero(tablero)
    return not any(valor for fila in tablero for valor in fila)


def aplicar_vector(
    tablero: list[list[int]], pulsaciones: list[int],
) -> list[list[int]]:
    """Aplica un vector por filas sobre una copia, sin alterar el original."""
    n = validar_tablero(tablero)
    if (not isinstance(pulsaciones, list) or len(pulsaciones) != n * n
            or any(type(valor) is not int or valor not in (0, 1)
                   for valor in pulsaciones)):
        raise ValueError("El vector debe contener n² enteros 0 o 1.")
    resultado = copiar_tablero(tablero)
    for indice, valor in enumerate(pulsaciones):
        if valor == 1:
            aplicar_pulsacion(resultado, *divmod(indice, n))
    return resultado


def generar_tablero(
    n: int, generador: Random | None = None,
) -> list[list[int]]:
    """Genera un tablero resoluble no apagado; acepta un Random con semilla."""
    validar_tamano(n)
    azar = generador if generador is not None else Random()
    vacio = [[0] * n for _ in range(n)]
    pulsaciones = [azar.randrange(2) for _ in range(n * n)]
    tablero = aplicar_vector(vacio, pulsaciones)
    if esta_resuelto(tablero):
        # Evita iniciar con victoria, incluso si el vector pertenece al núcleo.
        aplicar_pulsacion(tablero, azar.randrange(n), azar.randrange(n))
    return tablero
