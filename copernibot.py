# -*- coding: utf-8 -*-
import os
import pygame
import sys

PANTALLA_ANCHO = 1180
PANTALLA_ALTO = 720
COLUMNAS = 12
FILAS = 8
TAMANO_CELDA = 64
GRILLA_OFFSET_X = 20
GRILLA_OFFSET_Y = 60
HUD_X = GRILLA_OFFSET_X + COLUMNAS * TAMANO_CELDA + 20
FPS = 60

COLOR_FONDO       = (28, 32, 42)
COLOR_CELDA       = (64, 72, 92)
COLOR_CELDA_BORDE = (40, 46, 60)
COLOR_SENDERO     = (240, 215, 90)
COLOR_MERENDERO   = (230, 130, 70)
COLOR_TEXTO       = (235, 235, 235)
COLOR_TEXTO_TENUE = (160, 165, 180)
COLOR_OK          = (90, 220, 130)
COLOR_HUD_BG      = (38, 44, 58)
COLOR_OBSTACULO   = (110, 70, 40)
COLOR_ITEM        = (240, 215, 90)

COOLDOWN_MS = 140

# --- Bloque 2: posiciones fijas de obstáculos e ítems recolectables ---
# Fijas (no aleatorias) para que el nivel sea reproducible y fácil de depurar.
OBSTACULOS_BASE = [(3, 4), (3, 5), (5, 7), (2, 9)]
ITEMS_BASE = [(1, 2), (4, 2), (6, 5), (3, 10)]


def en_grilla(fila, columna):
    return 0 <= fila < FILAS and 0 <= columna < COLUMNAS


def celda_a_pixel(fila, columna):
    pixel_x = GRILLA_OFFSET_X + columna * TAMANO_CELDA
    pixel_y = GRILLA_OFFSET_Y + fila * TAMANO_CELDA
    return pixel_x, pixel_y


def mover_copernibot(estado, delta_fila, delta_columna):
    """Intenta mover a COPERNIBOT. Devuelve True si el movimiento se concretó
    (para poder disparar el sonido solo cuando realmente hubo desplazamiento)."""
    if estado["completado"]:
        return False

    fila_actual, columna_actual = estado["cursor"]
    nueva_fila = fila_actual + delta_fila
    nueva_columna = columna_actual + delta_columna
    nueva_pos = (nueva_fila, nueva_columna)

    if not en_grilla(nueva_fila, nueva_columna):
        return False  # fuera de la grilla

    if nueva_pos in estado["obstaculos"]:
        return False  # pared infranqueable

    if nueva_pos in estado["sendero"]:
        return False  # no se puede volver a pisar el propio camino

    estado["sendero"].append(nueva_pos)
    estado["cursor"] = nueva_pos
    estado["pasos"] += 1

    if nueva_pos in estado["items_restantes"]:
        estado["items_restantes"].remove(nueva_pos)
        estado["items_recolectados"] += 1

    if nueva_pos == estado["merendero"]:
        estado["completado"] = True
        estado["tiempo_completado"] = pygame.time.get_ticks()

    return True


def dibujar_grilla(pantalla, estado, fuente_chica, imagen_copernibot, imagen_merendero):
    celdas_sendero = set(estado["sendero"])

    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            pixel_x, pixel_y = celda_a_pixel(fila, columna)
            rect_celda = pygame.Rect(pixel_x, pixel_y, TAMANO_CELDA, TAMANO_CELDA)
            color_celda = COLOR_CELDA
            if (fila, columna) in celdas_sendero:
                color_celda = COLOR_SENDERO
            pygame.draw.rect(pantalla, color_celda, rect_celda)
            pygame.draw.rect(pantalla, COLOR_CELDA_BORDE, rect_celda, 1)

    # Obstáculos: paredes marrones infranqueables
    for fila_obs, columna_obs in estado["obstaculos"]:
        pixel_x, pixel_y = celda_a_pixel(fila_obs, columna_obs)
        rect_obstaculo = pygame.Rect(pixel_x + 3, pixel_y + 3, TAMANO_CELDA - 6, TAMANO_CELDA - 6)
        pygame.draw.rect(pantalla, COLOR_OBSTACULO, rect_obstaculo, border_radius=4)
        pygame.draw.rect(pantalla, COLOR_CELDA_BORDE, rect_obstaculo, 2, border_radius=4)

    # Ítems recolectables (donaciones) pendientes
    for fila_item, columna_item in estado["items_restantes"]:
        pixel_x, pixel_y = celda_a_pixel(fila_item, columna_item)
        centro = (pixel_x + TAMANO_CELDA // 2, pixel_y + TAMANO_CELDA // 2)
        pygame.draw.circle(pantalla, COLOR_ITEM, centro, TAMANO_CELDA // 6)
        pygame.draw.circle(pantalla, COLOR_CELDA_BORDE, centro, TAMANO_CELDA // 6, 2)

    # Casilla del merendero (imagen)
    fila_merendero, columna_merendero = estado["merendero"]
    pixel_merendero_x, pixel_merendero_y = celda_a_pixel(fila_merendero, columna_merendero)
    pantalla.blit(imagen_merendero, (pixel_merendero_x + 2, pixel_merendero_y + 2))
    texto_merendero = fuente_chica.render("MERENDERO", True, COLOR_TEXTO)
    pantalla.blit(texto_merendero,
                  (pixel_merendero_x + TAMANO_CELDA // 2 - texto_merendero.get_width() // 2,
                   pixel_merendero_y + TAMANO_CELDA - 16))

    mitad = TAMANO_CELDA // 2
    sendero = estado["sendero"]
    for indice in range(1, len(sendero)):
        origen_x, origen_y = celda_a_pixel(*sendero[indice - 1])
        destino_x, destino_y = celda_a_pixel(*sendero[indice])
        pygame.draw.line(pantalla, (255, 255, 255),
                         (origen_x + mitad, origen_y + mitad),
                         (destino_x + mitad, destino_y + mitad), 4)

    fila_cursor, columna_cursor = estado["cursor"]
    pixel_cursor_x, pixel_cursor_y = celda_a_pixel(fila_cursor, columna_cursor)
    pantalla.blit(imagen_copernibot, (pixel_cursor_x + 2, pixel_cursor_y + 2))


def dibujar_hud(pantalla, estado, fuente_mediana, fuente_chica):
    panel = pygame.Rect(HUD_X - 10, GRILLA_OFFSET_Y - 10,
                        PANTALLA_ANCHO - HUD_X, FILAS * TAMANO_CELDA + 20)
    pygame.draw.rect(pantalla, COLOR_HUD_BG, panel, border_radius=8)

    posicion_y = GRILLA_OFFSET_Y

    titulo_mision = fuente_mediana.render("Misión", True, COLOR_OK)
    pantalla.blit(titulo_mision, (HUD_X, posicion_y))
    posicion_y += titulo_mision.get_height() + 6

    lineas_mision = [
        "Acompaña a COPERNIBOT a dejar",
        "las donaciones en el merendero.",
    ]
    for linea in lineas_mision:
        texto_mision = fuente_chica.render(linea, True, COLOR_TEXTO)
        pantalla.blit(texto_mision, (HUD_X, posicion_y))
        posicion_y += texto_mision.get_height() + 2

    posicion_y += 14

    # --- Contador de pasos en tiempo real ---
    texto_pasos = fuente_mediana.render(f"Pasos: {estado['pasos']}", True, COLOR_TEXTO)
    pantalla.blit(texto_pasos, (HUD_X, posicion_y))
    posicion_y += texto_pasos.get_height() + 6

    # --- Contador de donaciones recolectadas (funcionalidad extra) ---
    total_items = estado["items_totales"]
    texto_items = fuente_mediana.render(
        f"Donaciones: {estado['items_recolectados']}/{total_items}", True, COLOR_ITEM)
    pantalla.blit(texto_items, (HUD_X, posicion_y))
    posicion_y += texto_items.get_height() + 18

    titulo_controles = fuente_mediana.render("Controles", True, COLOR_TEXTO)
    pantalla.blit(titulo_controles, (HUD_X, posicion_y))
    posicion_y += titulo_controles.get_height() + 10

    instrucciones = [
        "Flechas: Movimiento COPERNIBOT",
        "R      : Reiniciar nivel",
        "ESC    : Salir",
    ]
    for linea in instrucciones:
        texto_linea = fuente_chica.render(linea, True, COLOR_TEXTO_TENUE)
        pantalla.blit(texto_linea, (HUD_X, posicion_y))
        posicion_y += texto_linea.get_height() + 4


def dibujar_cartel_completado(pantalla, fuente_grande, fuente_mediana, tiempo_transcurrido_ms):
    """Cartel de victoria con una pequeña animación de entrada (fade-in +
    título con efecto de 'pulso') basada en el tiempo transcurrido desde
    que se completó el nivel."""
    import math

    # Fade-in del overlay durante los primeros 400ms
    alpha_overlay = min(180, int(180 * (tiempo_transcurrido_ms / 400)))
    overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha_overlay))
    pantalla.blit(overlay, (0, 0))

    cartel_ancho = 520
    cartel_alto = 180
    cartel_x = PANTALLA_ANCHO // 2 - cartel_ancho // 2
    cartel_y = PANTALLA_ALTO // 2 - cartel_alto // 2
    pygame.draw.rect(pantalla, COLOR_HUD_BG,
                     (cartel_x, cartel_y, cartel_ancho, cartel_alto),
                     border_radius=12)
    pygame.draw.rect(pantalla, COLOR_OK,
                     (cartel_x, cartel_y, cartel_ancho, cartel_alto),
                     4, border_radius=12)

    # Título con efecto de "pulso" (escala oscilante con el tiempo)
    escala = 1.0 + 0.06 * math.sin(tiempo_transcurrido_ms / 150)
    texto_titulo_base = fuente_grande.render("NIVEL COMPLETADO", True, COLOR_OK)
    ancho_escalado = int(texto_titulo_base.get_width() * escala)
    alto_escalado = int(texto_titulo_base.get_height() * escala)
    texto_titulo = pygame.transform.smoothscale(texto_titulo_base, (ancho_escalado, alto_escalado))
    pantalla.blit(texto_titulo,
                  (PANTALLA_ANCHO // 2 - texto_titulo.get_width() // 2,
                   cartel_y + 50))

    texto_subtitulo = fuente_mediana.render("Llegaste al merendero", True, COLOR_TEXTO)
    pantalla.blit(texto_subtitulo,
                  (PANTALLA_ANCHO // 2 - texto_subtitulo.get_width() // 2,
                   cartel_y + 110))

    texto_reinicio = fuente_mediana.render("Presioná R para jugar de nuevo", True, COLOR_TEXTO_TENUE)
    pantalla.blit(texto_reinicio,
                  (PANTALLA_ANCHO // 2 - texto_reinicio.get_width() // 2,
                   cartel_y + 145))


def crear_estado_de_juego():
    entrada = (0, 0)
    merendero = (7, 11)
    estado_de_juego = {
        "merendero": merendero,
        "sendero": [entrada],
        "cursor": entrada,
        "ultimo_movimiento": 0,
        "completado": False,
        "tiempo_completado": None,
        "obstaculos": set(OBSTACULOS_BASE),
        "items_restantes": set(ITEMS_BASE),
        "items_totales": len(ITEMS_BASE),
        "items_recolectados": 0,
        "pasos": 0,
    }
    return estado_de_juego


def cargar_imagen_copernibot():
    ruta_imagen = os.path.join(os.path.dirname(__file__), "COPERNIBOT.png")
    imagen = pygame.image.load(ruta_imagen).convert_alpha()
    return pygame.transform.smoothscale(imagen, (TAMANO_CELDA - 4, TAMANO_CELDA - 4))


def cargar_imagen_merendero():
    ruta_imagen = os.path.join(os.path.dirname(__file__), "MERENDERO.png")
    imagen = pygame.image.load(ruta_imagen).convert_alpha()
    return pygame.transform.smoothscale(imagen, (TAMANO_CELDA - 4, TAMANO_CELDA - 4))


def cargar_sonido_movimiento():
    """Carga el sonido de feedback de movimiento. Si el mixer de audio no
    está disponible (por ejemplo, en un entorno sin salida de sonido), el
    juego debe poder seguir funcionando sin romperse."""
    try:
        pygame.mixer.init()
        ruta_sonido = os.path.join(os.path.dirname(__file__), "movimiento.wav")
        return pygame.mixer.Sound(ruta_sonido)
    except pygame.error as error:
        print(f"Aviso: no se pudo inicializar el audio ({error}). El juego continuará sin sonido.")
        return None


def main():
    pygame.init()
    pygame.display.set_caption("OFIRCA 2026 - Ronda 1: Inicio")
    pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
    reloj = pygame.time.Clock()

    fuente_grande = pygame.font.SysFont("consolas", 28, bold=True)
    fuente_mediana = pygame.font.SysFont("consolas", 17)
    fuente_chica = pygame.font.SysFont("consolas", 14)

    imagen_copernibot = cargar_imagen_copernibot()
    imagen_merendero = cargar_imagen_merendero()
    sonido_movimiento = cargar_sonido_movimiento()
    estado = crear_estado_de_juego()

    juego_en_ejecucion = True

    while juego_en_ejecucion:
        ahora = pygame.time.get_ticks()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                juego_en_ejecucion = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    juego_en_ejecucion = False
                elif evento.key == pygame.K_r:
                    # --- Bloque 2: sistema de reinicio ---
                    estado = crear_estado_de_juego()

        if not estado["completado"]:
            if ahora - estado["ultimo_movimiento"] >= COOLDOWN_MS:
                teclas = pygame.key.get_pressed()
                delta_fila, delta_columna = 0, 0
                if teclas[pygame.K_UP]:
                    delta_fila = -1
                elif teclas[pygame.K_DOWN]:
                    delta_fila = 1
                elif teclas[pygame.K_LEFT]:
                    delta_columna = -1
                elif teclas[pygame.K_RIGHT]:
                    delta_columna = 1
                if delta_fila != 0 or delta_columna != 0:
                    se_movio = mover_copernibot(estado, delta_fila, delta_columna)
                    estado["ultimo_movimiento"] = ahora
                    if se_movio and sonido_movimiento is not None:
                        sonido_movimiento.play()

        pantalla.fill(COLOR_FONDO)
        dibujar_grilla(pantalla, estado, fuente_chica, imagen_copernibot, imagen_merendero)
        dibujar_hud(pantalla, estado, fuente_mediana, fuente_chica)
        if estado["completado"]:
            tiempo_transcurrido = ahora - estado["tiempo_completado"]
            dibujar_cartel_completado(pantalla, fuente_grande, fuente_mediana, tiempo_transcurrido)

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
