# User guide — ResultScope 2.0

## Start with a question

Type a laboratory question in the composer and press Enter. Shift+Enter inserts a
new line. No file is required. You can ask in your preferred language, request a simpler
explanation or ask a follow-up. The page controls stay in English. Model quality varies
by language; professional terms, units and report intervals should remain unchanged.

When **Connect AI** appears, open **Settings & connection**. The project operator must
configure the language and safety models. If requested, enter the demo access code;
it stays in this tab. A configured badge is not proof of a successful provider call.

## Read a response

The interface shows actual processing stages while the models work. The answer appears
only after the evidence and safety checks complete. Open source links to read the
original publisher. Source presence does not guarantee clinical correctness. Ask another
question in your own words or use a suggested follow-up. **Stop** cancels a pending
request; a provider attempt may already have been charged. **Try again** starts a new
attempt and also consumes budget. **Download conversation** exports the visible exchange.

## Add an optional report

Use the paperclip for PNG, JPEG or PDF, at most 3 MB. PDFs support one to three pages.
Open **Sample reports** for the six supplied Thai laboratory reports. Each is synthetic,
including its identities, results and ranges; these are not real patient records.
Download the original PNG/PDF from the preview if needed.

Selecting a file does not send it to the model. Review consent, then choose **Read with AI**.
The report reader transcribes the actual pixels. Compare every name, value, unit,
reference interval and flag with the original. Correct mistakes or remove spurious rows.
Only **Confirm values & continue the conversation** makes those rows available to chat.
You can inspect confirmed rows again through **Report context**.

Printed flags are preserved separately from conservative numeric interval comparisons.
Qualitative or ambiguous results stay unchanged and may have an unknown comparison.
A public reference interval never replaces the interval printed on your report. The
combined six-page demo PDF is for browsing; upload individual panel PDFs to the reader.

## Privacy and limits

Use synthetic or de-identified documents for this prototype. The configured AI services
receive your message, relevant recent conversation and confirmed report fields. The
vision provider receives document pixels after consent. The guard receives the request
and candidate answer. An optional LightRAG service receives a model-written search query.
Providers may retain data under their own policies. No provider retention guarantee is made.

The app holds an encrypted, session-bound context token in tab memory. It expires after
one hour by default. Refreshing clears the workspace. The server does not save v2 report
images or conversation bodies to disk. The signed cookie and Redis usage counts contain
no report text. Logs record request ID/outcome/duration, not message bodies.
A downloaded conversation is your own file and may contain sensitive information.

**New conversation** clears the current workspace after confirmation and rotates its
session cookie. Attach a different report in a new conversation to avoid mixing context.
A copied old token is unusable with the new cookie; this is not remote revocation of a
previously stolen cookie/token pair. Do not share browser sessions.

ResultScope explains laboratory information. It cannot diagnose, prescribe, change
medication or decide treatment. Missing evidence leads to clarification or a candid
limitation. Discuss important findings and any urgent symptoms with a qualified clinician.
