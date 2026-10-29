#!/usr/bin/env python3
"""Lint requirements against the EARS ruleset (Mavin et al., RE'09).

Input:
  .md   requirements in table cells under a header named Requirement, EARS,
        Text, Statement, or After; or bullet lines "- Text: ...".
  other one requirement per line; "#" lines skipped; leading IDs stripped.
  -     read stdin as plain text.

Suppress a justified warning inside the requirement: "ears-ignore: E006,E101".

Exit codes: 0 clean, 1 FAIL found (or WARN with --strict), 2 usage or no input.
Stdlib only. Rule IDs are documented in references/anti-patterns.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

TEXT_HEADERS = ("requirement", "ears", "text", "statement", "after", "acceptance criteria")
ID_RE = re.compile(r"^\s*(?:[-*]\s+)?(?:\*\*)?([A-Za-z][A-Za-z0-9]*-[A-Za-z0-9.-]*\d[A-Za-z0-9.-]*)(?:\*\*)?\s*[:.)\]]?\s+")
BULLET_TEXT_RE = re.compile(r"^\s*[-*]\s*(?:\*\*)?text(?:\*\*)?\s*:\s*(?:\*\*)?\s*(.+)$", re.I)
IGNORE_RE = re.compile(r"\[?\s*ears-ignore\s*:\s*([A-Z0-9,\s]+?)\s*\]?\s*$", re.I)

SHALL = re.compile(r"\bshall\b", re.I)
KEYWORDS = {"where": 0, "while": 1, "when": 2, "if": 2}
KW_RE = re.compile(r"\b(where|while|when|if|then)\b", re.I)
MODAL_RE = re.compile(r"\b(should|will|must|may|can|needs? to)\b", re.I)

VAGUE = [
    "quickly", "fast", "rapidly", "promptly", "timely", "in a timely manner", "real-time", "real time",
    "user-friendly", "user friendly", "easy", "easily", "simple", "intuitive", "robust", "seamless",
    "seamlessly", "efficient", "efficiently", "flexible", "adequate", "adequately", "sufficient",
    "appropriate", "appropriately", "as appropriate", "as required", "as needed", "if needed",
    "if necessary", "where possible", "reasonable", "minimal", "optimal", "maximize", "minimize",
    "high performance", "highly available", "best", "state-of-the-art", "several", "various",
    "approximately", "normally", "typically",
]
VAGUE_RE = re.compile(r"\b(" + "|".join(re.escape(v) for v in sorted(VAGUE, key=len, reverse=True)) + r")\b", re.I)
PLACEHOLDER_RE = re.compile(r"(\bTBD\b|\bTBC\b|\bTBA\b|\betc\b\.?|\band/or\b|\?\?\?|\bXX+\b)", re.I)
WEAK_RE = re.compile(r"\bshall\s+(support|allow|enable|facilitate|be able to|be capable of|provide the ability|provide the capability)\b", re.I)
PASSIVE_RE = re.compile(r"\bshall\s+(?:not\s+)?be\s+([a-z]+(?:ed|en))\b", re.I)
NEG_RE = re.compile(r"\bshall\s+not\b", re.I)
GENERIC_SUBJECT_RE = re.compile(r"(?:^|,\s*|\bthen\s+)(?:the\s+)?(system|solution|platform|application|software|it)\s*$", re.I)
CONJ_RE = re.compile(r"\b(and|or)\b(?!\s+(?:more|less|fewer|later|earlier|greater|equal|above|below))", re.I)
QUANT_RE = re.compile(r"\b(any|all)\b(?!\s+of\s+the\s+following)", re.I)
POST_TRIGGER_RE = re.compile(r"\b(when|whenever|if|while)\b", re.I)


@dataclass
class Finding:
    rule: str
    level: str
    message: str


@dataclass
class Requirement:
    rid: str
    line: int
    text: str
    pattern: str = "unknown"
    ignore: set = field(default_factory=set)
    findings: list = field(default_factory=list)

    def add(self, rule: str, level: str, message: str) -> None:
        if rule not in self.ignore:
            self.findings.append(Finding(rule, level, message))


def clean(text: str) -> str:
    text = re.sub(r"[*`_]{1,3}", "", text)
    return re.sub(r"\s+", " ", text).strip().rstrip(".").strip()


def split_ignore(text: str) -> tuple[str, set]:
    m = IGNORE_RE.search(text)
    if not m:
        return text, set()
    rules = {r.strip().upper() for r in m.group(1).split(",") if r.strip()}
    return text[: m.start()].strip(), rules


def make(rid: str, line: int, raw: str) -> Requirement | None:
    raw, ignore = split_ignore(raw)
    text = clean(raw)
    if not text:
        return None
    return Requirement(rid=rid or f"L{line}", line=line, text=text, ignore=ignore)


def parse_markdown(lines: list[str]) -> list[Requirement]:
    reqs, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = [clean(c).lower() for c in line.strip().strip("|").split("|")]
            col = next((header.index(h) for h in TEXT_HEADERS if h in header), None)
            id_col = header.index("id") if "id" in header else None
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if col is not None and col < len(cells):
                    rid = clean(cells[id_col]) if id_col is not None and id_col < len(cells) else ""
                    req = make(rid, i + 1, cells[col])
                    if req:
                        reqs.append(req)
                i += 1
            continue
        m = BULLET_TEXT_RE.match(line)
        if m:
            rid = ""
            for back in range(i - 1, max(i - 6, -1), -1):
                h = re.match(r"^#+\s*([A-Za-z][A-Za-z0-9]*-[A-Za-z0-9.-]+)", lines[back])
                if h:
                    rid = h.group(1)
                    break
            req = make(rid, i + 1, m.group(1))
            if req:
                reqs.append(req)
        i += 1
    return reqs


def parse_plain(lines: list[str]) -> list[Requirement]:
    reqs = []
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        rid, body = "", line
        m = ID_RE.match(line)
        if m:
            rid, body = m.group(1), line[m.end():]
        else:
            body = re.sub(r"^\s*[-*]\s+", "", line)
        req = make(rid, n, body)
        if req:
            reqs.append(req)
    return reqs


def classify(kws: list[str]) -> str:
    present = {k for k in kws if k != "then"}
    if not present:
        return "ubiquitous"
    if len(present) > 1:
        return "complex"
    return {"where": "optional", "while": "state", "when": "event", "if": "unwanted"}[present.pop()]


def lint_wording(req: Requirement, t: str) -> None:
    for m in VAGUE_RE.finditer(t):
        req.add("E101", "WARN", f"Vague term '{m.group(1)}'. Replace with a value, unit, and bound.")
    for m in PLACEHOLDER_RE.finditer(t):
        req.add("E102", "WARN", f"Placeholder '{m.group(1)}'. Resolve before baseline.")
    m = re.search(r"\b(?:should|must|will)\s+(support|allow|enable|facilitate|be able to)\b", t, re.I)
    if m:
        req.add("E103", "WARN", f"Weak verb '{m.group(1)}'. State the observable behaviour.")


def lint(req: Requirement) -> None:
    t = req.text
    shalls = list(SHALL.finditer(t))
    if not shalls:
        modal = MODAL_RE.search(t)
        hint = f' Found "{modal.group(1)}"; EARS uses "shall".' if modal else ""
        req.add("E001", "FAIL", "No 'shall'." + hint)
        lint_wording(req, t)
        m = re.match(r"^\s*(?:the\s+)?(system|solution|platform|application|software)\b", t, re.I)
        if m:
            req.add("E106", "WARN", f"Generic subject '{m.group(1)}'. Name the system or component.")
        return
    if len(shalls) > 1:
        req.add("E005", "WARN", f"{len(shalls)} 'shall' clauses. Split into atomic requirements.")
    pre, post = t[: shalls[0].start()], t[shalls[0].end():]
    kws = [m.group(1).lower() for m in KW_RE.finditer(pre)]
    req.pattern = classify(kws)

    if "if" in kws and "then" not in kws:
        req.add("E002", "FAIL", "'If' without 'then'.")
    if kws.count("when") > 1 or kws.count("if") > 1:
        req.add("E003", "FAIL", "More than one trigger. Split, or convert one to a 'While' state.")
    if "then" in kws and "if" not in kws:
        req.add("E009", "WARN", "'then' without 'If' (WHEN...THEN tool form). Mavin uses 'then' only in unwanted behaviour.")
    if "when" in kws and "if" in kws:
        req.add("E007", "WARN", "'When' and 'If' together. Normal event: When. Fault: If.")

    ranks = [KEYWORDS[k] for k in kws if k in KEYWORDS]
    starts_kw = bool(re.match(r"^\s*(where|while|when|if)\b", pre, re.I))
    if ranks and (ranks != sorted(ranks) or not starts_kw):
        req.add("E004", "FAIL", "Clause order. Use: Where, While, When or If, then the <system> shall.")
    if "then" in kws and "if" in kws and kws.index("then") < kws.index("if"):
        req.add("E004", "FAIL", "'then' before 'If'.")

    trig = POST_TRIGGER_RE.search(post)
    if trig:
        req.add("E008", "WARN", f"'{trig.group(1)}' after 'shall'. Move the condition before the system name.")
    if CONJ_RE.search(post.replace("and/or", "")):
        req.add("E006", "WARN", "Response joined by 'and'/'or'. Split unless one atomic action.")

    lint_wording(req, t)
    m = QUANT_RE.search(t)
    if m:
        req.add("E107", "WARN", f"Unbounded quantifier '{m.group(1)}'. Define the set it covers.")
    m = WEAK_RE.search(t)
    if m:
        req.add("E103", "WARN", f"Weak verb 'shall {m.group(1)}'. State the observable behaviour.")
    m = PASSIVE_RE.search(t)
    if m:
        req.add("E104", "WARN", f"Passive 'shall be {m.group(1)}'. Keep the system as actor.")
    if NEG_RE.search(t):
        req.add("E105", "WARN", "'shall not'. State what the system does instead, or define the test.")
    m = GENERIC_SUBJECT_RE.search(pre.strip())
    if m:
        req.add("E106", "WARN", f"Generic subject '{m.group(1)}'. Name the system or component.")


def lint_set(reqs: list[Requirement]) -> list[Finding]:
    events = sum(1 for r in reqs if r.pattern in ("event", "complex") and re.search(r"\bwhen\b", r.text, re.I))
    unwanted = sum(1 for r in reqs if re.search(r"^\s*(?:where\b.*?,\s*)?(?:while\b.*?,\s*)?if\b", r.text, re.I))
    if events and not unwanted:
        return [Finding("E201", "WARN", f"{events} event-driven and 0 unwanted-behaviour requirements. Write the fault cases.")]
    return []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lint requirements against EARS.")
    ap.add_argument("files", nargs="+", help="requirement files (.md, .txt) or - for stdin")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--quiet", action="store_true", help="print findings only, no pattern summary")
    args = ap.parse_args(argv)

    report, total_fail, total_warn = [], 0, 0
    for name in args.files:
        if name == "-":
            lines, md = sys.stdin.read().splitlines(), False
        else:
            path = Path(name)
            if not path.is_file():
                print(f"error: {name}: not found", file=sys.stderr)
                return 2
            lines, md = path.read_text(encoding="utf-8").splitlines(), path.suffix.lower() in (".md", ".markdown")
        reqs = parse_markdown(lines) if md else parse_plain(lines)
        if not reqs:
            print(f"error: {name}: no requirements found", file=sys.stderr)
            return 2
        for r in reqs:
            lint(r)
        set_findings = lint_set(reqs)
        fails = sum(f.level == "FAIL" for r in reqs for f in r.findings)
        warns = sum(f.level == "WARN" for r in reqs for f in r.findings) + len(set_findings)
        total_fail += fails
        total_warn += warns
        patterns: dict[str, int] = {}
        for r in reqs:
            patterns[r.pattern] = patterns.get(r.pattern, 0) + 1
        report.append({
            "file": name,
            "requirements": [{**{k: v for k, v in asdict(r).items() if k != "ignore"}} for r in reqs],
            "set_findings": [asdict(f) for f in set_findings],
            "patterns": patterns,
            "fail": fails,
            "warn": warns,
        })

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for f in report:
            for r in f["requirements"]:
                for x in sorted(r["findings"], key=lambda x: (x["level"] != "FAIL", x["rule"])):
                    print(f"{x['level']} {x['rule']} {f['file']}:{r['line']} {r['rid']}: {x['message']}")
            for x in f["set_findings"]:
                print(f"{x['level']} {x['rule']} {f['file']}: {x['message']}")
            if not args.quiet:
                dist = ", ".join(f"{k}={v}" for k, v in sorted(f["patterns"].items()))
                print(f"{f['file']}: {len(f['requirements'])} requirements, {f['fail']} FAIL, {f['warn']} WARN ({dist})")
    if total_fail or (args.strict and total_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
