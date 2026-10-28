"""Generate one image with OpenAI Codex's built-in image_gen tool and copy it to --out.

Runs `codex exec` on the ChatGPT login Codex is signed into; no OPENAI_API_KEY. Codex saves
each generated image under $CODEX_HOME/generated_images/<thread_id>/, and `exec --json` does
not emit the image item, so the thread id from the `thread.started` event is the only handle
on the output.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

INSTRUCTIONS = """\
Call your built-in image_gen tool exactly once for the request below, then reply DONE.
Pass every detail of the request through to image_gen; do not simplify it. Do not run shell
commands or read or write files: the caller collects the image from Codex's default save
location.
"""
REFS_NOTE = ("The attached image(s) are inputs to this request: edit them or use them as "
             "references, as the request says.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path, help="destination .png path")
    ap.add_argument("--ref", action="append", default=[], type=Path,
                    help="image to edit or use as a reference (repeatable)")
    ap.add_argument("--force", action="store_true", help="overwrite --out if it exists")
    ap.add_argument("--timeout", type=int, default=900, help="seconds (default 900)")
    ap.add_argument("--prompt-file", type=Path,
                    help="read the request from this UTF-8 file instead of the argument")
    ap.add_argument("prompt", nargs="?", help="the image request, or - to read it from stdin")
    args = ap.parse_args()

    if (args.prompt is None) == (args.prompt_file is None):
        sys.exit("error: give the request as an argument, as - for stdin, or with --prompt-file")
    if args.prompt_file:
        # utf-8-sig: Windows editors and PowerShell often start the file with a BOM.
        try:
            prompt = args.prompt_file.read_text(encoding="utf-8-sig")
        except OSError as exc:
            sys.exit(f"error: cannot read --prompt-file: {exc}")
    elif args.prompt == "-":
        sys.stdin.reconfigure(encoding="utf-8")
        prompt = sys.stdin.read()
    else:
        prompt = args.prompt
    if not prompt.strip():
        sys.exit("error: empty prompt")
    out = args.out.resolve()
    if out.suffix.lower() != ".png":
        sys.exit(f"error: Codex outputs PNG; --out must end in .png (got {out.name})")
    if out.exists() and not args.force:
        sys.exit(f"error: {out} exists; pass --force to overwrite or choose another name")
    for ref in args.ref:
        if not ref.is_file():
            sys.exit(f"error: reference image not found: {ref}")
    codex = shutil.which("codex")
    if not codex:
        sys.exit("error: codex CLI not found on PATH")

    cmd = [codex, "exec", "--json", "--skip-git-repo-check", "-s", "read-only",
           # Codex only relays the prompt to image_gen; the configured default effort
           # would add minutes of reasoning for nothing.
           "-c", 'model_reasoning_effort="low"',
           # A neutral cwd keeps project AGENTS.md files out of Codex's context.
           "-C", tempfile.gettempdir()]
    for ref in args.ref:
        cmd += ["-i", str(ref.resolve())]
    # Prompt on stdin: given no stdin of its own, exec reads the inherited pipe and blocks
    # forever when the caller's stdin never closes (as in Claude Code's Bash tool).
    cmd.append("-")
    full_prompt = INSTRUCTIONS + (REFS_NOTE if args.ref else "") + "\nRequest:\n" + prompt

    try:
        proc = subprocess.run(cmd, input=full_prompt, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        sys.exit(f"error: codex exec timed out after {args.timeout}s")

    thread_id, messages, errors = None, [], []
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "thread.started":
            thread_id = event.get("thread_id")
        elif kind == "item.completed" and event.get("item", {}).get("type") == "agent_message":
            messages.append(event["item"].get("text", ""))
        elif kind in ("error", "turn.failed"):
            errors.append(line)

    images = []
    if thread_id:
        codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
        images = sorted((codex_home / "generated_images" / thread_id).glob("*.png"),
                        key=lambda p: p.stat().st_mtime)
    if not images:
        print(f"error: Codex produced no image (exit {proc.returncode}, thread {thread_id})",
              file=sys.stderr)
        for text in errors + messages[-1:] + proc.stderr.strip().splitlines()[-10:]:
            print("  codex: " + text, file=sys.stderr)
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(images[0], out)
    print(out)
    for extra in images[1:]:
        print(f"note: Codex made an extra image, left at {extra}", file=sys.stderr)


if __name__ == "__main__":
    main()
