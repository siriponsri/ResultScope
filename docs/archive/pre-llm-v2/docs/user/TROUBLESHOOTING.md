# Troubleshooting

| What you see | Meaning | Next action |
| --- | --- | --- |
| Provider access disabled | The offline guard is active | Continue with offline checks. An operator must authorize a new live cycle before provider testing. |
| Provider not configured | The server has no usable credential for that slot | Ask the operator to configure it privately. Do not paste keys into chat. |
| Budget exhausted | The configured attempt limit has been reached | Stop. Do not refresh, reset the ledger or open a new session to bypass the limit. |
| Could not read an image | Unsupported/unreadable image or OCR unavailable | Use a clear de-identified PNG/JPEG or type the values. PDF upload is not implemented. |
| Range unknown | No valid report-specific range was supplied | Add the range from the report, or leave the status unknown. |
| Safe refusal / insufficient evidence | The question is outside scope, lacks evidence or fails validation | Narrow the question or provide source information. Do not weaken the validator. |
| Administrator page unavailable | Explicit local-demo mode is disabled | This is expected outside local-demo mode. Ordinary users do not need this login. |
| Reset fails | The previous session could not be cleared safely | Wait and retry. Do not assume a different report has a clean context until reset succeeds. |

Start a new analysis for each separate report. Keep real patient identifiers out of
screenshots, demonstration data and provider experiments.
