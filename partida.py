"""Modelo de dominio y gestión de estado para una partida de Lights Out."""

from solver import resolver_lights_out
from juego import (
    aplicar_pulsacion,
    copiar_tablero,
    esta_resuelto,
    generar_tablero,
)

TAMANO_MINIMO, TAMANO_MAXIMO = 2, 8


class PartidaLightsOut:
    """Encapsula el estado y las restricciones de una partida activa."""

    def __init__(self, n: int = 5) -> None:
        if not TAMANO_MINIMO <= n <= TAMANO_MAXIMO:
            raise ValueError(f"El tamaño del tablero debe estar entre {TAMANO_MINIMO} y {TAMANO_MAXIMO}.")
        
        self._n = n
        self._tablero: list[list[int]] = []
        self._inicial: list[list[int]] = []
        self._movimientos = 0
        self._solucion: list[int] | None = None
        self._mensaje = ""
        self.nuevo_juego()

    @property
    def n(self) -> int:
        return self._n

    @property
    def tablero(self) -> list[list[int]]:
        return copiar_tablero(self._tablero)

    @property
    def movimientos(self) -> int:
        return self._movimientos

    @property
    def solucion(self) -> list[int] | None:
        return self._solucion.copy() if self._solucion is not None else None

    @property
    def mensaje(self) -> str:
        return self._mensaje

    def cambiar_tamano(self, nuevo_n: int) -> None:
        """Modifica el orden de la matriz del tablero si es válido."""
        if not TAMANO_MINIMO <= nuevo_n <= TAMANO_MAXIMO:
            raise ValueError(f"El tamaño debe estar entre {TAMANO_MINIMO} y {TAMANO_MAXIMO}.")
        self._n = nuevo_n
        self.nuevo_juego()

    def nuevo_juego(self) -> None:
        """Genera una nueva matriz inicial resoluble en Z_2."""
        self._inicial = generar_tablero(self._n)
        self.reiniciar()

    def reiniciar(self) -> None:
        """Restaura la partida al estado inicial sin perder la semilla o configuración."""
        self._tablero = copiar_tablero(self._inicial)
        self._movimientos = 0
        self._solucion = None
        self._actualizar_mensaje()

    def procesar_pulsacion(self, fila: int, columna: int) -> None:
        """Alterna la celda y sus vecinos, y actualiza las pistas si están activas."""
        if esta_resuelto(self._tablero):
            return

        aplicar_pulsacion(self._tablero, fila, columna)
        self._movimientos += 1

        if self._solucion is not None:
            # Un clic suma el vector unitario correspondiente a x.
            # Las pistas siguen siendo válidas tras cada jugada.
            indice = fila * self._n + columna
            self._solucion[indice] ^= 1

        self._actualizar_mensaje()

    def solicitar_solucion(self) -> None:
        """Delega en el solver la obtención del vector de pulsaciones óptimas."""
        resultado = resolver_lights_out(self._tablero)
        if resultado is None:
            self._solucion = None
            self._mensaje = "No existe solución para este tablero."
        else:
            self._solucion = resultado
            self._actualizar_mensaje()

    def _actualizar_mensaje(self) -> None:
        """Determina el estado de la partida y la retroalimentación al usuario."""
        if esta_resuelto(self._tablero):
            self._mensaje = "¡Victoria! Todas las luces están apagadas."
        elif self._solucion is None:
            self._mensaje = "Apagá todas las luces. Cada clic cambia una cruz."
        else:
            pendientes = sum(self._solucion)
            if pendientes == 0:
                self._mensaje = "¡El tablero ya está resuelto!"
            else:
                self._mensaje = f"Pulsaciones pendientes: {pendientes}. Seguí los puntos."