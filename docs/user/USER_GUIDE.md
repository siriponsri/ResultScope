# ResultScope Laboratory Assistant - user guide

A practical walkthrough of the redesigned application. The screenshots show the
shipped UI. Mocked OCR and generated-answer stages are visibly labeled in the
images and captions; they are not live provider or clinical validation evidence.

For local setup, read [Local setup](../operations/LOCAL_SETUP.md). For provider
configuration, read [Administrator guide](../operations/ADMIN_GUIDE.md).

## 1. Enter the workspace

Open ResultScope. Choose Open workspace or scroll to reach the conversation on the same page. Try an example loads synthetic text without submitting it. The desktop transition follows your normal scroll; reduced-motion preferences and mobile layouts use a static transition.

![Enter the workspace](../assets/screenshots/00-landing-desktop.png)

*Actual landing page; no provider call.*

## 2. Start in the workspace

In the conversation, select Your result or question. You do not need an administrator account to ask a laboratory question. Type in English or Thai. Include the value, unit and the reference range printed on your report.

![Start in the workspace](../assets/screenshots/01-workspace-desktop.png)

*Real application page; captured with provider network disabled.*

## 3. Try a synthetic example

Select Load example to fill the input. Review the text before choosing Send. Loading an example does not call a provider; submitting may do so only when live access has been explicitly enabled by an operator.

![Try a synthetic example](../assets/screenshots/02-example-loaded.png)

*Real example control. Example values and ranges are synthetic.*

## 4. Upload and review a report

Choose Attach report or Report to open the document drawer. Select a de-identified JPEG or PNG up to 3 MB. The drawer shows the selected filename and an image preview; reading an image requires an authorized OCR provider. Check each extracted value, unit and range against the image. Edit incorrect fields. If extraction is unavailable, type the values instead. PDF upload is not supported.

![Upload and review a report](../assets/screenshots/03-review-extracted-values.png)

*Real review UI with a MOCK OCR response. No OCR API call was made.*

## 5. Confirm the fields

Choose Confirm values only after checking every field. The review panel changes to Confirmed extracted values. The confirmed fields become read-only and the question box is filled with a request to explain them. On desktop choose Return to conversation; on mobile the panel closes after confirmation. Choose Send when ready. Before sending, Discard image clears the pending attachment. After sending, start a new analysis to replace a report.

![Confirm the fields](../assets/screenshots/04-confirmed-values.png)

*Real confirmation controls with a MOCK confirmation endpoint. This capture does not validate extraction accuracy.*

## 6. Read the result summary

Read the extracted values before the explanation. Select a value to inspect its supplied reference range. Below range, Above range, Within range and Range unknown are comparison states, not diagnoses. Read the explanation together with missing context.

![Read the result summary](../assets/screenshots/05-result-summary.png)

*Real result UI with fixed MOCK SSE answer and synthetic values. No live LLM validation.*

## 7. Inspect the source

Expand Sources used when it is available. Check the document title, organization, version and page before opening its link. Calculation details explains the deterministic rules. A displayed source is not proof of clinical applicability to your case.

![Inspect the source](../assets/screenshots/06-source-details.png)

*Source disclosure is demonstrated with a synthetic documentation source. This is not a live grounded-answer result.*

## 8. Ask a follow-up or start again

Use Ask a follow-up to ask about the same results. Choose Start a new analysis before using a different report. Wait for the reset to succeed. Do not mix reports from different people in one conversation.

![Ask a follow-up or start again](../assets/screenshots/12-follow-up.png)

*Real follow-up controls with MOCK SSE payloads. Session behavior is additionally covered by existing offline tests.*

## 9. Recover when a provider is unavailable

Read the error and keep the values you entered. Provider access may be disabled, unconfigured or out of budget. Ask the operator to resolve the specific condition. Do not repeatedly retry an exhausted budget. Never paste API keys into the question box.

![Recover when a provider is unavailable](../assets/screenshots/07-provider-unavailable.png)

*Actual offline/missing-configuration route; no browser response mock.*

## 10. Recognize the scope boundary

ResultScope handles laboratory information. An unrelated question is refused locally. Ask a laboratory question instead. The same boundary excludes diagnosis, prescribing and treatment changes.

![Recognize the scope boundary](../assets/screenshots/11-scope-boundary.png)

*Actual deterministic scope refusal; no LLM call.*

## 11. Administrator sign in

Operators can open Administrator from the footer. The login is available only in explicit local-demo mode. The demonstration credentials admin / 1234 must never be used online. Ordinary users do not need this account.

![Administrator sign in](../assets/screenshots/08-admin-login.png)

*Actual local-demo login page. The captured environment contains no private credentials.*

## 12. Configure providers privately

Choose the provider and model, then enter a replacement API key only in the password field. Leave it blank to retain an existing key. Save settings stores the configuration without a provider call. Test with mock does not verify live connectivity. SystemOne remains shadow-only.

![Configure providers privately](../assets/screenshots/09-provider-settings.png)

*Actual settings page with unconfigured slots. No Save, provider test or live request was performed during capture.*

## 13. Use the mobile workspace

On a phone, choose Open workspace or scroll down from the landing page. Type in the question box and select Send. Report opens a full-screen document panel. Use Close report panel or Return to conversation to return. The user guide remains available in the top navigation.

![Use the mobile workspace](../assets/screenshots/10-workspace-mobile.png)

*Actual application at a 390px viewport. Human usability testing has not yet been performed.*

## 14. Review a report on a phone

The report panel fills the screen. Scroll inside it to inspect the image and all extracted fields, then select Confirm values. Keyboard focus stays inside the panel while it is open. Escape or Close report panel returns to the control that opened it. A different report requires a new analysis.

![Review a report on a phone](../assets/screenshots/15-report-mobile.png)

*Actual mobile document panel with a MOCK OCR response. Values and report are synthetic.*

## Limits and privacy

ResultScope provides educational laboratory information. It does not diagnose,
prescribe or choose treatment. The supplied report range is authoritative for
its comparison; public reference documents may describe different methods or
populations. Missing evidence should lead to a clear limitation or abstention.

Use synthetic or de-identified reports in demonstrations. Local processing of a
page does not mean every future provider action stays on the device. Live-enabled
LLM and OCR requests send relevant content to the selected provider. Read the
operator's data policy before using real information.

No PDF OCR, HIS/pharmacy connector, billing, clinical certification or production
readiness is claimed by this manual. See [Readiness](../operations/READINESS.md).
