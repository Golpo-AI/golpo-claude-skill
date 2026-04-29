# Golpo Skill for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![Plugin: 0.1.1](https://img.shields.io/badge/plugin-v0.1.1-green.svg)]()

> Generate AI videos with [Golpo](https://video.golpoai.com) directly from any
> Claude Code conversation. Give Claude a prompt, a script, an audio file, or
> a PDF — Claude submits the job, polls until it's done, **downloads the MP4
> to your computer**, and shows you the file path plus the hosted URL.

```text
You:    "Make a 30-second video about why the sky is blue."
Claude: ✓ Submitted. Polling… 12% … 47% … 94% … done.
        Saved to ~/Golpo/videos/20260429-015405_why-is-the-sky-blue_a1b2c3d4.mp4
        Also at https://video.golpoai.com/...
```

---

## Table of contents

- [What it does](#what-it-does)
- [Install](#install)
- [First run](#first-run)
- [Usage examples](#usage-examples)
- [Where videos are saved](#where-videos-are-saved)
- [The full input matrix](#the-full-input-matrix)
- [Visual styles](#visual-styles)
- [Voices, languages, music](#voices-languages-music)
- [Direct CLI use](#direct-cli-use)
- [File map](#file-map)
- [How the skill works internally](#how-the-skill-works-internally)
- [Troubleshooting](#troubleshooting)
- [Self-hosting / forking](#self-hosting--forking)
- [Pricing](#pricing)
- [Links](#links)

---

## What it does

The plugin registers a Claude Code skill named `golpo` with one helper script
underneath. When you ask Claude to make a video, the skill:

1. Verifies your environment (Python, `requests`, API key).
2. Asks for your Golpo API key on first run, saves it to `~/.golpo/api_key`
   with `0600` perms.
3. Gathers requirements from your message — prompt, script, attachments,
   duration, voice, language, style. Defaults are sensible so most asks need
   no follow-up.
4. Uploads any audio/document files (two-step: API call + S3 PUT).
5. Submits the generate job, then polls the status endpoint with exponential
   backoff. Resilient to transient 5xx errors.
6. **Downloads the MP4 to `~/Golpo/videos/`** with a readable filename.
7. Shows you the local file (clickable) and the hosted URL.

It supports both Golpo engines:
- **Golpo Sketch** — whiteboard line-art animation (Classic, Improved,
  Formal, Dry Erase, **Professional Clean**, Crayon).
- **Golpo Canvas** — richer, image-driven look (Chalkboard B/W, Chalkboard
  Color, Whiteboard, Modern Minimal, Playful, Technical, Editorial,
  **Sharpie**), with optional drawing-cursor effects.

---

## Install

### Recommended — plugin marketplace

In the Claude Code terminal CLI:

```text
/plugin marketplace add Golpo-AI/golpo-claude-skill
/plugin install golpo@GolpoSkill
```

> `golpo` is the plugin `name`; `GolpoSkill` is the marketplace `name`. Both
> are case-sensitive.

`/plugin update golpo` later when a new version ships.

### Manual

```bash
git clone https://github.com/Golpo-AI/golpo-claude-skill.git ~/.claude/plugins/golpo
```

Restart Claude Code.

### From a local checkout (for forks / dev)

```bash
git clone https://github.com/Golpo-AI/golpo-claude-skill.git
cd golpo-claude-skill
# In Claude Code:
#   /plugin marketplace add /absolute/path/to/golpo-claude-skill
#   /plugin install golpo@GolpoSkill
```

### Requirements

- **Python 3.8+** (preinstalled on macOS and most Linux distros).
- **`requests`** Python package — install with `pip3 install --user requests`
  if missing. The skill prompts you with the exact command.
- **A Golpo API key** — get one at https://video.golpoai.com (API tier:
  $200 minimum entry, $1 = 1 credit, 2 credits per minute of video).

---

## First run

The first time you ask Claude to make a video:

1. Claude runs `golpo.py check` and notices `key_configured=false`.
2. It explains that the skill needs your API key, then asks you to paste it.
3. Behind the scenes it runs `golpo.py auth --key <YOUR_KEY>`.
4. Subsequent invocations skip auth.

The key lives at `~/.golpo/api_key` (mode `0600`). To rotate later:

```bash
python3 ~/.claude/plugins/golpo/skills/golpo/scripts/golpo.py auth --key NEW_KEY --force
```

To use an env var instead (overrides the file):

```bash
export GOLPO_API_KEY=...
```

---

## Usage examples

Just talk to Claude in plain English:

| You say | Claude does |
|---|---|
| "Make a 30-second video about why the sky is blue." | Prompt → Sketch Classic, default voice, 0.5 min |
| "Make it a vertical short with marker style." | Adds `--video_type short --use_2_0_style true --image_style marker` |
| "Use this script: \<paste\>" | Adds `--new_script "..."` (and bumps timing if your script is longer than the requested duration) |
| "Use my voice from `~/voice.mp3`." | Calls `upload`, then `--audio_clip <url>` |
| "Summarize this PDF: `~/report.pdf`." | Calls `upload`, then `--upload_urls <url>` |
| "Hindi narration with English captions." | `--language hi --display_language en` (Canvas only) |
| "Save it to `~/Desktop/clips/` instead." | Adds `--output_dir ~/Desktop/clips/` |
| "Don't download, just give me the URL." | Adds `--no_download` |
| "List my last 5 videos." | `golpo.py list --limit 5` |
| "Re-download video `<id>`." | `golpo.py get <id>` |

---

## Where videos are saved

**Default:** `~/Golpo/videos/`

**Filename pattern:**
```
YYYYMMDD-HHMMSS_<title-slug>_<video-id-short>.mp4
```

The slug comes from the API-canonical video title (what `golpo.py list` and
the Golpo dashboard show), so files match the names you see elsewhere.

For example:
```
~/Golpo/videos/20260429-015405_why-is-the-sky-blue_a1b2c3d4.mp4
~/Golpo/videos/20260429-015628_summarize-this-document-about-ocean-tides_b18d3425.mp4
```

**Override per-video:**
```bash
python3 .../golpo.py generate --prompt "..." --output_dir ~/Desktop/clips/
```
…or just say to Claude "save it to ~/Desktop/clips/".

**Override globally:**
```bash
export GOLPO_VIDEO_DIR=~/Desktop/clips
```

**Skip the download (URL only):**
```bash
python3 .../golpo.py generate --prompt "..." --no_download
```

The hosted URL is always printed too, so you can share without downloading.

---

## The full input matrix

| Input | Required field | Optional with |
|---|---|---|
| **Prompt only** | `--prompt "..."` | any styling, voice, language, music |
| **Prompt + custom script** | `--prompt "..." --new_script "..."` | (script length must fit the chosen `--timing`) |
| **Audio narration** | `--prompt "..." --audio_clip <url>` | upload first; ≤ 15 MB |
| **Document(s)** | `--prompt "..." --upload_urls <url>` (repeatable) | PDF/DOCX/PPTX/TXT, ≤ 15 MB each, **single-use** |
| **Embed images** | `--user_images <url>` + `--user_images_descriptions "..."` | per-image `--use_as_is` / `--skip_animation` flags |
| **Embed videos** | `--user_videos <url>` + `--user_videos_description "..."` | optional `--user_audio_in_video <idx>` |
| **Custom logo** | `--logo <url>` | `--logo_placement tl|tr|bl|br` |

> `prompt` is **always required**, even when also passing `audio_clip` /
> `new_script` / `upload_urls`. The Golpo backend uses it as the title /
> framing.

---

## Visual styles

### Golpo Sketch — `--use_lineart_2_style <value>`

Whiteboard line-art animation. Pass as a **string**.

| Value | Style name | Description |
|---|---|---|
| `false` | Classic (default) | Original Golpo Sketch — whiteboard line-art |
| `true` | Improved (BETA) | Cleaner strokes, more polished |
| `advanced` | Formal | Higher detail, refined aesthetics |
| `whiteboard` | Dry Erase | Smooth marker-like strokes |
| `modern_minimal` | **Professional Clean** | Geometric shapes with indigo accent |
| `storytelling` | Crayon | Hand-drawn crayon and colored pencil |

### Golpo Canvas — `--use_2_0_style true --image_style <value>`

Richer, image-driven look.

| `--image_style` | Label | Description |
|---|---|---|
| `chalkboard_white` | Chalkboard (B/W) (default) | Black & white chalkboard |
| `neon` | Chalkboard Color | Colorful neon chalkboard |
| `whiteboard` | Whiteboard | Clean whiteboard illustrations |
| `modern_minimal` | Modern Minimal | Sleek, minimal aesthetic |
| `playful` | Playful | Fun, colorful illustrations |
| `technical` | Technical | Diagrammatic style |
| `editorial` | Editorial | Magazine-style illustration |
| `marker` | **Sharpie** | Bold marker/sharpie drawn |

Add a drawing-cursor effect on Canvas: `--pen_style stylus|marker|pen`.

> **Sketch and Canvas are mutually exclusive.** Pick one engine per video.

---

## Voices, languages, music

**Voices** (`--style`):
- `solo-female-3` (default) — warm, neutral
- `solo-female-4` — brighter, energetic
- `solo-male-3` — calm, authoritative
- `solo-male-4` — deeper, dramatic

**Languages** (`--language`):
44+ codes. Common: `en` (default), `hi`, `es`, `fr`, `de`, `pt`, `ja`, `ko`,
`zh`, `ar`, `bn`, `ta`, `ur`. Full list:
[references/languages.md](plugins/golpo/skills/golpo/references/languages.md).

**Background music** (`--bg_music`):
`jazz`, `lofi`, `whimsical`, `dramatic`, `engaging`, `hyper`, `inspirational`,
`documentary`. Omit for narration-only audio.

---

## Direct CLI use

The helper is a standalone CLI — Claude Code is just one front-end.

```bash
HELPER=~/.claude/plugins/golpo/skills/golpo/scripts/golpo.py

# Sanity check
python3 "$HELPER" check

# Save the API key
python3 "$HELPER" auth --key sk-...

# Upload an attachment
python3 "$HELPER" upload ~/report.pdf
# -> FILE_URL=https://...

# Generate (auto-downloads to ~/Golpo/videos/)
python3 "$HELPER" generate \
  --prompt "Summarize this report" \
  --upload_urls "https://..." \
  --use_2_0_style true --image_style marker --pen_style stylus \
  --timing 1 --video_type long
# -> JOB_ID=...
# -> progress=0% status=generating
# -> ...
# -> VIDEO_FILE=/Users/you/Golpo/videos/20260429-015405_summarize-this-report_b18d3425.mp4
# -> VIDEO_URL=https://...

# Manage existing videos
python3 "$HELPER" list --limit 10
python3 "$HELPER" get <video_id>      # re-downloads
python3 "$HELPER" get <video_id> --no_download
python3 "$HELPER" status <job_id>
```

`python3 "$HELPER" generate --help` lists every flag.

---

## File map

```
golpo-claude-skill/                  # marketplace root
├── .claude-plugin/
│   └── marketplace.json             # lists plugins in this repo
├── plugins/
│   └── golpo/                       # plugin root
│       ├── .claude-plugin/
│       │   └── plugin.json          # plugin manifest
│       └── skills/
│           └── golpo/                # the skill
│               ├── SKILL.md          # instructions Claude follows
│               ├── QUICKSTART.md     # human-friendly cheat sheet
│               ├── scripts/
│               │   ├── golpo.py      # CLI helper
│               │   └── requirements.txt
│               └── references/       # loaded on demand
│                   ├── voices.md
│                   ├── styles.md
│                   ├── languages.md
│                   ├── bg_music.md
│                   └── full-payload.md
├── README.md                         # this file
└── LICENSE
```

---

## How the skill works internally

1. **Trigger.** Claude Code matches the user's message against the `description`
   field of [SKILL.md](plugins/golpo/skills/golpo/SKILL.md). The skill fires
   on phrasing like "make a video", "create an explainer", "summarize this
   PDF as a video", etc.
2. **Bootstrap.** Claude runs `golpo.py check` to confirm Python, `requests`,
   and the API key are in place.
3. **Auth (first run).** If no key, Claude asks for it and saves it via
   `golpo.py auth --key <KEY>`.
4. **Plan.** Claude turns the user's intent into a concrete payload, defaulting
   anything they didn't specify.
5. **Upload.** For audio or document inputs, Claude calls `golpo.py upload`
   per file. The helper does the two-step flow: POST to
   `/api/v1/videos/upload-file` to get a presigned S3 URL, then PUT the file
   to that URL.
6. **Generate.** `golpo.py generate` POSTs `/api/v1/videos/generate` with the
   payload, captures `job_id` and `video_id`, and polls
   `/api/v1/videos/status/{job_id}` until terminal. Polling backs off
   exponentially (5 s → 30 s) and retries 5xx up to 5 times.
7. **Download.** When the API returns `video_url`, the helper streams the MP4
   to `~/Golpo/videos/` (or your override) with a readable filename.
8. **Report.** Helper prints `VIDEO_FILE=<path>` and `VIDEO_URL=<url>`. Claude
   shows both to you with a clickable file link.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `requests_ok=false` from `check` | `pip3 install --user requests` |
| `ERROR: 401 Unauthorized` | API key rejected: `auth --key NEW --force` |
| `ERROR: 403 Forbidden` | Plan doesn't include the action; visit https://video.golpoai.com |
| `ERROR: 422` with `timing` complaint | Pass timing as a string: `--timing 0.5`, not `0.5` (the helper does this for you, but check your call) |
| `ERROR: 422 script duration N min > timing M min` | Bump `--timing` higher than `N` |
| `ERROR: 429 Rate limited` | Cap parallel jobs at 3; back off and retry |
| `WARNING: download failed` | Hosted URL still printed; download manually with `curl` or retry `golpo.py get <video_id>` |
| Job times out at 30 min | `--max_wait_seconds 5400` to extend, or resume later: `golpo.py status <JOB_ID>` |
| Document URL fails on second use | Document URLs are **single-use**; re-upload the file |
| `--use_lineart_2_style` and `--use_2_0_style` both set | Pick one — Sketch and Canvas are mutually exclusive |

---

## Self-hosting / forking

To run this from your own GitHub repo:

1. Fork or clone this repo and push to your `<org>/<repo>`.
2. Tell users:
   ```
   /plugin marketplace add <your-org>/<repo>
   /plugin install golpo@GolpoSkill
   ```
3. When shipping changes, bump `version` in **both**
   [plugins/golpo/.claude-plugin/plugin.json](plugins/golpo/.claude-plugin/plugin.json)
   and [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
   (keep them in sync), then optionally tag a release:
   ```bash
   git tag v0.2.0
   git push --tags
   ```

End users update with `/plugin update golpo`.

---

## Pricing

- **API tier minimum:** $200 USD = 200 credits.
- **Cost per credit:** $1 USD = 1 credit.
- **Video cost:** 2 credits per minute of generated video → ~$0.50 for a
  15-second video, $2 for a one-minute video.

The helper does not surface pricing — Golpo's billing happens server-side.
Check your usage at https://video.golpoai.com.

---

## Links

- **Golpo:** https://video.golpoai.com
- **API docs:** https://video.golpoai.com/api-docs/endpoints/v1
- **Payload examples:** https://video.golpoai.com/guide/golpo-ai-video-api-payload-examples
- **Issue tracker:** https://github.com/Golpo-AI/golpo-claude-skill/issues
- **License:** [MIT](LICENSE)
