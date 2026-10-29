---
name: ears-requirements
description: "EARS (Easy Approach to Requirements Syntax, Mavin, Rolls-Royce, RE'09). Use to write, convert, or review requirements and acceptance criteria: pick the pattern (ubiquitous, event, state, unwanted, optional, complex), enforce the ruleset, lint for vague or compound shall statements, and trace each one to a test."
license: MIT
compatibility: "Agent Skills standard. Works in Hermes Agent and Claude. Linter needs Python 3.9+ stdlib only; knowledge use needs no tools."
metadata:
  version: 1.0.0
  author: Dennis A. Garcia
  hermes:
    tags: [requirements, ears, acceptance-criteria, rfp, specification, testability]
    category: requirements
---

# EARS Requirements

## When to Use
- Write new requirements or acceptance criteria.
- Convert user stories, meeting notes, or RFP prose into EARS.
- Review a requirements set, RFP, or vendor response for testability.

## Ruleset (Mavin)
- Zero or many preconditions. Zero or one trigger. One system name. One or many responses.
- Clause order is fixed: `While` precondition, `When` trigger, `the <system> shall <response>`.
- House rule, stricter than Mavin: one response per requirement. Split the rest.

## Procedure
1. Name the system. One noun per requirement. No "the system" when several exist.
2. Pick the pattern with the decision tree in `references/patterns.md`.
   - Normal event: `When`. Fault, failure, misuse: `If ... then`. Never swap them.
3. Write the response with a measurable criterion: value, unit, bound, or observable state.
4. For every `When` requirement, ask what fails. Write the matching `If ... then`.
5. Fill `templates/requirement-set.md`: ID, text, pattern, source, verification method. User stories: `templates/user-story.md`; the story stays, EARS lines are its acceptance criteria.
6. Run the linter `scripts/ears_lint.py` (stdlib Python; rule IDs in `references/anti-patterns.md`):
   - `python3 scripts/ears_lint.py requirements.md` lints table cells under a Requirement column.
   - Plain text or `-` (stdin): one requirement per line.
   - `--strict` fails on warnings. `--json` for machine output.
   - Justified warning: append `ears-ignore: E006` to that requirement.
7. Fix every FAIL. Justify or fix every WARN in the review notes.
8. Telecom work: map each requirement to a TMF Open API and process using `references/telecom-examples.md`.

## Review mode
- Lint first. Then judge content the linter cannot see:
  - Missing unwanted-behaviour cases.
  - Responses that describe design, not behaviour.
  - Conflicting preconditions across requirements.
- Output: `| ID | Rule | Finding | Fix |` sorted FAIL then WARN.
- Judge outcome, not syntax. A clear non-EARS requirement beats a vague EARS one.

## Reference loading
- Hermes: `skill_view("ears-requirements", "references/patterns.md")`, same for `references/anti-patterns.md`, `references/telecom-examples.md`, `templates/requirement-set.md`, `templates/user-story.md`.
- Claude: read `references/patterns.md`, `references/anti-patterns.md`, `references/telecom-examples.md`, `templates/requirement-set.md`, `templates/user-story.md` in this skill's directory.

## Pitfalls
- Valid syntax with untestable content: "shall respond quickly". Add the number.
- `If/then` for normal events. Reserve it for unwanted behaviour.
- Two triggers in one requirement. Split, or move one to a `While` state.
- EARS for data models or interface specs. Use a schema or API spec; EARS covers behaviour.
- WITHIN clauses, all-caps keywords, WHEN...THEN (Kiro). Tool conventions, not Mavin EARS. Accept caps; flag WHEN...THEN (E009).
- "Any" or "all" with no defined set (E107). Name the items or the kind of change.

## Verification
- Linter exits 0.
- Every requirement has an ID, a source, and a verification method.
- Every event-driven requirement has a paired unwanted-behaviour requirement or a stated reason for none.
