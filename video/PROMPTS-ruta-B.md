# FactoryMind · Antes y después — Producción (ruta B)

Vídeo de 48 s en 16:9, sin locución. Los clips con personas se generan con IA de imagen a vídeo (Kling, Runway o Veo). Los rótulos, las cifras, las barras, la pantalla dividida y el logo los añado yo en el montaje.

**Regla clave: los clips no deben llevar ningún texto.** Las IA de vídeo deforman los rótulos.

---

## Paso 0 · Limpiar los fotogramas base (obligatorio)

Los recortes del storyboard están en `video/frames-base/`. Tienen dos problemas:

- Llevan rótulos incrustados.
- Su resolución original es de solo 493 px de ancho.

Antes de pasarlos al generador de vídeo, límpialos en un editor con IA (ChatGPT Images, Gemini/Nano Banana o el relleno generativo de Photoshop) con este prompt:

```
Remove all text, labels, banners, colored boxes, captions and UI overlays from this image.
Reconstruct the hidden areas naturally (factory background, conveyor, people).
Keep the exact same composition, people, clothing, lighting and camera angle.
Upscale to 1920x1080, photorealistic, sharp details, no text anywhere.
```

| Fotograma base | Uso |
|---|---|
| `E1_problema.png` | Clip E1. También va en la mitad izquierda de la pantalla dividida (E6). |
| `E2_cuello.png` | Clip E2 |
| `E3_consultor.png` | Clip E3. Borra también "FACTORY MIND" del chaleco y el logo de la izquierda; los añado yo después. |
| `E5_despues.png` | Clip E5. También va en la mitad derecha de E6. |
| `E7_cierre_fondo.png` | Opcional. Es mejor generar E7 desde cero con el prompt de abajo. |

---

## Ajustes comunes para todos los clips

- **Resolución y formato:** 1080p, 16:9.
- **Duración:** 10 s. Recorto en montaje lo que sobre.
- **Modo:** Professional / High quality (en Kling) y movimiento entre 0,4 y 0,6 si existe ese ajuste.
- **Prompt negativo para todos:**

```
text, letters, captions, logos, watermark, subtitles, distorted hands, extra fingers,
morphing faces, flickering, people walking through tables, objects appearing from nowhere,
cartoon, CGI look, blurry, low resolution
```

---

## E1 · El problema (0:00–0:05) · usa el fotograma base `E1_problema.png`

```
Realistic industrial food factory, packaging line for empanadillas (Spanish dumplings).
Five workers in white coats, hairnets and blue gloves stand along a stainless steel conveyor.
The first workers pack trays quickly and with visible stress; trays of empanadillas pile up
in front of the third station. The fourth worker stands idle, arms crossed, waiting.
Slow lateral camera dolly from left to right along the line. Natural hand movements,
subtle body motion, cool industrial lighting, documentary style, 24fps, photorealistic.
```

## E2 · El cuello de botella (0:05–0:12) · usa el fotograma base `E2_cuello.png`

```
Close-up of a female worker in white coat, hairnet and blue gloves, working fast and stressed,
placing empanadillas into plastic trays and closing them. Behind her, stacks of pending trays
keep accumulating on the conveyor. In the background, another worker waits with little to do.
Slow push-in camera toward the worker. Realistic hand motion, shallow depth of field,
industrial food factory, photorealistic, 24fps.
```

## E3 · Entra Factory Mind (0:12–0:18) · usa el fotograma base `E3_consultor.png`

```
A male industrial engineer consultant with glasses and short beard, wearing a dark navy vest,
holding a tablet, observes a food packaging line. He looks at the line, then taps and swipes
on the tablet, then looks back up, analytical expression. Workers move in the blurred
background. Slow orbit camera from behind his shoulder. Cool blue tones, cinematic,
photorealistic, 24fps. Blank vest, no logos.
```

## E5 · El después (0:25–0:34) · usa el fotograma base `E5_despues.png`

```
Same industrial food packaging line, now working in perfect coordination. Five workers in
white coats, hairnets and blue gloves pack empanadillas at the same steady rhythm.
Trays move continuously along the conveyor at constant speed, no piles, no one waiting.
Calm, efficient, synchronized movements. Slow lateral camera dolly from left to right.
Bright clean lighting, photorealistic, documentary style, 24fps.
```

## E7 · Fondo del cierre (0:42–0:48) · de texto a vídeo (o desde `E7_cierre_fondo.png` limpio)

```
Wide shot of a large modern food factory, multiple packaging lines running smoothly,
workers in white coats moving efficiently, conveyors flowing. Slow backward camera pull-out
and slight rise. Cinematic, deep blue industrial tones, soft light, photorealistic, 24fps.
```

---

## Escenas que monto yo (sin IA de vídeo)

- **E4 · Rediseño (0:18–0:25):** animación de barras. Las cinco barras (15, 19, 30, 12, 14 s) se reparten las tareas y se igualan en 17, 18, 20, 18 y 17 s. Termina con el sello "Equilibrado optimizado · Ciclo 30 s → 20 s".
- **E6 · Resultado (0:34–0:42):** pantalla dividida con el clip de E1 a la izquierda y el de E5 a la derecha. Las tarjetas de datos aparecen en secuencia, el contador sube de 120 a 180 bandejas/h y entra el sello central "+50 % capacidad".
- **Encima de E1, E2, E3, E5 y E7:** todos los rótulos del storyboard, con la paleta azul marino, rojo y verde, y animación de entrada y salida.

---

## Entrega de los clips

Nómbralos `E1.mp4`, `E2.mp4`, `E3.mp4`, `E5.mp4` y `E7.mp4`. Súbelos al chat o a `video/clips/`.

Revisa cada clip antes de mandármelo:

- Ninguna mano deformada.
- Ninguna cara que cambie a mitad del clip.
- Ninguna bandeja que aparezca o desaparezca.

Si un clip falla, regenéralo con la misma semilla y baja el nivel de movimiento.
