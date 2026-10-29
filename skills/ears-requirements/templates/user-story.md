# Story: <ID> <short title>

- As a <role>, I want <capability>, so that <benefit>.
- Source: <stakeholder, RFP clause, ticket>
- Systems named: <every system used as a subject below>

## Acceptance criteria (EARS)
| ID | Requirement | Pattern | Verification |
|---|---|---|---|
| <ID>.1 | While <state>, when <trigger>, the <system> shall <one response with bound>. | complex | test |
| <ID>.2 | When <trigger>, the <system> shall <response>. | event | test |
| <ID>.3 | If <fault>, then the <system> shall <response>. | unwanted | test |

## Scenarios (optional, derived)
- <ID>.1 Given <state with concrete data>, when <trigger with concrete data>, then <observable result>.

## Example: CPQ quote revision
- As an account manager, I want to revise an approved quote, so that the customer gets the corrected price without a new deal record.

| ID | Requirement | Pattern | Verification |
|---|---|---|---|
| CPQ-010 | While a quote is in "approved" state, when the account manager changes the price, quantity, or discount of a quote item, the CPQ system shall create a new quote version. | complex | test |
| CPQ-011 | When the CPQ system creates a new version of an approved quote, the CPQ system shall set that version's approval state to "pending". | event | test |
| CPQ-012 | When the CPQ system creates a new version of an approved quote, the CPQ system shall set the previous version to "superseded". | event | test |
| CPQ-013 | If the CPQ system fails to create the new quote version, then the CPQ system shall keep the approved version unchanged. | unwanted | test |

- CPQ-010 Given quote Q at version N in "approved" state, when the account manager changes item 1 price from 100 to 90, then version N+1 exists and version N is unchanged.
