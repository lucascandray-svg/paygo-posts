# Motor de diseño de posts de Paygo

Genera las láminas PNG (1080×1350) en el mismo formato de todos los posts del repo: blanco y negro, serif (EB Garamond) más Inter, logo PAYGO abajo.
Reconstruido el 14 nov 2026 midiendo los posts originales: cada tipo de lámina coincide con el original dentro de 1 o 2 píxeles.

## Instalar y usar
```bash
pip install playwright --break-system-packages   # y que Chromium esté instalado (en la nube ya viene)
python3 motor/render.py motor/ejemplos/seguridad_binance.json 2026-12/05_Mi_post
```
Salida: `01.png`, `02.png`, ... en la carpeta indicada. Usá el nombre `DD_Slug` (día del mes + tema, sin tildes ni espacios), por ejemplo `2026-12/05_Mi_post`.
Las fuentes (`fonts/`) y los logos (`logo_blanco.png`, `logo_negro.png`, `logo_original.jpeg`) ya están en esta carpeta. No hay que instalar nada más.

## Formato del JSON
```json
{
  "etiqueta": "Seguridad cripto",
  "laminas": [ { "tipo": "portada", "titulo": "...", "fantasma": "5" }, ... ]
}
```
- `etiqueta`: texto pequeño arriba a la izquierda. Arriba a la derecha el motor pone solo "1 / 7".
- Saltos de línea con `\n` dentro de los textos (conviene cortar cada línea, no confiar en que se acomoden solas).
- **Fondos:** en un carrusel se alternan solos: lámina 1 oscura, 2 clara, 3 oscura... y la última siempre oscura. Una imagen sola es oscura por defecto; con `"fondo": "claro"` sale clara.
- La flecha "Desliza →" aparece sola en todas menos la última.

### Tipos de lámina (`tipo`)
| tipo | para qué | campos |
|---|---|---|
| `portada` | primera lámina del carrusel: título grande abajo | `titulo`, `fantasma` (opcional) |
| `contenido` | un paso o idea | `numero` (opcional, número grande en cursiva), `titulo`, `texto` |
| `lista` | lista con líneas finas o encuesta | `titulo`, `items` (lista), `subtitulo` (opcional, cursiva gris) |
| `frase` | frase sola, con subtítulo cursivo | `titulo`, `subtitulo` (opcional), `y` (altura, por defecto 351) |
| `cierre` | última lámina: título, texto y botón | `titulo`, `texto`, `boton` (opcional), `aviso` (opcional) |

Campos opcionales en cualquier lámina: `aviso` (letra pequeña arriba del logo, ej. "Contenido educativo. No constituye asesoría de inversión." en posts de inversión y trading), `aviso_tam`, `tam` (tamaño del título), `fondo` ("oscuro" o "claro"), `desliza` (true o false), `pos` y `total` (forzar "n / total", útil para rehacer una sola lámina).

`fantasma` es el número o palabra grande en contorno detrás del título de una portada: `"5"`, `"VS"` o un año como `"2023"`. Ya tiene posición calibrada. Se puede mover con `fantasma_x`, `fantasma_y` y `fantasma_tam`.

## Ejemplos
`ejemplos/seguridad_binance.json` es el carrusel completo del 18 de nov (7 láminas). En `ejemplos/lamina_*.json` hay un ejemplo de cada variante: lista de encuesta, frase, portada con "VS", resumen, cierre con aviso, lista clara, portada con "5", contenido sin número y portada de historia con año.

## Historias (1080×1920)
```bash
python3 motor/historia.py 2026-12/02_Presupuesto/01.png historias/2026-12/02_Presupuesto.png
```

## Cómo escribir el contenido (estilo)
- Educativo y estilo noticia, no promocional. Frases cortas. Un título de 2 a 4 líneas por lámina y un texto de máximo 3 o 4 líneas.
- Carrusel típico de 5 a 7 láminas: portada, 3 a 5 pasos y cierre con una frase para guardar el post.
- Posts de brókers: aclarar que Paygo trabaja con brókers aliados como afiliado. Posts de inversión o trading: agregar el `aviso` de contenido educativo.
- Tras generar un post, subirlo al repo en `YYYY-MM/DD_Slug/`, agregarlo a `calendario.md` del mes y programarlo con las descripciones del estilo de la sección "Descripciones" del documento de contexto.

## Limitaciones
- No existe la portada con el logo grande del primer post ("qué es Paygo"): ese se hizo aparte y no quedó en el repo.
- Palabras de más de 4 letras como `fantasma` no están calibradas (sale correcto en tamaño, pero hay que ajustar x e y).
