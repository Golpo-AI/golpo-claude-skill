# Full `generate` payload reference

Every parameter the `POST /api/v1/videos/generate` endpoint accepts. Helper
flags are `--<field_name>`.

## Required (one of)

| Field | Type | Notes |
|---|---|---|
| `prompt` | string | The topic or full prompt. Required even when `audio_clip`/`new_script`/`upload_urls` is also passed. |
| `audio_clip` | string (URL) | URL of an uploaded audio/video file to use as narration. |

## Content sources (optional, can combine)

| Field | Type | Notes |
|---|---|---|
| `new_script` | string | Custom narration script — overrides Golpo's auto-generated script. |
| `upload_urls` | string[] | Document URLs (PDF/DOCX/PPTX/TXT) to ground the script. **Single-use** — files are deleted after extraction. |
| `input_images` | string[] | Image URLs/paths for Canvas-based generation. |
| `user_images` | string[] | Image URLs to embed in the video. |
| `user_images_descriptions` | string[] | One description per `user_images`. |
| `use_as_is` | bool[] | One per `user_images`. `true` = embed without AI processing. |
| `skip_animation` | bool[] | One per `user_images`. `true` = static, no animation. |
| `user_videos` | string[] | Video URLs to embed in the output. |
| `user_videos_description` | string[] | One per `user_videos`. |
| `user_audio_in_video` | int[] | Indices into `user_videos` where AI-generated narration replaces the original audio. |

## Voice and language

| Field | Type | Default | Notes |
|---|---|---|---|
| `style` | string | `solo-female-3` | Voice ID. See `voices.md`. |
| `voice_instructions` | string | "" | Free-text guidance: "speak slowly with a British accent", etc. |
| `language` | string | `en` | Narration language code. See `languages.md`. |
| `display_language` | string | — | On-screen text language. **Canvas only** (`use_2_0_style: true`). |

## Format and pacing

| Field | Type | Default | Notes |
|---|---|---|---|
| `video_type` | string | `long` | `long` (16:9, 1536×1024) or `short` (9:16, 1024×1536). |
| `timing` | **string** | — | Duration in minutes: `"0.25"`, `"0.5"`, `"1"`, `"2"`, `"4"`, `"8"`, `"10"`, `"auto"`. Must be a string. |
| `pacing` | string | `normal` | `normal` = 15 s max per frame; `fast` = 10 s. |
| `audio_only` | bool | `false` | Generate podcast/audio only, no video. |

## Engine A — Golpo Sketch

| Field | Type | Default | Notes |
|---|---|---|---|
| `use_lineart_2_style` | **string** | `"false"` | `"false"` Classic, `"true"` Improved, `"advanced"` Formal, `"whiteboard"` Dry Erase, `"modern_minimal"` Pro Clean, `"storytelling"` Crayon. |
| `use_color` | bool | `true` | Color or B/W. |
| `pen_style` | string | — | `stylus`, `marker`, `pen`. |
| `show_pencil_cursor` | bool | `false` | Show drawing cursor during animation. |

## Engine B — Golpo Canvas

| Field | Type | Default | Notes |
|---|---|---|---|
| `use_2_0_style` | bool | `false` | Switch to Canvas engine. |
| `image_style` | string | — | `editorial`, `neon`, `whiteboard`, `modern_minimal`, `playful`, `technical`, `marker`, `chalkboard_white`. See `styles.md`. |

**Sketch and Canvas are mutually exclusive.** Don't set both.

## Music, branding, output options

| Field | Type | Default | Notes |
|---|---|---|---|
| `bg_music` | string | — | `jazz`, `lofi`, `whimsical`, `dramatic`, `engaging`, `hyper`, `inspirational`, `documentary`. See `bg_music.md`. |
| `video_instructions` | string | "" | Visual guidance: "show graphs", "include stock footage", etc. |
| `include_watermark` | bool | `false` | Add Golpo watermark. |
| `logo` | string | — | Custom logo URL or local path. |
| `logo_placement` | string | `tl` | `tl`, `tr`, `bl`, `br`. |
| `is_public` | bool | `false` | Make video publicly browsable in the Golpo gallery. |
| `just_return_script` | bool | `false` | Generate the script only — no video/podcast. |

## Response

```json
{ "job_id": "...", "video_id": "...", "status": "..." }
```

Poll `GET /videos/status/{job_id}` until `status` is terminal or `video_url`
appears.

## Validation gotchas

- `timing` must be a **string**: `"0.5"`, not `0.5`.
- `use_lineart_2_style` must be a **string**: `"false"`, not `false`.
- `prompt` is **always** required.
- Document `upload_urls` are single-use; the file is deleted after extraction.
- Recommended parallel limit: ≤ 3 simultaneous jobs.

## Pricing

Per Golpo: 2 credits per minute of generated video ($2/min). Minimum API
purchase: $200 = 200 credits.
