---
name: golpo
description: Generate AI videos with Golpo. Use when the user asks to make/create/produce a video, animated explainer, podcast-to-video, or wants Golpo to turn a prompt, custom script, audio file, or document into a video. Handles single-prompt, long-script, audio-narration, and document-grounded video generation, polls for completion, and returns the final video URL.
---

# Golpo Video Skill

This skill turns a user request into a finished video using the Golpo Video API
(`https://api.golpoai.com/api/v1`). It accepts:

- a **prompt** (Golpo writes the script),
- a **prompt + custom script** (`new_script`),
- a **prompt + audio narration** (`audio_clip`),
- a **prompt + supporting documents** (`upload_urls`: PDF/DOCX/PPTX/TXT),
- or any combination, plus optional images, logos, and styling.

All work goes through the bundled Python helper at
`${CLAUDE_PLUGIN_ROOT}/skills/golpo/scripts/golpo.py`. Always invoke it via
`python3` with that absolute path.

## 1. Bootstrap on every invocation

Run the helper's environment check first:

```bash
python3 "$CLAUDE_PLUGIN_ROOT/skills/golpo/scripts/golpo.py" check
```

It prints machine-parsable lines:

```
python_ok=true|false
python_version=3.x
requests_ok=true|false
key_configured=true|false
key_source=env|file|none
```

- If `python_ok=false`, tell the user to install Python 3.8+.
- If `requests_ok=false`, tell the user to run
  `pip3 install --user requests` (or `pip install requests` in their venv).
- If `key_configured=false`, go to step 2.

## 2. API key (one-time)

If no key is configured, ask the user to paste their Golpo API key. Explain:

> Your key will be saved to `~/.golpo/api_key` with `0600` permissions. You
> can rotate it any time with the same command, and `GOLPO_API_KEY` env var
> overrides the file if set. Get a key at https://video.golpoai.com.

Once they provide it, save it:

```bash
python3 "$CLAUDE_PLUGIN_ROOT/skills/golpo/scripts/golpo.py" auth --key "<KEY>"
```

Add `--force` to overwrite an existing key. Re-run `check` to confirm
`key_configured=true`.

## 3. Gather requirements

Figure out what video the user wants. Most users will say "make a video about
X" — just default everything sensible and tell them what you defaulted to. Only
ask follow-ups if the request is ambiguous or the user explicitly wants
control.

Sensible defaults:

| Field | Default | Notes |
|---|---|---|
| `timing` | `"0.5"` (~30s) | string; allowed: `"0.25"`, `"0.5"`, `"1"`, `"2"`, `"4"`, `"8"`, `"10"`, `"auto"` |
| `video_type` | `"long"` | `long` = 16:9, `short` = 9:16 vertical |
| `style` | `"solo-female-3"` | voice. See `references/voices.md` |
| `language` | `"en"` | narration language. See `references/languages.md` |
| engine | Sketch Classic (`use_lineart_2_style="false"`) | for Canvas, set `use_2_0_style=true` and pick an `image_style` |

Important field gotchas (the API rejects wrong types):

- `timing` is a **string**, not a number: `"0.5"`, not `0.5`.
- `use_lineart_2_style` is a **string**: `"false"`, `"true"`, `"advanced"`,
  `"whiteboard"`, `"modern_minimal"`, `"storytelling"`. The helper coerces for
  you, but pass it as a string anyway.
- `use_2_0_style` is a **boolean**.
- `prompt` is required even when `audio_clip`, `new_script`, or `upload_urls`
  is also passed.
- Sketch (`use_lineart_2_style`) and Canvas (`use_2_0_style`) are mutually
  exclusive — pick one engine per video.

For style/voice/language/music details, read the reference files on demand:
`references/voices.md`, `references/styles.md`, `references/languages.md`,
`references/bg_music.md`. For every parameter, see `references/full-payload.md`.

## 4. Upload step (only if the user provides an audio file or document)

Run upload once per file. Files must be ≤ 15 MB.

```bash
python3 "$CLAUDE_PLUGIN_ROOT/skills/golpo/scripts/golpo.py" upload /path/to/file.mp3
```

The helper prints JSON and a final `FILE_URL=<url>` line. Use that URL:

- audio narration → pass as `--audio_clip <FILE_URL>`
- documents (PDF/DOCX/PPTX/TXT) → pass as `--upload_urls <FILE_URL>` (you can
  pass `--upload_urls` multiple times to attach several documents)
- input images for Canvas → `--input_images <FILE_URL>`
- user images embedded in the video → `--user_images <FILE_URL>`
  (paired with `--user_images_descriptions "<desc>"` per image)

**Document URLs are single-use** — Golpo deletes the file after extraction. If
the user wants to regenerate, re-upload.

## 5. Generate

Submit the job. Each API field is a `--<field>` flag. Repeatable list fields
(`--upload_urls`, `--input_images`, `--user_images`,
`--user_images_descriptions`, `--user_videos`, `--user_videos_description`,
`--use_as_is`, `--skip_animation`, `--user_audio_in_video`) take one
occurrence per value.

Examples:

**Simple prompt, 30 s, default voice and Sketch Classic:**
```bash
python3 "$CLAUDE_PLUGIN_ROOT/skills/golpo/scripts/golpo.py" generate \
  --prompt "Why is the sky blue?" \
  --timing 0.5 \
  --video_type long
```

**Prompt + custom script in Canvas Editorial:**
```bash
python3 "$CLAUDE_PLUGIN_ROOT/skills/golpo/scripts/golpo.py" generate \
  --prompt "Why is the sky blue?" \
  --new_script "Sunlight looks white, but it's really every color of the rainbow..." \
  --use_2_0_style true --image_style editorial \
  --timing 0.5 --style solo-male-3 --video_type long --language en
```

**User-provided audio narration:**
```bash
# 1. upload
python3 .../golpo.py upload my_narration.mp3
# -> FILE_URL=https://...

# 2. generate using that url
python3 .../golpo.py generate \
  --prompt "Why is the sky blue?" \
  --audio_clip "https://..." \
  --timing 0.5 --video_type long --language en
```

**Document-grounded vertical short with background music:**
```bash
python3 .../golpo.py upload report.pdf  # -> FILE_URL=...
python3 .../golpo.py generate \
  --prompt "Summarize the Q3 earnings report" \
  --upload_urls "<FILE_URL>" \
  --video_type short --timing 1 \
  --style solo-female-4 --bg_music documentary
```

**Hindi voice with English on-screen text (Canvas only):**
```bash
python3 .../golpo.py generate \
  --prompt "Why is the sky blue?" \
  --use_2_0_style true --image_style marker \
  --style solo-female-3 --language hi --display_language en \
  --timing 0.5 --video_type long
```

The helper:
1. Submits `POST /videos/generate` and prints `JOB_ID=...` and `VIDEO_ID=...`.
2. Polls `GET /videos/status/{job_id}` with backoff (5 s → 30 s, capped at
   **90 min** by default; use `--max_wait_seconds N` to extend further).
   Polling is resilient to transient 5xx responses (up to 5 retries with
   exponential backoff).
3. Streams `progress=N% status=<state>` lines while it polls — relay these to
   the user as short progress updates.
4. **Auto-downloads the rendered MP4 to `~/Golpo/videos/`** by default.
   Filename pattern: `YYYYMMDD-HHMMSS_<title-slug>_<video-id-short>.mp4` —
   the slug is derived from the API-canonical video title (same string the
   user sees in `golpo.py list` and the Golpo dashboard).
   Override with `--output_dir <path>` or set `GOLPO_VIDEO_DIR` env var.
   Skip the download with `--no_download`.
5. On success, prints `VIDEO_FILE=/abs/path.mp4` then `VIDEO_URL=<url>` and
   exits 0.
6. On failure, prints `ERROR: ...` to stderr and exits non-zero.

## 6. Show the result

When `VIDEO_FILE=...` and `VIDEO_URL=...` appear, present **both** to the user
— the local file (they can play it immediately by clicking) and the URL (for
sharing). One-line summary of the params used, e.g.:

> Video ready, saved to
> [`~/Golpo/videos/20260429-015405_why-is-the-sky-blue_a1b2c3d4.mp4`](file:///Users/.../Golpo/videos/20260429-015405_why-is-the-sky-blue_a1b2c3d4.mp4).
> 30 s, 16:9, solo-female-3, English, Sketch Classic. Hosted at
> [Golpo](https://...). Re-download later with
> `python3 .../golpo.py get <VIDEO_ID>`.

If the user wants the file somewhere else, regenerate with `--output_dir <dir>`
or `export GOLPO_VIDEO_DIR=<dir>` once. To skip downloading (URL only), pass
`--no_download`. If the user wants to make adjustments, regenerate with the
changed flags. Note that uploaded **document** URLs cannot be reused —
re-upload to retry.

## 7. Error handling

- `ERROR: 401` → API key was rejected. Ask for a new key and re-run
  `auth --force`.
- `ERROR: 422` followed by a JSON `detail` array → surface the validation
  messages verbatim. The most common cause is a numeric `timing` or boolean
  `use_lineart_2_style`; the helper coerces these but check first if the
  user passed something exotic.
- `ERROR: 429` → rate-limited. Wait a minute and retry; if it persists,
  recommend running ≤ 3 jobs in parallel.
- `ERROR: 403` → the user's plan doesn't include the action; point them to
  https://video.golpoai.com.
- Network errors → retry once; if it still fails, surface the error.
- Timeout (`ERROR: timed out after Ns`) → the job may still be running. Tell
  the user the `JOB_ID` and how to resume:
  `python3 .../golpo.py status <JOB_ID>`.

## 8. Other useful commands

- `python3 .../golpo.py list --limit 10` — list the user's recent videos.
- `python3 .../golpo.py get <video_id>` — fetch metadata + URL for one video.
- `python3 .../golpo.py status <job_id>` — one-shot status check.

## 9. What to read on demand

Don't load these unless the user asks about advanced options:

- `references/voices.md` — voice IDs.
- `references/styles.md` — Sketch and Canvas style values, mutual exclusivity.
- `references/languages.md` — 44+ language codes.
- `references/bg_music.md` — background music options.
- `references/full-payload.md` — every parameter, type, default, and notes.
