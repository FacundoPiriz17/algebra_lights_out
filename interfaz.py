"""Ventana y eventos Pygame; delega reglas y resolución a sus módulos."""

import pygame

from juego import (
    aplicar_pulsacion, copiar_tablero, esta_resuelto, generar_tablero,
)
from solver import resolver_lights_out

ANCHO, ALTO = 780, 782
TAMANO_MINIMO, TAMANO_MAXIMO = 2, 8
TABLERO_RECT = pygame.Rect(150, 184, 480, 480)
FONDO = (17, 24, 39)
PANEL = (30, 41, 59)
TEXTO = (238, 242, 247)
SECUNDARIO = (163, 177, 196)
ENCENDIDA = (220, 65, 65)
APAGADA = (46, 160, 67)
ACENTO = (88, 217, 187)
PISTA = (250, 204, 74)


class InterfazLightsOut:
    """Gestiona una partida, sus controles y la visualización de pistas."""

    def __init__(self, pantalla: pygame.Surface, n: int = 5) -> None:
        """Prepara fuentes, botones y una partida resoluble."""
        if not TAMANO_MINIMO <= n <= TAMANO_MAXIMO:
            raise ValueError("El tamaño del tablero debe estar entre 2 y 8.")
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("segoeui", 21)
        self.pequena = pygame.font.SysFont("segoeui", 17)
        self.titulo = pygame.font.SysFont("segoeui", 38, bold=True)
        self.botones = {
            "menos": pygame.Rect(496, 99, 44, 40),
            "mas": pygame.Rect(668, 99, 44, 40),
            "nuevo": pygame.Rect(60, 689, 204, 48),
            "reiniciar": pygame.Rect(288, 689, 204, 48),
            "solucion": pygame.Rect(516, 689, 204, 48),
        }
        self.n = n
        self.tablero: list[list[int]] = []
        self.inicial: list[list[int]] = []
        self.movimientos = 0
        self.solucion: list[int] | None = None
        self.mensaje = ""
        self.nuevo_juego()

    def nuevo_juego(self) -> None:
        """Genera una partida del tamaño seleccionado y borra pistas."""
        self.inicial = generar_tablero(self.n)
        self.reiniciar()

    def reiniciar(self) -> None:
        """Recupera el tablero inicial y reinicia el contador de la partida."""
        self.tablero = copiar_tablero(self.inicial)
        self.movimientos = 0
        self.solucion = None
        self.mensaje = "Apagá todas las luces. Cada clic cambia una cruz."

    def mostrar_solucion(self) -> None:
        """Consulta el solucionador algebraico para el estado actual."""
        self.solucion = resolver_lights_out(self.tablero)
        self._actualizar_mensaje()

    def _actualizar_mensaje(self) -> None:
        """Comunica victoria, incompatibilidad o pulsaciones pendientes."""
        if esta_resuelto(self.tablero):
            self.mensaje = "¡Victoria! Todas las luces están apagadas."
        elif self.solucion is None:
            self.mensaje = "No existe solución para este tablero."
        else:
            pendientes = sum(self.solucion)
            self.mensaje = (
                f"Pulsaciones pendientes: {pendientes}. Seguí los puntos."
            )

    def rect_celda(self, fila: int, columna: int) -> pygame.Rect:
        """Calcula el área visible de una celda y el espacio entre luces."""
        paso = TABLERO_RECT.width / self.n
        izquierda = round(TABLERO_RECT.x + columna * paso)
        arriba = round(TABLERO_RECT.y + fila * paso)
        derecha = round(TABLERO_RECT.x + (columna + 1) * paso)
        abajo = round(TABLERO_RECT.y + (fila + 1) * paso)
        return pygame.Rect(izquierda + 4, arriba + 4,
                           derecha - izquierda - 8, abajo - arriba - 8)

    def gestionar_evento(self, evento: pygame.event.Event) -> bool:
        """Procesa eventos; devuelve si continúa la aplicación."""
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return False
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return True

        for nombre, rect in self.botones.items():
            if rect.collidepoint(evento.pos):
                if nombre == "nuevo":
                    self.nuevo_juego()
                elif nombre == "reiniciar":
                    self.reiniciar()
                elif nombre == "solucion":
                    self.mostrar_solucion()
                else:
                    cambio = -1 if nombre == "menos" else 1
                    nuevo_n = self.n + cambio
                    if TAMANO_MINIMO <= nuevo_n <= TAMANO_MAXIMO:
                        self.n = nuevo_n
                        self.nuevo_juego()
                return True

        if esta_resuelto(self.tablero):
            return True
        for fila in range(self.n):
            for columna in range(self.n):
                if self.rect_celda(fila, columna).collidepoint(evento.pos):
                    aplicar_pulsacion(self.tablero, fila, columna)
                    self.movimientos += 1
                    if self.solucion is not None:
                        # Un clic suma el vector unitario correspondiente a x.
                        # Las pistas siguen siendo válidas tras cada jugada.
                        self.solucion[fila * self.n + columna] ^= 1
                        self._actualizar_mensaje()
                    elif esta_resuelto(self.tablero):
                        self._actualizar_mensaje()
                    else:
                        self.mensaje = (
                            "Apagá todas las luces. Cada clic cambia una cruz."
                        )
                    return True
        return True

    def _texto(
        self, texto: str, posicion: tuple[int, int],
        fuente: pygame.font.Font | None = None,
        color: tuple[int, int, int] = TEXTO,
    ) -> None:
        """Dibuja texto con fuente y color opcionales."""
        imagen = (fuente or self.fuente).render(texto, True, color)
        self.pantalla.blit(imagen, posicion)

    def _dibujar_leyenda(self) -> None:
        """Centra la leyenda con una muestra de color junto a cada etiqueta."""
        elementos = (
            (ENCENDIDA, "Encendida"),
            (APAGADA, "Apagada"),
            (PISTA, "Pulsar"),
        )
        lado, separacion_texto, separacion_elementos = 16, 8, 28
        etiquetas = [
            self.pequena.render(texto, True, SECUNDARIO)
            for _, texto in elementos
        ]
        ancho_total = sum(
            lado + separacion_texto + etiqueta.get_width()
            for etiqueta in etiquetas
        ) + separacion_elementos * (len(elementos) - 1)
        izquierda = (self.pantalla.get_width() - ancho_total) // 2
        centro_y = self.pantalla.get_height() - 24
        for (color, _), etiqueta in zip(elementos, etiquetas):
            cuadrado = pygame.Rect(
                izquierda, centro_y - lado // 2, lado, lado,
            )
            pygame.draw.rect(self.pantalla, color, cuadrado, border_radius=3)
            texto_rect = etiqueta.get_rect(
                midleft=(cuadrado.right + separacion_texto, centro_y),
            )
            self.pantalla.blit(etiqueta, texto_rect)
            izquierda = texto_rect.right + separacion_elementos

    def dibujar(self) -> None:
        """Dibuja tablero, pistas, contador, mensajes y botones."""
        self.pantalla.fill(FONDO)
        self._texto("LIGHTS OUT", (60, 27), self.titulo)
        self._texto(
            "Álgebra aplicada", (61, 76),
            self.pequena, SECUNDARIO,
        )
        self._texto(f"Movimientos: {self.movimientos}", (60, 111))
        self._texto(f"{self.n} × {self.n}", (579, 105))
        self._texto("Tamaño", (563, 78), self.pequena, SECUNDARIO)

        pygame.draw.rect(self.pantalla, PANEL, TABLERO_RECT.inflate(16, 16),
                         border_radius=16)
        for fila in range(self.n):
            for columna in range(self.n):
                rect = self.rect_celda(fila, columna)
                color = ENCENDIDA if self.tablero[fila][columna] else APAGADA
                pygame.draw.rect(self.pantalla, color, rect, border_radius=10)
                indice = fila * self.n + columna
                if self.solucion is not None and self.solucion[indice]:
                    pygame.draw.rect(self.pantalla, PISTA, rect, width=3,
                                     border_radius=10)
                    pygame.draw.circle(self.pantalla, FONDO, rect.center, 8)
                    pygame.draw.circle(self.pantalla, PISTA, rect.center, 5)

        self._texto(self.mensaje, (60, 153), self.pequena,
                    ACENTO if esta_resuelto(self.tablero) else TEXTO)
        etiquetas = {
            "menos": "−", "mas": "+", "nuevo": "Nuevo juego",
            "reiniciar": "Reiniciar", "solucion": "Mostrar solución",
        }
        cursor = pygame.mouse.get_pos()
        for nombre, rect in self.botones.items():
            habilitado = not ((nombre == "menos" and self.n == TAMANO_MINIMO)
                             or (nombre == "mas" and self.n == TAMANO_MAXIMO))
            color = (
                (52, 71, 94)
                if rect.collidepoint(cursor) and habilitado else PANEL
            )
            pygame.draw.rect(self.pantalla, color, rect, border_radius=9)
            imagen = self.fuente.render(etiquetas[nombre], True,
                                       TEXTO if habilitado else SECUNDARIO)
            self.pantalla.blit(imagen, imagen.get_rect(center=rect.center))
        self._dibujar_leyenda()


def iniciar_interfaz() -> None:
    """Ejecuta la ventana Pygame hasta cerrarla o presionar Escape."""
    pygame.display.init()
    pygame.font.init()
    try:
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Lights Out")
        interfaz = InterfazLightsOut(pantalla)
        reloj = pygame.time.Clock()
        activa = True
        while activa:
            for evento in pygame.event.get():
                if not interfaz.gestionar_evento(evento):
                    activa = False
                    break
            interfaz.dibujar()
            pygame.display.flip()
            reloj.tick(60)
    finally:
        pygame.quit()
