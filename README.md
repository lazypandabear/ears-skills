# ears-skills

EARS (Easy Approach to Requirements Syntax) skill for Hermes Agent and Claude. Writes, converts, and reviews requirements, with a stdlib Python linter. Format follows the Agent Skills standard, so the same folder loads in both agents.

Companion to [tmf-skills](https://github.com/lazypandabear/tmf-skills). Telecom examples map requirements to TM Forum Open APIs.

## Skills
| Skill | Covers | Load when |
|---|---|---|
| `ears-requirements` | Six EARS patterns, Mavin ruleset, user-story acceptance criteria, linter, telecom examples | Writing, converting, or reviewing requirements and acceptance criteria |

## Layout
```
skills/ears-requirements/SKILL.md                     # procedure, under 4k chars
skills/ears-requirements/references/patterns.md       # templates, ruleset, decision tree
skills/ears-requirements/references/anti-patterns.md  # linter rule IDs and content defects
skills/ears-requirements/references/telecom-examples.md
skills/ears-requirements/templates/requirement-set.md
skills/ears-requirements/templates/user-story.md      # story plus EARS acceptance criteria
skills/ears-requirements/scripts/ears_lint.py         # stdlib linter
scripts/validate.py                                   # Claude and Hermes skill rules
tests/test_ears_lint.py                               # linter regression tests
install.sh                                            # Hermes, Claude Code, claude.ai zips
```

## Install

### Hermes Agent
Option A. Tap this repo (updates via `hermes skills check` and `hermes skills update`):
```bash
hermes skills tap add lazypandabear/ears-skills
hermes skills install lazypandabear/ears-skills/skills/ears-requirements
```
Option B. External directory (git pull updates; no copy):
```yaml
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - ~/src/ears-skills/skills
```
Option C. Copy or symlink into a profile:
```bash
./install.sh --hermes                                   # default profile
./install.sh --hermes --hermes-home ~/.hermes-work      # another profile home
./install.sh --hermes --link                            # symlink instead of copy
```

### Claude Code
```bash
./install.sh --claude-code          # ~/.claude/skills/
```

### claude.ai
```bash
./install.sh --zip                  # dist/ears-requirements.zip
```
Upload the zip in claude.ai skills settings. The linter runs where code execution is available; the skill works as knowledge without it.

## Linter
```bash
python3 skills/ears-requirements/scripts/ears_lint.py requirements.md          # markdown tables
python3 skills/ears-requirements/scripts/ears_lint.py reqs.txt --strict        # one per line, fail on WARN
cat reqs.txt | python3 skills/ears-requirements/scripts/ears_lint.py - --json  # stdin, JSON
```
- Markdown: lints cells under a column named Requirement, EARS, Text, Statement, or After. ID comes from an ID column.
- Suppress a justified warning: append `ears-ignore: E006` to the requirement.
- Exit codes: 0 clean, 1 FAIL (or WARN with `--strict`), 2 usage error or no requirements found.

| Rule | Level | Check |
|---|---|---|
| E001 | FAIL | No "shall" |
| E002 | FAIL | "If" without "then" |
| E003 | FAIL | More than one trigger |
| E004 | FAIL | Clause order |
| E005 | WARN | More than one "shall" |
| E006 | WARN | Compound response (and/or) |
| E007 | WARN | "When" and "If" together |
| E008 | WARN | Condition after "shall" |
| E009 | WARN | "then" without "If" (Kiro WHEN...THEN form) |
| E101 | WARN | Vague term |
| E102 | WARN | Placeholder (TBD, etc., and/or) |
| E103 | WARN | Weak verb (support, allow, be able to) |
| E104 | WARN | Passive response |
| E105 | WARN | "shall not" |
| E106 | WARN | Generic subject ("the system") |
| E107 | WARN | Unbounded quantifier (any, all) |
| E201 | WARN | Set has event-driven but no unwanted-behaviour requirements |

## Design decisions
- One response per requirement. Stricter than Mavin, who allows one or many. Atomic requirements map one-to-one to tests.
- Uppercase keywords and WITHIN clauses are tool conventions (Kiro, spec-driven frameworks), not Mavin EARS. The linter is case-insensitive and does not require WITHIN.
- The linter checks syntax and wording. It cannot detect missing fault cases, design leaks, or conflicting states. The review procedure in SKILL.md covers those.
- Linter is heuristic regex, not a parser. Expect occasional false positives on E004 and E006; suppress with `ears-ignore` and a reason.

Validate before every push:
```bash
pip install pyyaml && python scripts/validate.py && python -m unittest discover -s tests
```

## Sources
- Mavin, Wilkinson, Harwood, Novak, "Easy Approach to Requirements Syntax (EARS)", IEEE RE'09: https://doi.org/10.1109/RE.2009.9
- Mavin, Wilkinson, "Big Ears", IEEE RE'10: https://doi.org/10.1109/RE.2010.39
- Mavin et al., "Listens Learned (8 Lessons Learned Applying EARS)", IEEE RE'16: https://doi.org/10.1109/RE.2016.38
- Official EARS site: https://alistairmavin.com/ears/
- QRA Corp, "When Not to Use EARS": https://qracorp.com/when-not-to-use-ears/
- Wikipedia summary: https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax
- Hermes Agent skills: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
# ears-skills
