# Visual styles (engine selection)

Golpo has two video engines. **Pick exactly one per video.** They are mutually
exclusive — passing both `use_lineart_2_style` and `use_2_0_style` together is
an error.

## Engine A: Golpo Sketch (`--use_lineart_2_style <value>`)

Hand-drawn / line-art style. Pass the value as a **string**.

| Value | Look |
|---|---|
| `false` | Classic sketch (default). Black lines on white. |
| `true` | Improved sketch — cleaner, more polished line work. |
| `advanced` | Formal/professional sketch — corporate-friendly. |
| `whiteboard` | Dry-erase whiteboard look. |
| `modern_minimal` | Clean professional minimalist. |
| `storytelling` | Crayon / storybook texture. |

Optional with Sketch:

- `--use_color true|false` (default `true`) — turn color on/off.
- `--pen_style stylus|marker|pen` and `--show_pencil_cursor true` — show a
  drawing cursor that traces each frame.
- `--pacing normal|fast` — `fast` shortens max time per frame from 15 s to
  10 s.

## Engine B: Golpo Canvas (`--use_2_0_style true` + `--image_style <value>`)

Richer, image-driven look. Set `--use_2_0_style true` and pick an image style:

| `--image_style` | Look |
|---|---|
| `editorial` | Magazine / publication look. |
| `neon` | Vibrant neon-lit aesthetic. |
| `whiteboard` | Whiteboard-styled illustrations. |
| `modern_minimal` | Flat, minimalist, clean. |
| `playful` | Fun, friendly, colorful. |
| `technical` | Diagrammatic / technical illustration. |
| `marker` | Marker-pen feel. |
| `chalkboard_white` | Chalkboard texture. |

Canvas-only options:

- `--display_language <code>` — on-screen text language (different from
  narration `--language`).
- `--input_images <url>` (repeatable) — feed images for Canvas to use.

## Picking an engine

- **Sketch** for explainers, math/science walk-throughs, "drawn-on-the-board"
  feel, lower-bandwidth aesthetic.
- **Canvas** for richer visuals, branded content, magazine/social posts,
  shorts where polish matters.
