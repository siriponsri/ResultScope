# Decision: Python controls, optional shadow models

Status: implemented in the current local prototype. Documentation reviewed 2026-10-04.

Python remains authoritative for scope, privileged business routing, source
selection, supplied-range arithmetic, extraction confirmation and output validation.
A model cannot grant itself authorization, invent a retrieved citation, change a
supplied range or convert synthetic business records into approved information.

JSON and SSE run the same answer-validation boundary. The SSE response is not a
raw-token bypass. Invalid output fails closed with sanitized stable error codes.
Logs must not include raw provider answers, keys, patient content or image bytes.

Every provider transport path reserves a persistent local attempt before HTTP.
`PROVIDER_NETWORK_ENABLED=false` blocks transport before reservation. Consumed,
failed and unfinished attempts are never refunded. The ledger does not reset when
the app restarts. Admin tests and model listing share the same accounting boundary.

SystemOne is a distinct optional shadow adapter. Its output does not override Python.
Clef is disabled. A future external guard requires its own contract and validation;
it cannot replace source-ID, URL, number, authorization or session checks.

This keeps essential decisions inspectable and testable. It does not prove live
model safety, defeat every prompt injection, or establish distributed cloud controls.
See [threat model](THREAT_MODEL.md) and [readiness](../operations/READINESS.md).
