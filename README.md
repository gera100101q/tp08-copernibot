#COPERNIBOT 

Trabajo Práctico N° 8 - Laboratorio de Aplicaciones II (6° G)

Juego de grilla desarrollado en **Python 3.12.3** con **Pygame**, donde COPERNIBOT debe recorrer un mapa recolectando donaciones y llegar al merendero sin volver a pisar su propio camino ni chocar contra obstáculos.

## Objetivo

Aplicar lógica de grilla matricial, manejo de recursos multimedia (imágenes y sonido) y estructuras de datos, integrando técnicas de IA de forma ética y documentada durante el desarrollo.

## Estructura del proyecto

```
.
├── copernibot.py       # Código completo del juego
├── COPERNIBOT.png      # Sprite del avatar
├── MERENDERO.png       # Ícono de la casilla objetivo
└── movimiento.wav      # Sonido de feedback al moverse
```

> Los 4 archivos deben estar en la **misma carpeta** para que el juego cargue los recursos correctamente.

## Cómo ejecutar

Requiere Python 3.12.3 y Pygame instalado:

```bash
pip install pygame
python copernibot.py
```

## Controles

| Tecla | Acción |
|---|---|
| ↑ ↓ ← → | Mover a COPERNIBOT |
| R | Reiniciar el nivel |
| ESC | Salir |

## Funcionalidades

### Bloque 1: Mundo y COPERNIBOT
- Grilla de 12x8 celdas con panel lateral (HUD).
- Contador de pasos en tiempo real.
- Sprite de COPERNIBOT e ícono del merendero cargados como imágenes.
- Feedback sonoro corto en cada movimiento válido (con manejo de error si no hay salida de audio disponible).

### Bloque 2: Lógica de juego
- **Sendero:** COPERNIBOT no puede volver a pisar una celda ya visitada.
- **Obstáculos:** 4 celdas fijas funcionan como paredes infranqueables.
- **Reinicio:** la tecla `R` restablece el estado del juego en cualquier momento.
- **Victoria animada:** al llegar al merendero se muestra un cartel con efecto de pulso y fade-in.
- **Extra (funcionalidad original):** 4 donaciones recolectables distribuidas en el mapa, con contador propio en el HUD (`Donaciones: X/4`).

## Uso de Inteligencia Artificial

Este proyecto fue desarrollado con asistencia de IA (Claude, Anthropic). la ia me ayudo con l detalle de herramienta, objetivo, aprendizaje y verificación.
el promt esacto fue " ayudame a ordenar este tabajo, hace un prueva lojica y crea un readmi con la informacion q tengas lo otro de el uso de ia transparente lo completo yo entre otas cosas q quiero q me avises q tengo q completar" 

## Autor

Gera - Laboratorio de Aplicaciones II - IPET N°249
