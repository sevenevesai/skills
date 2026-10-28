"""Generate many images in parallel with codex_image.py, from a JSON list of jobs.

Usage: python codex_batch.py JOBS.json [--parallel 4] [--force]

JOBS.json is either a list of jobs or an object {"style": "...", "jobs": [...]}. A job is
{"out": "assets/icons/potion.png", "prompt": "...", "refs": ["optional/ref.png"]}. A top-level
"style" is put in front of every prompt word for word, which is what keeps a set matching.
Relative paths resolve against the folder you run from.

Each job's full prompt is saved beside its image as <out>.prompt.txt, so a result can be traced
back to exactly what was asked. A job whose image already exists is skipped unless --force.
Prints one line per job (ok, skip or FAIL with Codex's last error lines) and exits 1 when any
job failed; rerun the same command to retry only the failures.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GENERATOR = Path(__file__).resolve().parent / "codex_image.py"
# Earlier batch tools around codex_image.py ran 4 to 6 calls at once. Each call is its own Codex
# thread with its own output folder, so calls never collide; the plan's rate limit is the cap.
DEFAULT_PARALLEL = 4


def load_jobs(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    style, jobs = ("", data) if isinstance(data, list) else (data.get("style", ""), data["jobs"])
    loaded = []
    for i, job in enumerate(jobs, 1):
        if not job.get("out") or not job.get("prompt"):
            raise ValueError(f"job {i} needs both 'out' and 'prompt'")
        prompt = (style.rstrip() + "\n\n" + job["prompt"]) if style else job["prompt"]
        loaded.append({"out": Path(job["out"]), "prompt": prompt, "refs": [Path(r) for r in job.get("refs", [])]})
    outs = [str(j["out"].resolve()) for j in loaded]
    if len(set(outs)) != len(outs):
        raise ValueError("two jobs write the same 'out' path")
    return loaded


def run_job(job: dict, force: bool) -> tuple[str, str]:
    out: Path = job["out"]
    if out.exists() and not force:
        return "skip", f"skip {out} (exists; --force to redo)"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_name(out.name + ".prompt.txt").write_text(job["prompt"], encoding="utf-8", newline="\n")
    cmd = [sys.executable, str(GENERATOR), "--out", str(out)]
    if force:
        cmd.append("--force")
    for ref in job["refs"]:
        cmd += ["--ref", str(ref)]
    cmd.append("-")
    result = subprocess.run(cmd, input=job["prompt"], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0 or not out.exists():
        tail = " | ".join(result.stderr.strip().splitlines()[-4:])
        return "fail", f"FAIL {out}: {tail}"
    return "ok", f"ok   {out}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("jobs", type=Path, help="JSON file of jobs")
    ap.add_argument("--parallel", type=int, default=DEFAULT_PARALLEL, help=f"concurrent calls (default {DEFAULT_PARALLEL})")
    ap.add_argument("--force", action="store_true", help="regenerate images that already exist")
    args = ap.parse_args()
    try:
        jobs = load_jobs(args.jobs)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        sys.exit(f"error: {args.jobs}: {exc}")
    with ThreadPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        results = list(pool.map(lambda j: run_job(j, args.force), jobs))
    for _, line in results:
        print(line)
    failed = sum(1 for status, _ in results if status == "fail")
    print(f"{len(jobs)} jobs: {len(jobs) - failed} done or skipped, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
