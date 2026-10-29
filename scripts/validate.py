#!/usr/bin/env python3
"""Validate every skill against Claude (Agent Skills) and Hermes rules.

Claude: frontmatter keys limited to name, description, license, allowed-tools,
metadata, compatibility; kebab-case name up to 64 chars; description up to
1024 chars with no angle brackets; exactly one SKILL.md per skill.
Hermes: metadata.hermes.category present; referenced files exist (URL installs
copy only referenced files); body under ~24k chars (oversized-body lint).
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent / "skills"
ALLOWED = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
REF_RE = re.compile(r"`((?:references|templates|scripts|assets|examples)/[\w./-]+)`")
BODY_LIMIT = 24000

errors, warnings = [], []

for skill_dir in sorted(p for p in ROOT.iterdir() if p.is_dir()):
    name = skill_dir.name
    md = skill_dir / "SKILL.md"
    if not md.exists():
        errors.append(f"{name}: SKILL.md missing")
        continue
    if len(list(skill_dir.rglob("SKILL.md"))) != 1:
        errors.append(f"{name}: more than one SKILL.md")
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        errors.append(f"{name}: bad frontmatter")
        continue
    fm, body = yaml.safe_load(m.group(1)), m.group(2)
    extra = set(fm) - ALLOWED
    if extra:
        errors.append(f"{name}: disallowed keys {sorted(extra)} (put them under metadata)")
    if fm.get("name") != name:
        errors.append(f"{name}: name field '{fm.get('name')}' does not match directory")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append(f"{name}: invalid name")
    desc = str(fm.get("description", "")).strip()
    if not desc or len(desc) > 1024:
        errors.append(f"{name}: description missing or over 1024 chars")
    if "<" in desc or ">" in desc:
        errors.append(f"{name}: description contains angle brackets")
    if not (fm.get("metadata") or {}).get("hermes", {}).get("category"):
        errors.append(f"{name}: metadata.hermes.category missing")
    if len(body) > BODY_LIMIT:
        warnings.append(f"{name}: body {len(body)} chars exceeds {BODY_LIMIT}")
    for ref in REF_RE.findall(body):
        if not (skill_dir / ref).exists():
            errors.append(f"{name}: referenced file not found: {ref}")
    for f in skill_dir.rglob("*.md"):
        if f.name != "SKILL.md" and f"`{f.relative_to(skill_dir).as_posix()}`" not in body:
            warnings.append(f"{name}: {f.relative_to(skill_dir)} not referenced in SKILL.md (Hermes URL installs skip it)")
    print(f"ok  {name:28s} desc={len(desc):4d} body={len(body):5d}")

for w in warnings:
    print("WARN", w)
for e in errors:
    print("FAIL", e)
sys.exit(1 if errors else 0)
