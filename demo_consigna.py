"""Demostración por consola del sistema 3x3 de la consigna académica."""

from juego import aplicar_vector, esta_resuelto
from solver import (
    construir_matriz_aumentada,
    construir_matriz_coeficientes,
    escalerizar_binaria,
    resolver_lights_out,
    vectorizar_tablero,
)

TABLERO_CONSIGNA = [[0, 1, 0], [1, 1, 0], [0, 0, 1]]
SOLUCION_CONSIGNA = [0, 0, 0, 0, 1, 0, 0, 0, 1]


def mostrar_matriz(
    titulo: str, matriz: list[list[int]], aumentada: bool = False,
) -> None:
    """Imprime una matriz; puede separar el término independiente."""
    print(f"\n{titulo}")
    for fila in matriz:
        if aumentada:
            print("  " + " ".join(map(str, fila[:-1])) + f" | {fila[-1]}")
        else:
            print("  " + " ".join(map(str, fila)))


def main() -> None:
    """Muestra A, b, la escalerización y la solución verificada del ejemplo."""
    mostrar_matriz("Tablero inicial", TABLERO_CONSIGNA)
    b = vectorizar_tablero(TABLERO_CONSIGNA)
    print(f"\nVector b (recorrido por filas): {b}")
    A = construir_matriz_coeficientes(3)
    mostrar_matriz("Matriz A (filas: luces; columnas: pulsaciones)", A)
    aumentada = construir_matriz_aumentada(TABLERO_CONSIGNA)
    mostrar_matriz("Matriz aumentada [A | b]", aumentada, True)
    reducida, pivotes = escalerizar_binaria(aumentada)
    mostrar_matriz(
        "Matriz escalonada (solo sumas de filas módulo 2)", reducida, True,
    )
    print(f"\nColumnas pivote (índices desde 0): {pivotes}")
    x = resolver_lights_out(TABLERO_CONSIGNA)
    if x is None:
        raise RuntimeError("El ejemplo oficial debe ser compatible.")
    print(f"Vector solución x: {x}")
    print("Presionar: " + ", ".join(
        f"a{indice // 3 + 1}{indice % 3 + 1}"
        for indice, valor in enumerate(x) if valor
    ))
    producto = [sum(coef * valor for coef, valor in zip(fila, x)) % 2
                for fila in A]
    final = aplicar_vector(TABLERO_CONSIGNA, x)
    mostrar_matriz("Tablero final", final)
    if x != SOLUCION_CONSIGNA or producto != b or not esta_resuelto(final):
        raise RuntimeError("La verificación algebraica del ejemplo falló.")
    print("\nVerificación: A x = b (mod 2) y todas las luces apagadas.")


if __name__ == "__main__":
    main()
