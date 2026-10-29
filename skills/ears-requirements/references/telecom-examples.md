# Telecom Examples

BSS/OSS and access-network requirements in EARS. API numbers are TM Forum Open APIs; confirm the release in scope before contract use. Process area names follow eTOM operations groupings.

## Fulfillment
| ID | Pattern | Requirement | API |
|---|---|---|---|
| FUL-001 | Event | When a product order passes validation, the order manager shall create service orders within 5 s. | TMF622, TMF641 |
| FUL-002 | Unwanted | If the service inventory query returns no available PON port at the serving FDH, then the order manager shall set the product order state to "held" with reason "no capacity". | TMF638, TMF639 |
| FUL-003 | State | While a product order is in "held" state, the order manager shall reject modification requests with HTTP 409. | TMF622 |
| FUL-004 | Complex | While the OLT is in maintenance mode, when a service activation request arrives, the activation manager shall queue the request until maintenance ends. | TMF640 |
| FUL-005 | Unwanted | If the OLT does not respond to an activation request within 30 s, then the activation manager shall resend the request up to 2 times at 30 s intervals. | TMF640 |
| FUL-006 | Unwanted | If the OLT does not respond to the final resend within 30 s, then the activation manager shall raise a fallout task. | TMF640 |

## Assurance
| ID | Pattern | Requirement | API |
|---|---|---|---|
| ASR-001 | Event | When the OLT reports loss of signal on a PON port, the assurance platform shall raise a critical alarm within 5 s. | TMF642 |
| ASR-002 | Event | When the assurance platform correlates 8 or more ONT LOS alarms on one PON port within 60 s, the assurance platform shall raise one feeder-fibre alarm. | TMF642 |
| ASR-006 | Event | When the assurance platform raises a feeder-fibre alarm, the assurance platform shall suppress the child ONT LOS alarms on that PON port. | TMF642 |
| ASR-003 | Complex | While a planned outage covers a PON port, when a customer reports a fault on that port, the trouble ticket system shall link the ticket to the outage record. | TMF621 |
| ASR-004 | Unwanted | If the alarm event hub is unreachable for 60 s, then the assurance platform shall buffer alarms locally for up to 24 h. | TMF642, TMF688 |
| ASR-005 | Event | When the alarm event hub becomes reachable after an outage, the assurance platform shall replay buffered alarms in original order. | TMF642, TMF688 |

## Billing
| ID | Pattern | Requirement | API |
|---|---|---|---|
| BIL-001 | Event | When a usage record arrives, the rating engine shall rate it within 15 min. | TMF635 |
| BIL-002 | Unwanted | If a usage record references an unknown product instance, then the rating engine shall route it to the suspense queue with error code. | TMF635, TMF637 |
| BIL-003 | Complex | Where prepaid charging is licensed, when the balance reaches zero, the charging system shall block the session. | TMF654 |

## Non-functional
| ID | Pattern | Requirement |
|---|---|---|
| NFR-001 | Ubiquitous | The order manager shall acknowledge 95 % of product orders within 2 s at 200 orders per minute. |
| NFR-002 | State | While the primary data centre is unavailable, the order manager shall accept new orders at the secondary site within 15 min (RTO). |
| NFR-003 | Ubiquitous | The customer portal shall be available 99.9 % per calendar month, excluding notified maintenance windows. |

## Rewrites from real RFP prose
| Before | Defect | After |
|---|---|---|
| The system should support fast provisioning. | E001, E101, E103, E106 | When a product order passes validation, the order manager shall complete service activation within 10 min for 95 % of orders. |
| Alarms must be handled appropriately and escalated if needed. | E001, E101, E006 | When a critical alarm remains unacknowledged for 15 min, the assurance platform shall page the on-call NOC engineer. |
| Invalid orders will be rejected and logged. | E001, E104, E006 | If a product order fails schema validation, then the order manager shall reject it with an HTTP 400 response that names the failing field. |

## Traceability fields for TMF work
- Source: RFP clause, regulation, or stakeholder.
- Process: eTOM L2 or L3 process.
- Function: Functional Framework (GB929) function. Mark "verify" until checked against the release in scope.
- API: TMF Open API number and resource.
- Verification: test, inspection, analysis, or demonstration.
