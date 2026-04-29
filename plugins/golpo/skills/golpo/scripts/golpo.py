#!/usr/bin/env python3
"""Golpo CLI helper for the Claude Skill.

Subcommands:
  check                    Verify python/requests/api-key state.
  auth [--key K] [--force] Save API key to ~/.golpo/api_key (0600).
  upload <path>            Upload audio/document/image; print {file_url, ...}.
  generate <flags...>      Submit job, poll, print VIDEO_URL=<url> on success.
  status <job_id>          Print one status payload.
  get <video_id>           Print video metadata payload.
  list [--limit] [--offset] Print recent videos.

API key resolution: GOLPO_API_KEY env var -> ~/.golpo/api_key -> error.
"""

import argparse
import json
import os
import pathlib
import sys
import time
import warnings

warnings.filterwarnings("ignore", message=".*OpenSSL.*")

API_BASE = os.environ.get("GOLPO_API_BASE", "https://api.golpoai.com/api/v1")
KEY_PATH = pathlib.Path.home() / ".golpo" / "api_key"
TERMINAL_OK = {"completed", "ready", "done", "success", "finished"}
TERMINAL_FAIL = {"failed", "error", "errored", "cancelled", "canceled"}

GENERATE_FIELDS = {
    "prompt": str, "audio_clip": str, "voice_instructions": str,
    "new_script": str, "style": str, "language": str, "display_language": str,
    "bg_music": str, "video_type": str, "timing": "str_coerce",
    "audio_only": bool, "use_color": bool,
    "use_lineart_2_style": "str_coerce", "use_2_0_style": bool,
    "image_style": str, "pen_style": str, "show_pencil_cursor": bool,
    "pacing": str, "video_instructions": str, "just_return_script": bool,
    "include_watermark": bool, "logo": str, "logo_placement": str,
    "is_public": bool,
}
GENERATE_LIST_FIELDS = {
    "upload_urls": str, "input_images": str, "user_images": str,
    "user_images_descriptions": str, "user_videos": str,
    "user_videos_description": str,
    "use_as_is": bool, "skip_animation": bool, "user_audio_in_video": int,
}


def get_key():
    env = os.environ.get("GOLPO_API_KEY")
    if env:
        return env.strip()
    if KEY_PATH.exists():
        return KEY_PATH.read_text().strip()
    sys.stderr.write(
        "ERROR: No Golpo API key configured.\n"
        "  Run: python3 golpo.py auth --key <YOUR_KEY>\n"
        "  Or:  export GOLPO_API_KEY=<YOUR_KEY>\n"
    )
    sys.exit(2)


def save_key(key):
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(KEY_PATH.parent, 0o700)
    except OSError:
        pass
    KEY_PATH.write_text(key.strip() + "\n")
    os.chmod(KEY_PATH, 0o600)


def lazy_requests():
    try:
        import requests
        return requests
    except ImportError:
        sys.stderr.write(
            "ERROR: The 'requests' package is required.\n"
            "  Install: pip3 install --user requests\n"
        )
        sys.exit(3)


def api_request(method, path, json_body=None, files=None, data=None, stream=False):
    requests = lazy_requests()
    url = API_BASE + path
    headers = {"x-api-key": get_key()}
    if json_body is not None:
        headers["Content-Type"] = "application/json"
    try:
        r = requests.request(
            method, url, headers=headers,
            json=json_body, files=files, data=data,
            timeout=120, stream=stream,
        )
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"ERROR: network failure: {e}\n")
        sys.exit(4)

    if r.status_code == 401:
        sys.stderr.write(
            "ERROR: 401 Unauthorized. Your API key was rejected.\n"
            "  Re-run: python3 golpo.py auth --key <NEW_KEY> --force\n"
        )
        sys.exit(5)
    if r.status_code == 403:
        sys.stderr.write(
            "ERROR: 403 Forbidden. Your plan may not allow this action.\n"
        )
        sys.exit(6)
    if r.status_code == 429:
        sys.stderr.write(
            "ERROR: 429 Rate limited. Back off and retry.\n"
        )
        sys.exit(7)
    if r.status_code == 422:
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        sys.stderr.write("ERROR: 422 Validation failed:\n")
        sys.stderr.write(json.dumps(detail, indent=2) + "\n")
        sys.exit(8)
    if not r.ok:
        try:
            body = r.json()
        except Exception:
            body = r.text
        sys.stderr.write(f"ERROR: HTTP {r.status_code}: {body}\n")
        sys.exit(9)
    if stream:
        return r
    try:
        return r.json()
    except Exception:
        return {"raw": r.text}


def cmd_check(args):
    py_ok = sys.version_info >= (3, 8)
    try:
        import requests  # noqa: F401
        req_ok = True
    except ImportError:
        req_ok = False
    key_configured = bool(os.environ.get("GOLPO_API_KEY")) or KEY_PATH.exists()
    key_source = (
        "env" if os.environ.get("GOLPO_API_KEY")
        else ("file" if KEY_PATH.exists() else "none")
    )
    print(f"python_ok={'true' if py_ok else 'false'}")
    print(f"python_version={sys.version_info.major}.{sys.version_info.minor}")
    print(f"requests_ok={'true' if req_ok else 'false'}")
    print(f"key_configured={'true' if key_configured else 'false'}")
    print(f"key_source={key_source}")
    print(f"key_path={KEY_PATH}")
    print(f"api_base={API_BASE}")
    if not (py_ok and req_ok):
        sys.exit(1)


def cmd_auth(args):
    if KEY_PATH.exists() and not args.force:
        sys.stderr.write(
            f"API key already exists at {KEY_PATH}. Use --force to overwrite.\n"
        )
        sys.exit(1)
    key = args.key
    if not key:
        try:
            key = input("Enter your Golpo API key: ").strip()
        except EOFError:
            key = ""
    if not key:
        sys.stderr.write("ERROR: empty API key\n")
        sys.exit(1)
    save_key(key)
    print(f"Saved API key to {KEY_PATH} (0600).")


def cmd_upload(args):
    path = pathlib.Path(args.path).expanduser()
    if not path.is_file():
        sys.stderr.write(f"ERROR: file not found: {path}\n")
        sys.exit(1)
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 15:
        sys.stderr.write(
            f"ERROR: file is {size_mb:.1f} MB; Golpo upload limit is 15 MB.\n"
        )
        sys.exit(1)
    requests = lazy_requests()
    url = API_BASE + "/videos/upload-file"
    headers = {"x-api-key": get_key()}
    with path.open("rb") as f:
        files = {"file": (path.name, f)}
        try:
            r = requests.post(url, headers=headers, files=files, timeout=300)
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"ERROR: network failure: {e}\n")
            sys.exit(4)
    if not r.ok:
        try:
            body = r.json()
        except Exception:
            body = r.text
        sys.stderr.write(f"ERROR: HTTP {r.status_code}: {body}\n")
        sys.exit(9)
    out = r.json()
    print(json.dumps(out, indent=2))
    file_url = out.get("file_url") or out.get("upload_url")
    if file_url:
        print(f"FILE_URL={file_url}")


def coerce_value(name, raw):
    expected = GENERATE_FIELDS.get(name) or GENERATE_LIST_FIELDS.get(name)
    if expected is bool:
        if isinstance(raw, bool):
            return raw
        s = str(raw).strip().lower()
        if s in ("true", "1", "yes", "y"):
            return True
        if s in ("false", "0", "no", "n"):
            return False
        raise ValueError(f"--{name}: expected boolean, got {raw!r}")
    if expected is int:
        return int(raw)
    if expected == "str_coerce" or expected is str:
        if isinstance(raw, bool):
            return "true" if raw else "false"
        return str(raw)
    return raw


def build_generate_payload(args):
    payload = {}
    for name in GENERATE_FIELDS:
        v = getattr(args, name, None)
        if v is None:
            continue
        payload[name] = coerce_value(name, v)
    for name in GENERATE_LIST_FIELDS:
        vals = getattr(args, name, None)
        if not vals:
            continue
        payload[name] = [coerce_value(name, x) for x in vals]
    return payload


def cmd_generate(args):
    payload = build_generate_payload(args)
    if "prompt" not in payload and "audio_clip" not in payload:
        sys.stderr.write(
            "ERROR: at least one of --prompt or --audio_clip is required.\n"
            "  Note: Golpo requires --prompt even when audio_clip/new_script/upload_urls is also passed.\n"
        )
        sys.exit(1)
    if args.print_payload:
        print("PAYLOAD=" + json.dumps(payload))

    sub = api_request("POST", "/videos/generate", json_body=payload)
    job_id = sub.get("job_id")
    video_id = sub.get("video_id")
    if not job_id:
        sys.stderr.write(f"ERROR: response missing job_id: {sub}\n")
        sys.exit(10)
    print(f"JOB_ID={job_id}")
    if video_id:
        print(f"VIDEO_ID={video_id}")
    sys.stdout.flush()

    delay = 5.0
    deadline = time.time() + args.max_wait_seconds
    last_progress = -1
    while time.time() < deadline:
        st = api_request("GET", f"/videos/status/{job_id}")
        status = (st.get("status") or "").strip().lower()
        progress = st.get("progress")
        video_url = st.get("video_url")
        if progress is not None and progress != last_progress:
            print(f"progress={progress}% status={status}")
            last_progress = progress
            sys.stdout.flush()
        elif status:
            print(f"status={status}")
            sys.stdout.flush()
        if status in TERMINAL_OK or video_url:
            if not video_url and st.get("video_id"):
                meta = api_request("GET", f"/videos/{st['video_id']}")
                video_url = meta.get("video_url")
            if video_url:
                print(f"VIDEO_URL={video_url}")
                return
            sys.stderr.write(f"ERROR: status terminal but no video_url: {st}\n")
            sys.exit(11)
        if status in TERMINAL_FAIL:
            sys.stderr.write(f"ERROR: generation failed: {json.dumps(st)}\n")
            sys.exit(12)
        time.sleep(delay)
        delay = min(delay * 1.5, 30.0)
    sys.stderr.write(
        f"ERROR: timed out after {args.max_wait_seconds}s waiting for job {job_id}.\n"
        f"  Re-check later: python3 golpo.py status {job_id}\n"
    )
    sys.exit(13)


def cmd_status(args):
    out = api_request("GET", f"/videos/status/{args.job_id}")
    print(json.dumps(out, indent=2))


def cmd_get(args):
    out = api_request("GET", f"/videos/{args.video_id}")
    print(json.dumps(out, indent=2))
    if out.get("video_url"):
        print(f"VIDEO_URL={out['video_url']}")


def cmd_list(args):
    qs = []
    if args.limit is not None:
        qs.append(f"limit={args.limit}")
    if args.offset is not None:
        qs.append(f"offset={args.offset}")
    suffix = ("?" + "&".join(qs)) if qs else ""
    out = api_request("GET", f"/videos{suffix}")
    print(json.dumps(out, indent=2))


def add_generate_args(p):
    for name, t in GENERATE_FIELDS.items():
        if t is bool:
            p.add_argument(f"--{name}", default=None,
                           help="boolean: true|false")
        else:
            p.add_argument(f"--{name}", default=None)
    for name, _ in GENERATE_LIST_FIELDS.items():
        p.add_argument(f"--{name}", action="append", default=None,
                       help="repeatable; pass once per item")
    p.add_argument("--max_wait_seconds", type=int, default=1800,
                   help="poll cap (default 30 min)")
    p.add_argument("--print_payload", action="store_true",
                   help="echo the JSON payload before submitting")


def main():
    ap = argparse.ArgumentParser(
        prog="golpo.py",
        description="Golpo Video API helper for the Claude Skill.",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="report environment readiness").set_defaults(
        func=cmd_check)

    pa = sub.add_parser("auth", help="save API key to ~/.golpo/api_key")
    pa.add_argument("--key", help="API key value (else read from stdin)")
    pa.add_argument("--force", action="store_true",
                    help="overwrite existing key file")
    pa.set_defaults(func=cmd_auth)

    pu = sub.add_parser("upload", help="upload an audio/doc/image file")
    pu.add_argument("path", help="local file path (max 15 MB)")
    pu.set_defaults(func=cmd_upload)

    pg = sub.add_parser("generate", help="submit a video job and poll to completion")
    add_generate_args(pg)
    pg.set_defaults(func=cmd_generate)

    ps = sub.add_parser("status", help="check one job status")
    ps.add_argument("job_id")
    ps.set_defaults(func=cmd_status)

    pgv = sub.add_parser("get", help="fetch a video's metadata by id")
    pgv.add_argument("video_id")
    pgv.set_defaults(func=cmd_get)

    pl = sub.add_parser("list", help="list recent videos")
    pl.add_argument("--limit", type=int, default=None)
    pl.add_argument("--offset", type=int, default=None)
    pl.set_defaults(func=cmd_list)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
