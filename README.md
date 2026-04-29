# Golpo Skill for Claude Code

A Claude Code plugin that turns any conversation into a finished
[Golpo](https://video.golpoai.com) video. Give Claude a prompt, a script, an
audio narration, or a PDF — Claude submits the job, polls for completion, and
returns the video URL.

```text
You: "Make a 1-minute vertical video explaining photosynthesis with marker style and lofi music."
Claude: [submits → polls → renders] -> https://video.golpoai.com/v/...
```

## Install

### Via Claude Code marketplace (recommended)

```text
/plugin marketplace add golpoai/claude-skill
/plugin install golpo@GolpoSkill
```

(Replace `golpoai/claude-skill` with the actual GitHub `<org>/<repo>` once
this is hosted there. Until then, point it at this directory:
`/plugin marketplace add /Users/you/path/to/GolpoSkill`.)

### Manual

```bash
git clone https://github.com/golpoai/claude-skill.git ~/.claude/plugins/golpo
```

Restart Claude Code; the `golpo` skill will register automatically.

## First run

The skill needs a Golpo API key. Get one at
[video.golpoai.com](https://video.golpoai.com) (API tier — minimum $200 / 200
credits, $2/credit ≈ $2 per minute of video). On first invocation Claude will
ask for your key and save it to `~/.golpo/api_key` with `0600` permissions.

To rotate later:

```bash
python3 ~/.claude/plugins/golpo/skills/golpo/scripts/golpo.py auth --key NEW_KEY --force
```

To use an env var instead (overrides the file):

```bash
export GOLPO_API_KEY=...
```

## What you can ask Claude

| Ask | What happens |
|---|---|
| "Make a 30-second video about why the sky is blue." | Prompt-only generate, default voice / Sketch Classic. |
| "Turn this script into a vertical short with editorial style." | `--new_script` + `--video_type short` + Canvas Editorial. |
| "Use this audio file as narration: `/path/to/voice.mp3`." | `upload` then `--audio_clip <url>`. |
| "Summarize this PDF as a 1-minute video." | `upload` then `--upload_urls <url>` + `--timing 1`. |
| "Hindi narration, English on-screen text, marker style." | Canvas with `--language hi --display_language en --image_style marker`. |
| "List my last 5 videos." | `golpo.py list --limit 5`. |

You can also invoke the helper directly:

```bash
python3 ~/.claude/plugins/golpo/skills/golpo/scripts/golpo.py generate \
  --prompt "Why is the sky blue?" --timing 0.5 --video_type long
```

## Requirements

- Python 3.8+
- `pip install requests` (skill prompts you if missing)
- A Golpo API key (`https://video.golpoai.com`)

## File map

```
GolpoSkill/                          # marketplace root
├── .claude-plugin/
│   └── marketplace.json             # lists plugins in this repo
└── plugins/
    └── golpo/                       # plugin root
        ├── .claude-plugin/
        │   └── plugin.json          # plugin manifest
        └── skills/
            └── golpo/                # the skill
                ├── SKILL.md          # instructions Claude follows
                ├── scripts/
                │   ├── golpo.py      # CLI helper
                │   └── requirements.txt
                └── references/       # loaded on demand
                    ├── voices.md
                    ├── styles.md
                    ├── languages.md
                    ├── bg_music.md
                    └── full-payload.md
```

## Hosting your own copy

To host this so anyone can install it from your repo:

1. Push this directory to a public GitHub repo.
2. Tell users:
   ```
   /plugin marketplace add <your-gh-org>/<repo>
   /plugin install golpo@GolpoSkill
   ```
3. Bump `version` in `.claude-plugin/plugin.json` and
   `.claude-plugin/marketplace.json` together when shipping changes.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `requests_ok=false` from `check` | `pip3 install --user requests` |
| `ERROR: 401 Unauthorized` | Run `auth --key <NEW_KEY> --force`. |
| `ERROR: 422` with `timing` complaint | Pass timing as a string: `--timing 0.5`, not `0.5` (helper does this for you, but check). |
| `ERROR: 429 Rate limited` | Run ≤ 3 jobs in parallel; back off and retry. |
| Job times out at 30 min | Pass `--max_wait_seconds 5400` to extend, or resume later with `python3 .../golpo.py status <JOB_ID>`. |

## Links

- Golpo: https://video.golpoai.com
- API docs: https://video.golpoai.com/api-docs/endpoints/v1
- Payload examples: https://video.golpoai.com/guide/golpo-ai-video-api-payload-examples

## License

MIT.
