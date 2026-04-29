# Visual styles (engine selection)

Golpo has two video engines. **Pick exactly one per video.** They are mutually
exclusive — passing both `use_lineart_2_style` and `use_2_0_style` together is
an error. `pen_style` and `image_style` are **Canvas only** — do not use with
Sketch.

## Engine A: Golpo Sketch (`--use_lineart_2_style <value>`)

Hand-drawn / line-art whiteboard animation. Pass the value as a **string**.

| `--use_lineart_2_style` | Style name | Description |
|---|---|---|
| `false` | Classic (default) | Original Golpo Sketch — classic whiteboard line-art animation |
| `true` | Improved (BETA) | Improved line-art with cleaner strokes and a more polished look |
| `advanced` | Formal | Advanced sketch generation with higher detail and refined aesthetics |
| `whiteboard` | Dry Erase | Clean whiteboard presentation style with smooth marker-like strokes |
| `modern_minimal` | **Professional Clean** | Modern minimalist design with clean geometric shapes and indigo accent |
| `storytelling` | Crayon | Hand-drawn crayon and colored pencil illustration with bold ink outlines |

Optional with Sketch:

- `--use_color true|false` (default `true`) — color or B/W.
- `--pacing normal|fast` — `fast` shortens max time per frame from 15 s to
  10 s.

## Engine B: Golpo Canvas (`--use_2_0_style true` + `--image_style <value>`)

Richer, image-driven look. Set `--use_2_0_style true` and pick an image style:

| `--image_style` | Label | Description |
|---|---|---|
| `chalkboard_white` | Chalkboard (B/W) (default) | Black & white chalkboard style |
| `neon` | Chalkboard Color | Colorful neon chalkboard style |
| `whiteboard` | Whiteboard | Clean whiteboard illustrations |
| `modern_minimal` | Modern Minimal | Sleek, minimal modern aesthetic |
| `playful` | Playful | Fun, colorful playful illustrations |
| `technical` | Technical | Technical diagram style |
| `editorial` | Editorial | Magazine/editorial illustration style |
| `marker` | **Sharpie** | Bold marker/sharpie drawn style |

### Pen style (Canvas only — `--pen_style <value>`)

Drawing-cursor effect during animation. Canvas only.

| `--pen_style` | Description |
|---|---|
| `none` | No pen cursor (default) |
| `stylus` | Thin stylus pen cursor |
| `marker` | Thick marker cursor |
| `pen` | Classic pen cursor |

### Other Canvas-only options

- `--display_language <code>` — on-screen text language (different from
  narration `--language`).
- `--input_images <url>` (repeatable) — feed images for Canvas to use.

## Picking an engine

- **Sketch** for explainers, math/science walk-throughs, "drawn-on-the-board"
  feel.
- **Canvas** for richer visuals, branded content, magazine/social posts,
  shorts where polish matters. Pair with `pen_style` for a "hand-drawn live"
  effect.

## Common payloads

**Sketch — Professional Clean:**
```json
{ "prompt": "...", "use_lineart_2_style": "modern_minimal" }
```

**Sketch — Crayon:**
```json
{ "prompt": "...", "use_lineart_2_style": "storytelling" }
```

**Canvas — Sharpie + stylus drawing cursor (from a document):**
```json
{
  "prompt": "Summarize this for a general audience",
  "upload_urls": ["<file_url>"],
  "use_2_0_style": true,
  "image_style": "marker",
  "pen_style": "stylus"
}
```
