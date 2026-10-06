# ADR: LLM decisions with independent safety boundaries

Status: implemented in v2; live model effectiveness remains unvalidated.

The owner requested LLM-led conversation. We removed symbolic intent decisions from the
active route. Deterministic checks remain for authentication, range arithmetic, data
integrity and resource limits. These checks do not generate educational responses.

The guard integration follows `chacharin/llama-guard-layer`: separate safety model,
input/output directions, and screening at the application boundary. Direct mode uses
Llama Guard chat roles; output classification includes the original user request followed
by an assistant message. Service mode calls `/check` with message and direction.
The reviewed teacher guard.py blob was `40c849e67d5dd84d4473af20256abd33e92a08ef`.

We deliberately tighten the teacher example: malformed/missing verdicts, unknown category
syntax, timeouts and unavailable models fail closed. Direct mode rejects every reported
S1–S14 unsafe result, including specialized advice S6 and privacy S7. Teacher service mode
requires a valid direction/result/categories response and an empty category list for safe.
Configure the external service to block all categories required by this deployment; the
upstream example's configurable category exclusions must not silently weaken this policy.
Protect a remote service with an authenticated proxy if it does not implement the optional
Bearer token itself. Local string tripwires only cover a few obvious injection attempts.

Llama Guard is not a factuality detector. Citation IDs and structured observations are
checked in code, then a distinct LLM call checks support and prose-level field fidelity.
A same-model critic can share the generator's mistakes; evaluate it rather than treating
it as independent medical approval. Check follow-up suggestions as part of the output.
No unreviewed text is streamed; failures display an English operational message.

Sources: [teacher repository](https://github.com/chacharin/llama-guard-layer),
[Llama Guard 4 model card](https://huggingface.co/meta-llama/Llama-Guard-4-12B).
The model card does not establish equally reliable safety in every language. Maintain
language-specific tests, false-refusal review and adversarial evaluation before widening use.
