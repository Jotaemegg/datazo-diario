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

## 6a. Storyboard (criterio de Motion Architect)
Antes del spec, escribe en `hoy/storyboard.md` una línea por escena:
**Hook (0–3 s)** → **Revelación** → **1–2 highlights** (uno por escena, concreto: "el contador sube a 20 %") → **Remate + cierre**.
- El hook debe entenderse **en silencio** (texto grande + imagen en el primer segundo).
- Una sola idea por escena; una sola cosa se mueve "en grande" a la vez; el orden de entrada = orden de lectura.
- Todo texto debe quedarse en pantalla al menos 1 s + 0.1 s por letra.

## 6. Escribir `hoy/spec.json`
Ver `test/spec.json` como ejemplo completo. Estructura:
```json
{"tag": "DATO CURIOSO", "voice": "voz.mp3",
 "scenes": [{"dur": 3.1, "elements": [ ... ]}, ...],
 "sfx": [{"name": "vine_boom", "t": 0.75, "vol": 0.55}]}
```
Colores: `W` blanco, `Y` amarillo, `P` rosa, `C` cian, `G` gris. Zona segura: x 80–1000, y 150–1550
(abajo y a la derecha está la interfaz de TikTok/IG). Tamaños de texto ya se reducen al 80 % internamente.

Movimiento por escena (motor v5):
- Transiciones automáticas entre escenas (rotan `zoom` → `slide` → `whip`; la primera abre con `flash`).
  Puedes forzar una con `"in": "zoom|slide|whip|cut"` en la escena. Varía: no repitas la misma 3 veces seguidas.
- `"punch": [t, ...]` (tiempos locales de la escena): golpe de zoom de cámara. **Ponlo exactamente donde suena
  un efecto fuerte** (vine_boom, boom_dramatico, airhorn, dato numérico). 1–2 por video, máximo uno por escena.
- `"drift": 0.03` (defecto): zoom lento para que la toma nunca esté congelada.

Elementos (`type`):
- `words` — bloque de texto que aparece palabra por palabra: `y`, `lines: [[[palabra, tamaño, color, t, estilo?], ...], ...]`.
  Títulos ~84–92, palabra clave 120–150, secundarias ~70. Estilo (opcional): `pop` (defecto: sube y aparece),
  `slam` (cae desde grande; automático si tamaño ≥ 130), `box` (tarjeta de color detrás, texto oscuro).
  **Usa `box` en 1–2 palabras clave por video** (el número o la palabra del dato), en color Y, P o C.
- `text` — un texto suelto con pop: `text, size, color, x, y, t, t_end?, wobble?`.
- `emoji` — ilustración (Noto Emoji, libre): `char, x, y, size, t, t_end?, anim` (`float|spin|bounce|shake|pulse|wiggle`),
  opcional `to: [x2, y2]` + `move` (segundos) para desplazarse. **Usar 2–4 emojis por escena relacionados al tema.**
- `meme` — foto de reacción en tarjeta con zoom de golpe: `tag, x, y, size (360–440), t, t_end?, rot`.
  Usar 2–3 memes por video en los momentos de reacción, **acompañados de un sonido de la misma emoción**,
  y no repetir los memes del video anterior. Tags disponibles (assets/memes), por emoción → sonidos que combinan:

  | Emoción | Memes | Sonidos que combinan |
  |---|---|---|
  | Shock / sorpresa | shock_gato, buho_ojos, hamster_sorprendido, sorprendido_mono, gato_intenso | vine_boom, gasp, oh_my_god, anime_wow, boom_dramatico |
  | Grito / exagerado | grito_gato, gato_grito_bostezo, gatitos_grito | faaah, airhorn, violin_chirrido, ninos_woah |
  | Duda / sospecha | pensando_mono, curioso_gato, hamster_curioso, mapache_sospecha, sospecha_perro | huh_gato, huh_pregunta, what, suspenso |
  | Juzgando / serio | mirada_seria_gato, cabra_juzgando, bulldog_serio, gato_negro_misterio | dun_dun_dun, reloj_tictac, glitch |
  | Risa / burla | gato_riendo, burlon_gato, lengua_gato, cachorro_lengua, perro_sonrisa_incomoda | risa_gato, risas_sitcom, bocina_goofy, cachetada_oh |
  | Feliz / celebración | feliz_perro, perrito_sonriente, cachorro_feliz, cabra_feliz, loro | yippee, tada, aplausos, caja_registradora, ninos_wow |
  | Enojo | enojado_gato, furioso_gato, perro_grunendo, perro_furioso, rana_enojada | buzzer_fuerte, tubo_metal, punch |
  | Triste / decepción | triste_perro, desanimado_perro, aburrido_gato, gato_atrapado | trombon_triste, publico_decepcion, error_buzzer, aww |
  | Calma / descanso / lento | mono_relajado, perezoso_feliz | ronquido, pop, burbuja_pop |
  | Huir / rápido | husky_corriendo | run_vine, silbato_slide, riser |
- `mascota` — **Inspector Bigotes**, el gato detective de la cuenta (original, sin copyright): `tag, x, y, size (420–560), t, t_end?, anim (bob|shake|bounce|pulse), flip?, rot?`.
  Aparece en **todos** los videos (1–2 veces): en el gancho inicial y/o en la reacción al dato fuerte; puede reemplazar a un meme.
  Expresiones (assets/mascota) → sonido que combina:
  shock → vine_boom/gasp · grito → faaah/airhorn · duda → huh_gato/what · sospecha → suspenso/dun_dun_dun ·
  serio → reloj_tictac/glitch · risa → risa_gato/risas_sitcom · feliz → yippee/tada · enojo → buzzer_fuerte/tubo_metal ·
  triste → trombon_triste/aww · dormido → ronquido · eureka → ding/anime_wow · pensando → reloj_tictac/burbuja_pop.
  Ponerlo en la mitad inferior (y≈1250–1400) para no tapar el texto. No repetir la misma expresión del video anterior.
- `meter` — barra que sube/baja: `label, x, y, w, t, from, to, t0, t1, color`.
- `counter` — número que cuenta: `from, to, dur, prefix?, suffix?, decimals?, size, color, x, y, t`.
- `qmarks` (signos ? girando), `confetti`, `burst` (rayos), `shake` (sacudida), `rings` (ondas),
  `clock`, `brain`, `face` (`mood: neutral|laugh`), `button` (`text: "SÍGUENOS"`).
- Escena final: emoji 😂 o 🤯 + `words` "Un dato curioso / CADA DÍA" + `button` + `confetti`.

Sonidos (`sfx`, nombres en assets/sfx; `python fetch_assets.py` los descarga con volumen igualado):

| Momento | Opciones |
|---|---|
| Dato fuerte / revelación | vine_boom, boom_dramatico, dun_dun_dun, dun_dun_brass, airhorn, tubo_metal, anime_wow |
| Sorpresa / asombro | gasp, ninos_woah, ninos_wow, oh_my_god, aww, yippee |
| Duda / confusión | huh_gato, huh_hombre, huh_pregunta, what |
| Error / mito falso | error_buzzer, buzzer_fuerte, trombon_triste, publico_decepcion, scratch_disco |
| Humor / golpe | bonk, boing, cachetada_oh, punch, hueso_crack, bocina_goofy, violin_chirrido, silbato_slide |
| Risa / celebración | risa_gato, risas_sitcom, aplausos (trim 2), tada, caja_registradora, faaah |
| Tensión / antes de revelar | suspenso, riser, reloj_tictac (trim 2), redoble (trim 2.5), glitch |
| Detalle / transición suave | pop, burbuja_pop, ding, camara (trim 0.6), ronquido (para dormir/descanso), run_vine (trim 2, huida) |

**Variedad (obligatorio):** 4–6 sonidos por video, de al menos 3 categorías distintas; máximo un
vine_boom por video y no repetir la misma combinación del video anterior (revisa el último spec en videos/).
Volumen 0.4–0.7. `trim` (s) para cortar los largos. **No usar bruh** (al dueño no le gustó).
Poner sonidos en pausas de la voz, no encima de frases clave. Los whooshes entre escenas y la música se agregan solos.

## 7. Revisar y renderizar
```bash
python engine.py hoy/spec.json hoy/prev.png --preview 1.5,6,12,18,24     # tiempos globales
# mirar prev.png (Read) con este checklist:
#  - ¿el primer frame (t≈0.4) ya engancha sin audio?   - ¿algún texto encimado o fuera de zona segura?
#  - ¿cada punch coincide con su sonido?               - ¿hay alguna escena con más de una cosa grande moviéndose?
python engine.py hoy/spec.json hoy/video.mp4
```

## 8. Entregar
- Enviar `hoy/video.mp4` al dueño con `SendUserFile` (status `proactive`), con nombre del tema.
- En el mensaje incluir: **descripción lista para pegar** (2 líneas + pregunta para comentarios),
  **hashtags para Instagram: máximo 5** (límite de IG desde dic. 2025), **para TikTok: 5–7**
  (#datoscuriosos #sabiasque #ciencia + del tema), la **fuente del dato** y el **cuadro sugerido para la portada**.
- Al final del mensaje incluir la línea para el historial: `AAAA-MM-DD | tema | fuente`
  (la sesión programada no puede hacer push; José Miguel o Claude la agregan después).

### Límite de Metricool (plan gratis: 20 publicaciones al mes, cada red cuenta 1 → un video en IG+TikTok+YouTube = 3)
- Mira la sección **Metricool** de `historial.md` (uso del mes) y súmale 3 por cada video del mes que aparezca después.
  El contador vuelve a 0 el día 1 de cada mes.
- Si con el video de hoy **se pasaría de 20**, escribe al inicio del mensaje: **"⚠️ Se acabó el límite de Metricool este mes:
  hoy toca publicar a mano"** y agrega este paso a paso:
  1. **Instagram** (app): + → Reel → elegir el video → portada: el cuadro sugerido → pegar descripción y los 5 hashtags →
     Configuración avanzada → activar "Etiqueta de IA" → Compartir.
  2. **TikTok** (app): + → Subir → elegir el video → Siguiente → pegar descripción + hashtags → Portada →
     Más opciones → activar "Contenido generado por IA" → Publicar.
  3. **YouTube** (app): + → Video corto → elegir el video → título (máx. 100 caracteres) → descripción →
     Audiencia: "No, no es contenido para niños" → "Contenido alterado o sintético": Sí → Subir video corto.
- Si quedan **3–5 publicaciones**, avisa en el mensaje: "Quedan X publicaciones de Metricool este mes".
