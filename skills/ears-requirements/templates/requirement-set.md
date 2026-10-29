# Requirement Set: <name>

- Scope: <system boundary, in and out>
- Release / baseline: <version, date>
- Owner: <name>
- Systems named: <list every system noun used as subject below>

## Requirements
| ID | Requirement | Pattern | Source | Verification | Notes |
|---|---|---|---|---|---|
| ABC-001 | When <trigger>, the <system> shall <response with value, unit, bound>. | event | <RFP clause / stakeholder / regulation> | test | |
| ABC-002 | If <fault trigger>, then the <system> shall <response>. | unwanted | | test | pairs with ABC-001 |

Pattern values: ubiquitous, event, state, unwanted, optional, complex.
Verification values: test, inspection, analysis, demonstration.

## Telecom traceability (optional)
| ID | eTOM process | Function (GB929) | Open API | Resource |
|---|---|---|---|---|
| ABC-001 | | verify | TMFxxx | |

## Review log
| ID | Rule | Finding | Fix | Status |
|---|---|---|---|---|
