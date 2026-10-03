# ResultScope capability matrix

| Capability | Implemented locally | Verified live | Proposed / blocked |
|---|---:|---:|---|
| Lab-only scope gate | Yes | No live provider required | — |
| Supplied-range parsing and flags | Yes | No | — |
| Typed question and follow-up flow | Yes | No live LLM | Live quality NOT_RUN |
| JPEG/PNG upload and OCR correction | Yes, mocked/local | No live Vision | Live Vision authorization missing |
| English web UI with multilingual LLM conversation | Yes | No live LLM | Live language-quality evaluation NOT_RUN |
| Typhoon LLM answer adapter | Yes, mocked/local | No | Live contract and quality NOT_RUN |
| Typhoon OCR image boundary | Yes, separate adapter, mocked/local | No | PNG/JPEG upload only; PDF upload BLOCKED; live OCR verification NOT_RUN |
| OpenThai-SystemOne iApp shadow adapter | Yes, separate typed parser | No | Shadow comparison and live contract NOT_RUN |
| Provider compatibility catalog | Yes, server allowlist | No | Model/account access verification per provider |
| Local Admin Settings authentication and CSRF | Yes, local-demo only | No online verification | Cloud secret persistence BLOCKED |
| Public numeric reference lookup | Yes, pinned offline | No | Not business approval |
| WHO educational guideline notes | Yes, separate namespace | No | Commercial rights need review |
| Source metadata/citation disclosure | Yes | No live model | — |
| Clef decision route | No; disabled | No | Must remain disabled |
| HIS/pharmacy connector | No | No | Contract-only; credentials/partner absent |
| Authentication/patient profiles | Admin authentication only, local-demo | No online verification | Patient profiles not implemented |
| Deployment | No | No | Owner authorization required |
