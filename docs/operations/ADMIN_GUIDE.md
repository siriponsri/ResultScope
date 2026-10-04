# Local administrator guide

Provider settings are an explicitly enabled **local demonstration surface**. Ordinary workspace use has no administrator sign-in step. The settings screen is not a patient account system or an approved cloud administration console.

## Open the settings screen

Start with [local setup](LOCAL_SETUP.md), set `LOCAL_DEMO_MODE=true` in the local process, keep `APP_ENV=development`, and retain `PROVIDER_NETWORK_ENABLED=false`. Bind the server to `127.0.0.1` and open `/admin/login`.

If no custom password hash is configured, the local-demo fallback is `admin` / `1234`. Never expose it online. Outside the allowed local environment, the administration routes return unavailable. Login attempts are rate limited. Admin sessions use an HttpOnly cookie and CSRF protection for writes; they are held in the server process and expire.

## Understand the provider slots

| Slot | Default integration | Role |
|---|---|---|
| LLM | OpenTyphoon LLM | Generate educational explanation text after local checks and retrieval |
| OCR | Typhoon OCR | Extract a laboratory image through a separate request contract |
| SystemOne | OpenThai-SystemOne through iApp | Optional typed decision observer, shadow-only |

The catalog includes compatibility choices, but availability of a catalog entry is not proof that this candidate has passed a live test or that an account has access. The current chat path requires the supported OpenAI-compatible contract; the presence of a native-protocol catalog entry does not automatically add it to that path. SystemOne never replaces the Python scope decision or output validator.

## Save or change settings

1. Select an allowlisted provider and model for the intended slot.
2. Review the timeout; the form accepts 1–300 seconds.
3. Leave **Replace key** blank to retain the stored key. To replace it, enter a new key in the password field.
4. Use **Delete key** to mark a key for removal, then **Save settings** to apply the change.
5. Read the status message. Saving does not call a provider.

Do not paste secrets into prompts, reports, issues, screenshots, or source files. A saved key is not returned to the browser; the screen reports configured/not configured state. Provider URLs come from the server catalog.

Changes remain local. `services/provider_config.py` persists encrypted values to the configured local settings file, with a configured storage key or a locally generated key file. Those files are ignored by Git. This is not an approved cloud secret vault and does not encrypt the conversation database.

## Test without using a provider

**Test with mock** sends `live: false` to the shared adapter test endpoint. It checks the mock contract without an outbound provider request or attempt reservation. Tests are separate from saving and are rate limited. They use the saved configuration, so save intended changes before testing them.

A terminal equivalent is:

```powershell
$env:PROVIDER_NETWORK_ENABLED = "false"
python scripts/provider_verification_runner.py
```

Do not add `--live` for this workflow. A mock pass does not validate account access, quota, provider quality, or production readiness.

## Important operating boundaries

- The global provider guard is the reliable offline control. The per-slot **enabled** checkbox is not a substitute: compatible runtime paths can fall back to existing environment configuration.
- A live-capable path must pass the guard and reserve an attempt in an already active persistent cycle before transport.
- `GET /api/v1/models` can use the LLM provider and its budget; it is not a free offline diagnostic.
- Failed and rejected attempts can consume quota. Restarting the server does not reset a persistent ledger.
- SystemOne must remain shadow-only; paid fallback and Clef are not enabled by this workflow.
- Do not delete or recreate a ledger to bypass limits. Historical overruns remain part of the readiness record.

Use **Log out** when finished. If a session expires, sign in again; do not bypass CSRF or session checks. See [readiness](READINESS.md) before proposing any online use.
