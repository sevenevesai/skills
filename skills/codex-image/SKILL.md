---
name: codex-image
description: Generates or edits raster images (illustrations, concept art, UI mockups, sprites, icons, textures, photos, cutouts) with OpenAI Codex's built-in image generation, using the ChatGPT login Codex is signed into, and saves the PNG where the project needs it. Use when the user asks to create, draw, render, paint or edit an image, or a task needs a bitmap asset such as a hero image, a game sprite or a texture. Sends the prompt and any reference images to OpenAI. Not for 3D models, or for vector and diagram assets (logos, UI icons, charts) better built as SVG, CSS or code.
license: MIT
compatibility: Needs the OpenAI Codex CLI on PATH (tested with codex-cli 0.164.0), signed in with a ChatGPT plan that includes image generation, Python 3.8 or later, and a shell to run the bundled script.
---

# Codex image generation

An agent that writes code can't draw, but Codex can: its built-in image tool runs on the
ChatGPT login Codex already has, so no API key is needed. `scripts/codex_image.py` (relative to
this skill's folder) runs `codex exec` in a read-only sandbox, has Codex call its image tool
exactly once, and copies the PNG to `--out`. One image took about 30-40 seconds in testing.

## 1. Write a self-contained prompt

Codex sees only the prompt: not the conversation, not the project's files. Include:

- the subject, the style or medium, the composition, and the aspect ratio or size ("landscape
  3:2, about 1536x1024");
- any text to render, exactly, in quotes;
- "transparent background" when the asset needs alpha;
- what to avoid: watermarks, captions, device frames, perspective mockups.

For a matching set, repeat the shared style block word for word in every prompt.

## 2. Run the script

From a POSIX shell (macOS, Linux, Git Bash), pass the prompt on stdin with a quoted heredoc so
quotes inside it survive:

```bash
python "<skill folder>/scripts/codex_image.py" --out "assets/hero.png" - <<'EOF'
A watercolour lighthouse on a cliff at dusk, landscape 3:2, about 1536x1024, no text.
EOF
```

From PowerShell, pipe the prompt in: `Get-Content prompt.txt | python <skill folder>/scripts/codex_image.py --out assets/hero.png -`.
A short prompt can also be the last argument instead of `-`.

- `--out` must end in `.png`. Missing parent folders are created. The script refuses to
  overwrite an existing file unless you pass `--force`.
- Save project assets where the project keeps them, and previews in a temporary folder.
- `--ref <image>` (repeatable) attaches images. Say in the prompt whether to edit them ("Edit
  the attached image: ...") or use them as references ("Match the style of the attached
  image"). For an edit, list what must stay unchanged.
- One call makes one image. For variants or a set, make separate calls. Each call runs in its
  own Codex thread with its own output folder, so parallel calls are safe.
- Codex runs on the user's ChatGPT plan, so each call uses their quota. Ask before making a
  large batch.

## 3. Check the result

Success is exit code 0 with the saved path on stdout. Then open the PNG and look at it: check
it against the request (subject, text, size, alpha where asked) before using it or calling the
task done.

- An edit redraws the whole image. Regions it was told to keep come back with slight colour
  drift (3-7 levels of 255 in testing). When exact pixels matter, paste the originals back
  afterwards.
- Positions written in the prompt (pixel rows, percentages) are loose; one came back 76 pixels
  off. To pin a layout, put real pixels at those positions on the canvas you send for editing.
- Output is PNG only. Convert it afterwards if the project needs another format.

## When it fails

- Exit 1 with "Codex produced no image": stderr carries Codex's last message and any error
  events. That is usually a content refusal (rephrase the prompt) or a login or usage-limit
  error. Report those to the user, who can run `codex login`.
- "codex CLI not found on PATH": Codex isn't installed, or not on this shell's PATH.
- Codex keeps every original under `~/.codex/generated_images/<thread id>/` (or under
  `$CODEX_HOME` when that is set), so nothing is lost if the copy step fails.
