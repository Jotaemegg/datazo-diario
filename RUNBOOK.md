# Datazo Diario — cómo producir el video del día

Cuenta: **Datazo Diario** (@datazo.diario_, nombre visible "Datos Curiosos") en Instagram y TikTok.
Formato: video vertical 1080×1920, 22–30 s, voz de narrador documental, animaciones con Python,
memes de animales (Pixabay) y sonidos meme. El dueño (José Miguel) **revisa y aprueba** cada video
antes de publicarlo: este proceso solo lo produce y se lo envía.

## 1. Preparar
```bash
git clone --depth 1 https://github.com/Jotaemegg/datazo-diario.git && cd datazo-diario   # repo público
pip install --break-system-packages numpy pillow   # si faltan
python fetch_assets.py                             # descarga memes y sonidos a assets/
mkdir -p hoy
```

## 2. Elegir el tema y verificarlo
- El tema del día sale de **temas.md** (número de línea según la fecha, ver la cabecera del archivo).
  No repetir nada de historial.md.
- **Verificar el dato con WebSearch en al menos 2 fuentes confiables.** Si no se confirma, pasar al siguiente tema.

## 3. Guion (70–85 palabras)
Tono serio de investigador/documental, sin exagerar emoción. Estructura:
1. **Gancho** (pregunta o afirmación que sorprenda): "¿Por qué nadie puede…?"
2. **Explicación** simple en 2–3 frases cortas con pausas ("…").
3. **Giro / dato fuerte** (experimento, número, consecuencia).
4. **Cierre fijo:** "Un dato curioso… cada día."
El texto en pantalla debe decir lo mismo que la voz (mismas palabras clave).

## 4. Voz (ElevenLabs)
- `creative_generate_speech` con `model_id: eleven_v4`, `voice_id: yHD4CsKkghm19ToGLJEC` (Hernando),
  `generations_count: 1` (ahorra créditos). Empezar el prompt con:
  `[serious investigative documentary narrator, measured pace, low and confident]`
- Esperar ~25 s, luego `creative_get_generations` para obtener `full_res_url` y descargar:
  `curl -sS -o hoy/voz.mp3 "<full_res_url>"` (el CDN de ElevenLabs es accesible).
- No reintentar la generación (cobra de nuevo).

## 5. Sincronizar
```bash
python segments.py hoy/voz.mp3
```
Da los tramos de voz separados por pausas. Asignar cada frase a su tramo; cada escena dura desde el
inicio de su primera frase hasta el inicio de la siguiente escena (la 1.ª empieza en 0).
Los tiempos `t` de los elementos son **relativos a la escena**; los de `sfx` son **globales**.

## 6. Escribir `hoy/spec.json`
Ver `test/spec.json` como ejemplo completo. Estructura:
```json
{"tag": "DATO CURIOSO", "voice": "voz.mp3",
 "scenes": [{"dur": 3.1, "elements": [ ... ]}, ...],
 "sfx": [{"name": "vine_boom", "t": 0.75, "vol": 0.55}]}
```
Colores: `W` blanco, `Y` amarillo, `P` rosa, `C` cian, `G` gris. Zona segura: x 80–1000, y 150–1550
(abajo y a la derecha está la interfaz de TikTok/IG). Tamaños de texto ya se reducen al 80 % internamente.

Elementos (`type`):
- `words` — bloque de texto que aparece palabra por palabra: `y`, `lines: [[[palabra, tamaño, color, t], ...], ...]`.
  Títulos ~84–92, palabra clave 120–150, secundarias ~70.
- `text` — un texto suelto con pop: `text, size, color, x, y, t, t_end?, wobble?`.
- `emoji` — ilustración (Noto Emoji, libre): `char, x, y, size, t, t_end?, anim` (`float|spin|bounce|shake|pulse|wiggle`),
  opcional `to: [x2, y2]` + `move` (segundos) para desplazarse. **Usar 2–4 emojis por escena relacionados al tema.**
- `meme` — foto de reacción en tarjeta con zoom de golpe: `tag, x, y, size (360–440), t, t_end?, rot`.
  Tags disponibles (assets/memes): shock_gato, grito_gato, feliz_perro, pensando_mono, sorprendido_mono,
  mirada_seria_gato, curioso_gato, triste_perro, enojado_gato, furioso_gato, burlon_gato, aburrido_gato,
  sospecha_perro, desanimado_perro. Usar 2–3 memes por video en los momentos de reacción.
- `meter` — barra que sube/baja: `label, x, y, w, t, from, to, t0, t1, color`.
- `counter` — número que cuenta: `from, to, dur, prefix?, suffix?, decimals?, size, color, x, y, t`.
- `qmarks` (signos ? girando), `confetti`, `burst` (rayos), `shake` (sacudida), `rings` (ondas),
  `clock`, `brain`, `face` (`mood: neutral|laugh`), `button` (`text: "SÍGUENOS"`).
- Escena final: emoji 😂 o 🤯 + `words` "Un dato curioso / CADA DÍA" + `button` + `confetti`.

Sonidos (`sfx`, nombres en assets/sfx): vine_boom, huh_gato, huh_hombre, boing, ding, risa_gato,
risas_sitcom, scratch_disco, faaah, bruh. Volumen 0.45–0.8. `trim` (s) para cortar los largos.
**No usar bruh** (al dueño no le gustó). Poner sonidos en pausas de la voz, no encima de frases clave.
Los whooshes entre escenas y la música se agregan solos.

## 7. Revisar y renderizar
```bash
python engine.py hoy/spec.json hoy/prev.png --preview 1.5,6,12,18,24     # tiempos globales
# mirar prev.png (Read): textos dentro de zona segura, nada encimado
python engine.py hoy/spec.json hoy/video.mp4
```

## 8. Entregar
- Enviar `hoy/video.mp4` al dueño con `SendUserFile` (status `proactive`), con nombre del tema.
- En el mensaje incluir: **descripción lista para pegar** (2 líneas + pregunta para comentarios),
  **hashtags para Instagram: máximo 5** (límite de IG desde dic. 2025), **para TikTok: 5–7**
  (#datoscuriosos #sabiasque #ciencia + del tema), la **fuente del dato** y el **cuadro sugerido para la portada**.
- Al final del mensaje incluir la línea para el historial: `AAAA-MM-DD | tema | fuente`
  (la sesión programada no puede hacer push; José Miguel o Claude la agregan después).
