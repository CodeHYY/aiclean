# aiclean

Scan and safely clean local caches left behind by AI coding tools —
Claude Code, Cursor, VSCode, Ollama, npm/pnpm/yarn, uv/pip, HuggingFace,
PyTorch, Playwright, Hermes, and more.

AI dev tools are notorious for quietly eating disk space: Ollama models,
Claude Code project logs, HuggingFace model caches, browser binaries for
test automation... it adds up to tens of gigabytes without anyone noticing.
`aiclean` finds it, shows you exactly where it is, and only deletes what
you explicitly confirm.

## Install

```bash
pip install aiclean
# or run without installing:
pipx run aiclean
```

## Usage

```bash
# Scan only (read-only, safe to run anytime)
aiclean

# See all known cache locations this tool checks
aiclean --list

# Preview what would be deleted (no changes made)
aiclean --clean --dry-run

# Interactively confirm each cache before deleting
aiclean --clean

# Clean specific targets without prompts (careful!)
aiclean --clean --only ollama-models npm-cache --yes
```

### Example output

```
      SIZE  NAME                     PATH
----------------------------------------------------------------------
    12.4GB  ollama-models            /Users/you/.ollama/models
     3.1GB  claude-code-projects     /Users/you/.claude/projects
     1.8GB  huggingface-cache        /Users/you/.cache/huggingface
   420.0MB  npm-cache                /Users/you/.npm
   180.2MB  uv-cache                 /Users/you/.cache/uv
----------------------------------------------------------------------
    17.9GB  TOTAL (5 caches found)

Run with --clean to interactively remove caches (add --dry-run to preview safely).
```

## Safety

- Scan mode never touches the filesystem — it only computes sizes.
- `--clean` without `--yes` asks per-target before deleting anything.
- `--dry-run` combined with `--clean` shows exactly what would be removed,
  with zero deletions.
- Targets are well-known, documented cache directories only — aiclean never
  does a generic recursive delete of arbitrary paths.

## What it scans for

Run `aiclean --list` for the full, current list. Broadly: editor/IDE
caches (Cursor, VSCode), AI coding agent caches (Claude Code, Hermes),
local model caches (Ollama, HuggingFace, PyTorch Hub), and package manager
caches (npm, pnpm, yarn, uv, pip) — since these are the biggest and most
overlooked space users of an AI-assisted dev setup.

## Contributing

Issues and PRs welcome — especially "please add support for X cache
location" requests, since that's exactly the kind of real-world signal
this project is looking for.

## Support this project

If `aiclean` saved you disk space, consider supporting development of
`aiclean-pro` (scheduled auto-clean, multi-machine fleet reports, more
targets): https://afdian.com/a/aicleandev

## License

MIT
