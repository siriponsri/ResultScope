# Troubleshooting

| Symptom | Action |
|---|---|
| Connect AI | Open Settings; configure both language and guard models plus the named budget cycle. |
| Access required | Enter the project owner's demo access code for this tab. |
| Usage limit reached | Ask the operator to review the configured cycle. Do not reset counters to retry. |
| Safety check unavailable | Check guard endpoint, model and key. No unguarded fallback is available. |
| Could not verify an answer | Rephrase or add relevant context; the draft was withheld. |
| No source match | Name the test, add its abbreviation, or ask a more specific question. |
| Report reading unavailable | Configure vision separately; free-text questions remain available. |
| PDF page limit | Use an individual report PDF with one to three pages, below 3 MB. |
| Wrong/illegible extraction | Correct the visible rows before confirmation, or use a clearer scan. |
| Context expired/changed | Download any visible conversation you need, then start a new chat. |
| LightRAG error | Check `/query/data`, `X-API-Key`, service version and imported file-source IDs. |
| Vercel startup fails | Verify session secret, access code, Redis and cycle settings; SQLite is local only. |

Do not paste keys, reports or raw provider responses into bug reports. Include only the
request ID, the visible error code, deployment version and reproducible synthetic steps.
