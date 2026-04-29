# Voices (the `style` parameter)

Pass one of these to `--style` when generating a video. The Golpo API uses
the `style` parameter as the **voice** selector.

| Value | Description |
|---|---|
| `solo-female-3` | Default. Warm, neutral-accent female narration. Versatile across topics. |
| `solo-female-4` | Brighter, more energetic female voice. Good for marketing/social. |
| `solo-male-3` | Default male voice. Calm, authoritative; works well for explainers. |
| `solo-male-4` | Deeper, more dramatic male voice. Good for documentary tone. |

When using a non-English `--language`, pick any voice — Golpo's TTS adapts the
voice to the chosen language. If the user wants narration in one language but
on-screen text in another, use `--display_language` (Canvas only:
`--use_2_0_style true`).
