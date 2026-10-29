# EARS Anti-Patterns and Linter Rules

Rule IDs match `scripts/ears_lint.py` output. FAIL breaks the ruleset. WARN degrades testability.

## Structure
| Rule | Level | Detects | Fix |
|---|---|---|---|
| E001 | FAIL | No "shall" | Rewrite with one system and "shall". "Should", "will", "must" are not EARS. |
| E002 | FAIL | "If" without "then" | Add "then" before the system clause. |
| E003 | FAIL | More than one trigger ("When" or "If" twice) | Split, or move one to a "While" state. |
| E004 | FAIL | Clauses out of order (When before While, keyword after "shall") | Reorder: Where, While, When or If, system, shall. |
| E005 | WARN | More than one "shall" | Split into atomic requirements. |
| E006 | WARN | Response joined by "and" or "or" after "shall" | Split, unless the actions are one atomic transaction. |
| E007 | WARN | "When" and "If" in the same requirement | Pick one. Normal event: When. Fault: If. |
| E008 | WARN | Condition word (when, if, while) after "shall" | Move the condition before the system name. |
| E009 | WARN | "then" without "If" (WHEN...THEN tool form) | Drop "then". Reserve it for unwanted behaviour. |

## Testability
| Rule | Level | Detects | Fix |
|---|---|---|---|
| E101 | WARN | Vague term (quickly, user-friendly, robust, seamless, as appropriate, etc.) | Replace with a value, unit, and bound. |
| E102 | WARN | Placeholder (TBD, TBC, etc., and/or) | Resolve before baseline. |
| E103 | WARN | Weak verb ("shall support", "shall be able to", "shall allow") | State the observable behaviour. |
| E104 | WARN | Passive response ("shall be logged") | Keep the system as actor: "the X shall log". |
| E105 | WARN | Negative response ("shall not") | State what the system does instead, or define the test. |
| E106 | WARN | Generic subject ("the system") | Name the system or component. |
| E107 | WARN | Unbounded quantifier (any, all). "each" and "every" pass: they distribute over a named set. | Define the set or the kind of change: "price, quantity, or discount of a quote item". |

## Set level
| Rule | Level | Detects | Fix |
|---|---|---|---|
| E201 | WARN | Event-driven requirements with no unwanted-behaviour requirement in the set | Write the fault cases. |

## Content defects the linter cannot see
- Missing fault pairing per requirement: E201 checks only that the set has some unwanted-behaviour lines, not that each event has one.
- Design leak: the response names a technology ("shall use Kafka") rather than a behaviour. Move it to a design constraint, labelled as such.
- Conflicting states: two requirements whose preconditions overlap with contradictory responses.
- Untraceable: no source (stakeholder, regulation, contract clause) and no verification method.
- Wrong subject: the user or operator as the actor. Requirements bind the system.

## Tool conventions (accept, do not require)
- Uppercase keywords (Kiro and spec-driven tools).
- WITHIN timing clause (some spec frameworks). Mavin EARS puts the bound in the response.
