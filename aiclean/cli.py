"""aiclean — scan and safely clean local caches left by AI coding tools.

Covers: Claude Code, Cursor, VSCode extensions/cache, Ollama models,
npm/pnpm/yarn caches, uv/pip caches, Hermes, and other common AI dev tool
cache locations. Read-only scan by default; explicit --clean required to
delete anything, with dry-run preview and per-target confirmation.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


@dataclass
class Target:
    name: str
    path: Path
    description: str
    size_bytes: int = 0
    exists: bool = False


def _dir_size(path: Path, max_entries: int = 200_000) -> int:
    """Best-effort recursive size, capped to avoid pathological scans."""
    total = 0
    count = 0
    try:
        for root, dirs, files in os.walk(path, onerror=lambda e: None):
            for f in files:
                count += 1
                if count > max_entries:
                    return total
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    continue
    except OSError:
        return 0
    return total


def known_targets() -> list[Target]:
    home = Path.home()
    candidates = [
        ("claude-code-cache", home / ".claude" / "cache", "Claude Code local cache"),
        ("claude-code-projects", home / ".claude" / "projects", "Claude Code project session data (large logs)"),
        ("cursor-cache", home / "Library" / "Application Support" / "Cursor" / "Cache", "Cursor editor cache (macOS)"),
        ("cursor-cache-linux", home / ".config" / "Cursor" / "Cache", "Cursor editor cache (Linux)"),
        ("vscode-cachedata", home / "Library" / "Application Support" / "Code" / "CachedData", "VSCode cached data (macOS)"),
        ("vscode-cachedata-linux", home / ".config" / "Code" / "CachedData", "VSCode cached data (Linux)"),
        ("ollama-models", home / ".ollama" / "models", "Ollama downloaded models (often multi-GB)"),
        ("npm-cache", home / ".npm", "npm package cache"),
        ("pnpm-store", home / ".local" / "share" / "pnpm" / "store", "pnpm content-addressable store"),
        ("yarn-cache", home / "Library" / "Caches" / "Yarn", "Yarn cache (macOS)"),
        ("uv-cache", home / ".cache" / "uv", "uv (Python) package cache"),
        ("pip-cache", home / "Library" / "Caches" / "pip", "pip cache (macOS)"),
        ("pip-cache-linux", home / ".cache" / "pip", "pip cache (Linux)"),
        ("huggingface-cache", home / ".cache" / "huggingface", "HuggingFace model/dataset cache"),
        ("torch-hub-cache", home / ".cache" / "torch", "PyTorch hub cache"),
        ("playwright-cache", home / "Library" / "Caches" / "ms-playwright", "Playwright browser binaries (macOS)"),
        ("playwright-cache-linux", home / ".cache" / "ms-playwright", "Playwright browser binaries (Linux)"),
        ("hermes-cache", home / ".hermes" / "profiles", "Hermes profile caches (scans subdirs named 'cache')"),
    ]
    targets = []
    for name, path, desc in candidates:
        t = Target(name=name, path=path, description=desc)
        t.exists = path.exists()
        targets.append(t)
    return targets


def scan(targets: list[Target]) -> list[Target]:
    for t in targets:
        if t.exists:
            t.size_bytes = _dir_size(t.path)
    return targets


def print_report(targets: list[Target]) -> int:
    found = [t for t in targets if t.exists]
    if not found:
        print("No known AI tool caches found on this system.")
        return 0
    found.sort(key=lambda t: t.size_bytes, reverse=True)
    total = sum(t.size_bytes for t in found)
    print(f"{'SIZE':>10}  {'NAME':<24} PATH")
    print("-" * 70)
    for t in found:
        print(f"{human_size(t.size_bytes):>10}  {t.name:<24} {t.path}")
    print("-" * 70)
    print(f"{human_size(total):>10}  TOTAL ({len(found)} caches found)")
    return total


def clean(targets: list[Target], names: list[str] | None, dry_run: bool, yes: bool) -> None:
    found = [t for t in targets if t.exists and (not names or t.name in names)]
    if not found:
        print("Nothing to clean (no matching caches found).")
        return
    for t in found:
        label = f"[DRY RUN] would remove" if dry_run else "Removing"
        print(f"{label}: {t.name} ({human_size(t.size_bytes)}) at {t.path}")
        if dry_run:
            continue
        if not yes:
            resp = input(f"  Delete contents of {t.path}? [y/N] ").strip().lower()
            if resp != "y":
                print("  skipped")
                continue
        try:
            if t.path.is_dir():
                shutil.rmtree(t.path)
            else:
                t.path.unlink()
            print("  done")
        except OSError as e:
            print(f"  error: {e}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aiclean",
        description="Scan and clean local caches left by AI coding tools (Claude Code, Cursor, Ollama, npm/uv, etc).",
    )
    parser.add_argument("--clean", action="store_true", help="Delete caches instead of just scanning")
    parser.add_argument("--dry-run", action="store_true", help="With --clean, preview without deleting")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip per-target confirmation prompts")
    parser.add_argument("--only", nargs="*", help="Only operate on these target names (see --list)")
    parser.add_argument("--list", action="store_true", help="List known target names and exit")
    args = parser.parse_args(argv)

    targets = known_targets()

    if args.list:
        for t in targets:
            print(f"{t.name:<24} {t.description}")
        return 0

    scan(targets)

    if not args.clean:
        print_report(targets)
        print("\nRun with --clean to interactively remove caches (add --dry-run to preview safely).")
        return 0

    clean(targets, args.only, args.dry_run, args.yes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
