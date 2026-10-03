# ADR: Deterministic Guard and Optional Model Guard

Status: accepted for Phase 4 local prototype

## Decision

Use deterministic application controls as the mandatory guard layer:

- scope and privileged-business routing happen before provider invocation;
- server-selected corpus mode and retrieval determine canonical business facts;
- provider output is bounded and checked for unsafe clinical language,
  unsupported numbers, and forged source markers;
- sync and SSE use the same post-answer validation before persistence or output;
- session ownership, extraction confirmation, reset, image limits, provider
  timeout, and local request limits remain application responsibilities.

An external guard model/service is optional future work and is not installed,
called, or required for this phase. If introduced later, an unavailable or
ambiguous guard must fail closed and must not replace citation, price, tenant,
or clinical truth checks.

## Rationale

These decisions control authorization, provenance, and canonical facts at the
boundary where the application has the required data. A model guard can classify
language but cannot establish whether a citation was retrieved in this request,
whether a price is canonical, or whether a session owns an extraction.

## Consequences

The prototype has reproducible local tests and no new paid dependency. Residual
prompt-injection resistance and provider quality require a separately authorized
live evaluation. A shared rate limiter and formal authentication remain required
before a multi-instance or real-patient deployment.
