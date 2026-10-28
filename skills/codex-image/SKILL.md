---
name: codex-image
description: Generates or edits raster images (illustrations, concept art, UI mockups, sprites, icons, textures, photos, cutouts) with OpenAI Codex's built-in image generation, using the ChatGPT login Codex is signed into. Saves PNGs where the project needs them, runs batches in parallel, and cuts the sprite or icon sheets it generates into separate transparent files. Use when the user asks to create, draw, render, paint or edit an image, or a task needs bitmap assets such as a hero image, game sprites, item icons or textures. Sends the prompts and any reference images to OpenAI. Not for 3D models, or for vector and diagram assets (logos, UI icons, charts) better built as SVG, CSS or code.
license: MIT
compatibility: Needs the OpenAI Codex CLI on PATH (tested with codex-cli 0.164.0), signed in with a ChatGPT plan that includes image generation, Python 3.8 or later, and a shell to run the bundled scripts. slice_sheet.py also needs numpy and Pillow (scipy for overlapping subjects).
---

# Codex image generation

An agent that writes code can't draw, but Codex can: its built-in image tool runs on the
ChatGPT login Codex already has, so no API key is needed. Three scripts in this skill's
`scripts/` folder cover the work around it. Run them; there is no need to read them.

| Script | Use it for |
|---|---|
| `codex_image.py` | One image: runs `codex exec` read-only, has Codex make exactly one image, copies the PNG to `--out`. About 30-40 seconds. |
| `codex_batch.py` | Many images in parallel from a JSON list of jobs, with a shared style block, skip-if-exists, and a saved prompt beside each image. |
| `slice_sheet.py` | Cutting a generated sheet into one transparent PNG per subject, or one subject out of its background. |

## 1. Write a self-contained prompt

Codex sees only the prompt: not the conversation, not the project's files. Include:

- the subject, the style or medium, the composition, and the aspect ratio (square, landscape
  3:2, portrait 2:3);
- any text to render, exactly, in quotes;
- what to avoid: watermarks, captions, device frames, perspective mockups.

For a cutout (a sprite, an icon, an object), ask for a solid flat key colour that the subject
doesn't use, such as magenta `#FF00FF`, rather than a transparent background. A requested
transparent background often comes back opaque. `slice_sheet.py` removes either.

## 2. Generate

**One image.** From a POSIX shell (macOS, Linux, Git Bash), pass the prompt on stdin with a
quoted heredoc so quotes inside it survive:

```bash
python "<skill folder>/scripts/codex_image.py" --out "assets/hero.png" - <<'EOF'
A watercolour lighthouse on a cliff at dusk, landscape 3:2, no text.
EOF
```

From PowerShell, pipe it in: `Get-Content prompt.txt | python <skill folder>/scripts/codex_image.py --out assets/hero.png -`.
`--out` must end in `.png`, and an existing file is kept unless you pass `--force`. Add
`--ref <image>` (repeatable) to attach images, and say in the prompt whether to edit them or
match their style. For an edit, list what must stay unchanged.

**A set or many images.** Write the jobs to a JSON file in the project, next to where the
images go (never inside this skill's folder), and run them, four at a time by default:

```json
{"style": "Flat game-icon style, bold shapes, soft shading, solid magenta (#FF00FF) background, no text.",
 "jobs": [{"out": "assets/icons/sword.png", "prompt": "An iron sword."},
          {"out": "assets/icons/shield.png", "prompt": "A round wooden shield.", "refs": ["ref/style.png"]}]}
```

`python "<skill folder>/scripts/codex_batch.py" jobs.json` prints ok, skip or FAIL per job and
exits 1 if any failed. Run it again to retry only the failures. The `style` text goes in
front of every prompt word for word, which is what keeps a set matching.

**Small matching items** (icons, items, sprites) can share one sheet instead: up to 9
subjects in a grid ("a 3x3 grid of nine separate icons with wide empty gaps between them,
on solid magenta"), then cut it:

```bash
python "<skill folder>/scripts/slice_sheet.py" sheet.png assets/icons --rows 3 --cols 3 --names a,b,c,d,e,f,g,h,i --size 256
```

Codex ignores requested padding and cell sizes, so the script cuts at the empty gutters it
finds. It exits 1 and names the problem when subjects touch or a cell is empty; regenerate
the sheet then. A rerun is usually cheaper than repairing a bad image. Each call uses the
user's ChatGPT quota, so ask before a large batch.

## 3. Check the result

Success is exit 0 with the saved path printed. Then open the image and look at it. Check it
against the request (subject, text, aspect, background) before using it or calling the task
done.

- **Size**: the pixel size isn't under prompt control. Square came back as 1024x1024 or
  1254x1254, and 3:2 as 1536x1024. Resize afterwards when the project needs an exact size.
- **Scale and position** are loose: one requested position came back 76 pixels off, and a
  requested 4x scale came back 4.5x. Measure the result instead of trusting the prompt. To
  pin a layout, send a canvas with real pixels in place as a `--ref` to edit.
- **Edits** redraw the whole image. Regions it was told to keep come back with slight colour
  drift (3-7 levels of 255). When exact pixels matter, paste the originals back.
- **Pixel art** comes back as a large image of painted pixels, not true low-resolution art.
  Downscale it with nearest-neighbour resampling to the pixel size you measure.
- **Key-colour edges** keep a faint tint of the key colour after cutting. Choose a key close
  to the final background when that shows.

## When it fails

- Exit 1 with "Codex produced no image": stderr carries Codex's last message and any error
  events. That is usually a content refusal (rephrase the prompt) or a login or usage-limit
  error. Report those to the user, who can run `codex login`.
- "codex CLI not found on PATH": Codex isn't installed, or not on this shell's PATH.
- Codex keeps every original under `~/.codex/generated_images/<thread id>/` (or under
  `$CODEX_HOME` when that is set), so nothing is lost if the copy step fails.
