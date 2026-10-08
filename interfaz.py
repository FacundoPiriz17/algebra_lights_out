"""Ventana y eventos Pygame; delega reglas y resolución a sus módulos."""

import pygame

from juego import esta_resuelto
from partida import PartidaLightsOut, TAMANO_MINIMO, TAMANO_MAXIMO

ANCHO, ALTO = 780, 782
TABLERO_RECT = pygame.Rect(150, 184, 480, 480)
FONDO = (17, 24, 39)
PANEL = (30, 41, 59)
TEXTO = (238, 242, 247)
SECUNDARIO = (163, 177, 196)
ENCENDIDA = (220, 65, 65)
APAGADA = (46, 160, 67)
ACENTO = (88, 217, 187)
PISTA = (250, 204, 74)


class BotonUI:
    """Encapsular el renderizado y estado de un botón."""

    def __init__(self, rect: pygame.Rect, texto: str, clave: str) -> None:
        self.rect = rect
        self.texto = texto
        self.clave = clave

    def dibujar(
        self,
        pantalla: pygame.Surface,
        fuente: pygame.font.Font,
        cursor: tuple[int, int],
        habilitado: bool,
    ) -> None:
        color = (
            (52, 71, 94)
            if self.rect.collidepoint(cursor) and habilitado
            else PANEL
        )
        pygame.draw.rect(pantalla, color, self.rect, border_radius=9)
        color_texto = TEXTO if habilitado else SECUNDARIO
        imagen = fuente.render(self.texto, True, color_texto)
        pantalla.blit(imagen, imagen.get_rect(center=self.rect.center))


class InterfazLightsOut:
    """Capa de presentación gráfica orientada a eventos para el juego Lights Out."""

    def __init__(self, pantalla: pygame.Surface, n: int = 5) -> None:
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("segoeui", 21)
        self.pequena = pygame.font.SysFont("segoeui", 17)
        self.titulo = pygame.font.SysFont("segoeui", 38, bold=True)
        
        # Instanciación de la partida
        self.partida = PartidaLightsOut(n)
        
        # Componentes de botones de la interfaz
        self.botones = {
            "menos": BotonUI(pygame.Rect(496, 99, 44, 40), "−", "menos"),
            "mas": BotonUI(pygame.Rect(668, 99, 44, 40), "+", "mas"),
            "nuevo": BotonUI(pygame.Rect(60, 689, 204, 48), "Nuevo juego", "nuevo"),
            "reiniciar": BotonUI(pygame.Rect(288, 689, 204, 48), "Reiniciar", "reiniciar"),
            "solucion": BotonUI(pygame.Rect(516, 689, 204, 48), "Mostrar solución", "solucion"),
        }
        self.ventana_victoria = pygame.Rect(140, 261, 500, 260)
        self.botones_victoria = {
            "nuevo": pygame.Rect(190, 375, 400, 48),
            "cerrar": pygame.Rect(190, 439, 400, 48),
        }

    def rect_celda(self, fila: int, columna: int) -> pygame.Rect:
        """Calcula el área visible de una celda según el tamaño actual de la matriz."""
        n = self.partida.n
        paso = TABLERO_RECT.width / n
        izquierda = round(TABLERO_RECT.x + columna * paso)
        arriba = round(TABLERO_RECT.y + fila * paso)
        derecha = round(TABLERO_RECT.x + (columna + 1) * paso)
        abajo = round(TABLERO_RECT.y + (fila + 1) * paso)
        return pygame.Rect(
            izquierda + 4, arriba + 4,
            derecha - izquierda - 8, abajo - arriba - 8
        )

    def gestionar_evento(self, evento: pygame.event.Event) -> bool:
        """Procesa eventos; devuelve si continúa la aplicación."""
        if esta_resuelto(self.partida.tablero):
            # La victoria exige elegir una opción antes de continuar o salir.
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.botones_victoria["nuevo"].collidepoint(evento.pos):
                    self.partida.nuevo_juego()
                elif self.botones_victoria["cerrar"].collidepoint(evento.pos):
                    return False
            return True
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return False
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return True

        if self._manejar_click_botones(evento.pos):
            return True

        if not esta_resuelto(self.partida.tablero):
            self._manejar_click_tablero(evento.pos)

        return True

    def _manejar_click_botones(self, pos: tuple[int, int]) -> bool:
        """Delega las acciones de control de la sesión al modelo de dominio."""
        for nombre, boton in self.botones.items():
            if boton.rect.collidepoint(pos):
                if nombre == "nuevo":
                    self.partida.nuevo_juego()
                elif nombre == "reiniciar":
                    self.partida.reiniciar()
                elif nombre == "solucion":
                    self.partida.solicitar_solucion()
                elif nombre in ("menos", "mas"):
                    cambio = -1 if nombre == "menos" else 1
                    try:
                        self.partida.cambiar_tamano(self.partida.n + cambio)
                    except ValueError:
                        pass
                return True
        return False

    def _manejar_click_tablero(self, pos: tuple[int, int]) -> None:
        """Traduce el clic en una jugada sobre la celda."""
        n = self.partida.n
        for fila in range(n):
            for columna in range(n):
                if self.rect_celda(fila, columna).collidepoint(pos):
                    self.partida.procesar_pulsacion(fila, columna)
                    return

    def _texto(
        self,
        texto: str,
        posicion: tuple[int, int],
        fuente: pygame.font.Font | None = None,
        color: tuple[int, int, int] = TEXTO,
    ) -> None:
        """Dibuja texto plano en la ventana."""
        imagen = (fuente or self.fuente).render(texto, True, color)
        self.pantalla.blit(imagen, posicion)

    def _dibujar_cabecera(self) -> None:
        """Renderiza la información de la sesión y los selectores de dimensión."""
        self._texto("LIGHTS OUT", (60, 27), self.titulo)
        self._texto("Álgebra aplicada", (61, 76), self.pequena, SECUNDARIO)
        self._texto(f"Movimientos: {self.partida.movimientos}", (60, 111))
        self._texto(f"{self.partida.n} × {self.partida.n}", (579, 105))
        self._texto("Tamaño", (563, 78), self.pequena, SECUNDARIO)

    def _dibujar_tablero_y_pistas(self) -> None:
        """Renderiza el tablero, las luces y las pistas de la solución activa."""
        n = self.partida.n
        tablero = self.partida.tablero
        solucion = self.partida.solucion

        pygame.draw.rect(
            self.pantalla, PANEL, TABLERO_RECT.inflate(16, 16), border_radius=16
        )
        for fila in range(n):
            for columna in range(n):
                rect = self.rect_celda(fila, columna)
                color = ENCENDIDA if tablero[fila][columna] else APAGADA
                pygame.draw.rect(self.pantalla, color, rect, border_radius=10)
                
                indice = fila * n + columna
                if solucion is not None and solucion[indice]:
                    pygame.draw.rect(
                        self.pantalla, PISTA, rect, width=3, border_radius=10
                    )
                    pygame.draw.circle(self.pantalla, FONDO, rect.center, 8)
                    pygame.draw.circle(self.pantalla, PISTA, rect.center, 5)

        resuelto = esta_resuelto(tablero)
        self._texto(
            self.partida.mensaje,
            (60, 153),
            self.pequena,
            ACENTO if resuelto else TEXTO,
        )

    def _dibujar_botones_accion(self) -> None:
        """Renderiza los componentes de botones evaluando restricciones de tamaño."""
        cursor = pygame.mouse.get_pos()
        n = self.partida.n
        for nombre, boton in self.botones.items():
            habilitado = not (
                (nombre == "menos" and n == TAMANO_MINIMO)
                or (nombre == "mas" and n == TAMANO_MAXIMO)
            )
            boton.dibujar(self.pantalla, self.fuente, cursor, habilitado)

    def _dibujar_leyenda(self) -> None:
        """Renderiza la leyenda de colores inferior de forma centrada."""
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

    def _dibujar_victoria(self) -> None:
        """Muestra un cuadro modal con las dos opciones al ganar."""
        sombra = pygame.Surface(self.pantalla.get_size(), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 175))
        self.pantalla.blit(sombra, (0, 0))
        pygame.draw.rect(self.pantalla, PANEL, self.ventana_victoria,
                         border_radius=16)
        pygame.draw.rect(self.pantalla, ACENTO, self.ventana_victoria,
                         width=2, border_radius=16)
        titulo = self.titulo.render("¡Ganaste!", True, ACENTO)
        self.pantalla.blit(titulo, titulo.get_rect(center=(390, 302)))
        detalle = self.pequena.render(
            f"Apagaste todas las luces en {self.partida.movimientos} movimientos.",
            True, TEXTO,
        )
        self.pantalla.blit(detalle, detalle.get_rect(center=(390, 345)))
        etiquetas = {
            "nuevo": "Iniciar otro juego", "cerrar": "Cerrar aplicación",
        }
        cursor = pygame.mouse.get_pos()
        for nombre, rect in self.botones_victoria.items():
            color = (52, 71, 94) if rect.collidepoint(cursor) else FONDO
            pygame.draw.rect(self.pantalla, color, rect, border_radius=9)
            imagen = self.fuente.render(etiquetas[nombre], True, TEXTO)
            self.pantalla.blit(imagen, imagen.get_rect(center=rect.center))

    def dibujar(self) -> None:
        """Dibuja la partida y, al ganar, el cuadro modal de victoria."""
        self.pantalla.fill(FONDO)
        self._dibujar_cabecera()
        self._dibujar_tablero_y_pistas()
        self._dibujar_botones_accion()
        self._dibujar_leyenda()
        if esta_resuelto(self.partida.tablero):
            self._dibujar_victoria()


def iniciar_interfaz() -> None:
    """Ejecuta Pygame y exige elegir una opción del cuadro al ganar."""
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
