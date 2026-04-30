# Golpo Skill — Quickstart

Five steps from zero to a finished video.

## 1. Install (once per machine)

In the Claude Code terminal CLI:

```text
/plugin marketplace add Golpo-AI/golpo-claude-skill
/plugin install golpo@GolpoSkill
```

`golpo` is the plugin name; `GolpoSkill` is the marketplace name. Both are
case-sensitive.

> Already cloned the repo locally? Use the path:
> `/plugin marketplace add /path/to/GolpoSkill`

## 2. First-time setup

The skill needs Python 3.8+ and the `requests` library. If `requests` is
missing, the skill will tell you how to install it. Then it will ask for your
Golpo API key. Get one at [video.golpoai.com](https://video.golpoai.com)
(API tier; $2/credit, ~$0.50 per 15-second video).

The key gets saved to `~/.golpo/api_key` with `0600` permissions. To rotate
later: `python3 ~/.claude/plugins/golpo/skills/golpo/scripts/golpo.py auth --key NEW --force`.

## 3. Ask Claude to make a video

The skill triggers on natural language. Try any of these:

```
make a 30-second video about why the sky is blue
turn this script into a vertical short with marker style: <paste script>
summarize this PDF as a 1-minute video: /path/to/report.pdf
hindi narration with english on-screen text, pythagorean theorem, canvas whiteboard
```

Claude will:
1. Pick sensible defaults (30 s, 16:9, English, female narrator, Sketch Classic).
2. Tell you what defaults it used so you can adjust.
3. Submit the job and stream progress (`progress=42% status=generating`).
4. **Download the rendered MP4 to `~/Golpo/videos/`** when done.
5. Show you the local file path *and* the hosted URL.

## 4. Where your videos live

Default destination: **`~/Golpo/videos/`**.

Filename pattern: `YYYYMMDD-HHMMSS_<title-slug>_<video-id-short>.mp4` — the
slug comes from the API-provided video title (matches what shows in `golpo.py
list` and the Golpo dashboard).

Example:
```
~/Golpo/videos/20260429-015405_why-is-the-sky-blue_a1b2c3d4.mp4
```

Override per-job by saying "save it to `~/Desktop/clips/`" — Claude will pass
`--output_dir ~/Desktop/clips/` to the helper. Override globally with:

```bash
export GOLPO_VIDEO_DIR=~/Desktop/clips
```

If you don't want a local copy at all, ask Claude to "skip download" and it
will pass `--no_download`.

## 5. Useful follow-ups

| Ask | What happens |
|---|---|
| "List my last 5 videos" | `golpo.py list --limit 5` |
| "Re-download video b18d3425…" | `golpo.py get b18d3425…` |
| "Check status of job 1383e1c3…" | `golpo.py status 1383e1c3…` |
| "Make it Hindi instead" | regenerate with `--language hi` |
| "Make it a vertical short" | regenerate with `--video_type short` |

## What kinds of input are supported?

| Input mode | Flags Claude uses | When to ask Claude |
|---|---|---|
| Plain prompt | `--prompt "..."` | "Make a video about X" |
| Custom script | `--prompt "..." --new_script "..."` | "Turn this script into a video: ..." |
| Audio narration | `--audio_clip <url>` (uploaded first) | "Use this MP3 as narration" |
| Document(s) | `--upload_urls <url>` (uploaded first) | "Summarize this PDF" |

## Visual style cheat-sheet

**Golpo Sketch** (whiteboard line-art animation):

| Style | Flag |
|---|---|
| Classic (default) | `--use_lineart_2_style false` |
| Improved | `--use_lineart_2_style true` |
| Formal | `--use_lineart_2_style advanced` |
| Dry Erase | `--use_lineart_2_style whiteboard` |
| **Professional Clean** | `--use_lineart_2_style modern_minimal` |
| Crayon | `--use_lineart_2_style storytelling` |

**Golpo Canvas** (richer, image-driven; needs `--use_2_0_style true`):

| Style | Flag |
|---|---|
| Chalkboard B/W (default) | `--image_style chalkboard_white` |
| Chalkboard Color | `--image_style neon` |
| Whiteboard | `--image_style whiteboard` |
| Modern Minimal | `--image_style modern_minimal` |
| Playful | `--image_style playful` |
| Technical | `--image_style technical` |
| Editorial | `--image_style editorial` |
| **Sharpie** | `--image_style marker` |

Add a drawing-cursor effect on Canvas: `--pen_style stylus|marker|pen`.

> Sketch and Canvas are mutually exclusive. Pick one engine per video.

## Voices

Default `solo-female-3`. Other choices: `solo-female-4`, `solo-male-3`,
`solo-male-4`. Voice quality adapts to the language you pick.

## Languages

44+ supported. Common codes: `en`, `hi`, `es`, `fr`, `de`, `it`, `pt`, `ja`,
`ko`, `zh`, `ar`, `bn`, `ta`, `ur`. See [references/languages.md](references/languages.md)
for the full list.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `requests_ok=false` | `pip3 install --user requests` |
| `ERROR: 401` | Bad API key — rotate: `golpo.py auth --key NEW --force` |
| `ERROR: 422` with `timing` | Pass timing as a string: `--timing 0.5`, not `0.5` |
| `ERROR: 422 script duration N min > timing M min` | Bump `--timing` higher than `N` |
| `ERROR: 429` | Rate-limited; cap parallel jobs at 3 |
| Job times out at 90 min | `--max_wait_seconds 10800` to extend further, or resume: `golpo.py status <JOB_ID>` |
| Document URL fails on 2nd use | Document URLs are single-use; re-upload |

## Costs

2 credits per minute of video, where 1 credit = $1 USD. So a 15-second video
costs ~$0.50 and a 1-minute video costs $2.

## Direct CLI use (without Claude)

The helper works as a standalone CLI too. After installing the plugin:

```bash
HELPER=~/.claude/plugins/golpo/skills/golpo/scripts/golpo.py

python3 "$HELPER" check
python3 "$HELPER" auth --key <KEY>
python3 "$HELPER" generate --prompt "Why is the sky blue?" --timing 0.5
python3 "$HELPER" list --limit 10
python3 "$HELPER" get <video_id>
```

See `python3 "$HELPER" --help` and `python3 "$HELPER" generate --help` for all
flags.

## Reference docs (read on demand)

- [`references/voices.md`](references/voices.md) — voice IDs
- [`references/styles.md`](references/styles.md) — full style matrix
- [`references/languages.md`](references/languages.md) — 44+ language codes
- [`references/bg_music.md`](references/bg_music.md) — background music
- [`references/full-payload.md`](references/full-payload.md) — every API field
