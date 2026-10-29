# EARS Patterns

Source: Mavin, Wilkinson, Harwood, Novak, "Easy Approach to Requirements Syntax (EARS)", IEEE RE'09, doi:10.1109/RE.2009.9. Keywords are case-insensitive.

## Templates
| Pattern | Keyword | Template |
|---|---|---|
| Ubiquitous | none | The `<system>` shall `<response>`. |
| Event-driven | When | When `<trigger>`, the `<system>` shall `<response>`. |
| State-driven | While | While `<precondition(s)>`, the `<system>` shall `<response>`. |
| Unwanted behaviour | If, then | If `<trigger>`, then the `<system>` shall `<response>`. |
| Optional feature | Where | Where `<feature is included>`, the `<system>` shall `<response>`. |
| Complex | combination | While `<precondition(s)>`, when `<trigger>`, the `<system>` shall `<response>`. |

## Ruleset
- Preconditions: zero or many. Combine with "and" inside one `While` clause.
- Trigger: zero or one.
- System name: exactly one.
- Response: one or many in Mavin. This skill requires one (house rule) for test traceability.
- Order: Where, While, When or If, system, shall, response.

## Decision tree
1. Is the behaviour active only when a feature is fitted or licensed? Start with `Where`.
2. Does it apply only during a state or mode? Add `While`.
3. Is it a response to a discrete event?
   - Wanted or normal event: `When`.
   - Fault, failure, timeout, invalid input, misuse: `If ... then`.
4. None of the above: ubiquitous.
5. More than one trigger? Split into separate requirements, or convert one trigger into a `While` state.

## Distinctions that reviewers get wrong
- Trigger vs precondition: a trigger is an instant (signal lost, order received). A precondition is a duration (in maintenance mode, while session active).
- `When` vs `If`: `When the order is received` is normal flow. `If the order fails schema validation, then` is unwanted. Using `If` for normal flow hides the fault set.
- `shall not`: valid but often untestable. Prefer the positive response the system takes instead.

## User story structure
EARS does not replace the story. The story records intent; EARS lines are its acceptance criteria. Template: `templates/user-story.md`.
| Layer | Form | Testable |
|---|---|---|
| Story | As a role, I want capability, so that benefit. | No |
| Acceptance criteria | One EARS line per observable behaviour. System is the subject. | Yes |
| Scenarios (optional, BDD) | Given/When/Then with concrete data, one or more per EARS line. | Yes |

Mapping: role becomes the Source field, never the subject. "I want" becomes event or ubiquitous lines. "So that" becomes the measurable bound. Context ("during outages", "if licensed") becomes While or Where. Add the If/then lines the story omits. More than about 8 criteria: split the story.

Gherkin from EARS: While maps to Given, When maps to When, "the system shall" maps to Then, with concrete values substituted.

## Conversion recipe (user story to EARS)
1. Strip role and benefit ("As a ..., so that ..."). Keep them as source, not requirement text.
2. Identify the system that acts. The user is never the subject.
3. Extract trigger and state from the story and its acceptance criteria.
4. Write one EARS line per observable behaviour.
5. Add the unwanted-behaviour lines the story omitted.

Example:
- Story: "As a field technician I want to see the ONT status so I can close the ticket."
- EARS: When the technician opens a trouble ticket, the field app shall display the ONT operational state within 3 s.
- EARS: If the ONT state query times out after 3 s, then the field app shall display "state unavailable" and the timestamp of the last known state.

## Non-functional requirements
- Use ubiquitous or state-driven form with a measured bound.
- The order manager shall acknowledge 95 % of product orders within 2 s at 200 orders per minute.
- While the primary site is unavailable, the billing system shall rate usage records with no more than 15 min backlog.

## Further reading
- Mavin, Wilkinson, "Big Ears (The Return of Easy Approach to Requirements Engineering)", RE'10, doi:10.1109/RE.2010.39.
- Mavin et al., "Listens Learned (8 Lessons Learned Applying EARS)", RE'16, doi:10.1109/RE.2016.38.
- Official site: https://alistairmavin.com/ears/
- QRA Corp, "When Not to Use EARS": https://qracorp.com/when-not-to-use-ears/
