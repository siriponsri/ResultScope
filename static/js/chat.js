const starter = document.getElementById("starter");
const conversation = document.getElementById("conversation");
const chatWindow = document.getElementById("chat-window");
const loadingIndicator = document.getElementById("loading-indicator");
const errorBanner = document.getElementById("error-banner");
const analysisContent = document.querySelector(".analysis-content");

const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const analysisStopButton = document.getElementById("analysis-stop-button");
const sampleButton = document.getElementById("sample-button");
const charCount = document.getElementById("char-count");
const imageInput = document.getElementById("image-input");
const imageStatus = document.getElementById("image-status");
const imageReview = document.getElementById("image-review");

const followupForm = document.getElementById("followup-form");
const followupInput = document.getElementById("followup-input");
const followupSend = document.getElementById("followup-send");
const newChatButton = document.getElementById("new-chat-button");

let activeAbortController = null;
let runCount = 0;
let pendingExtraction = null;
let confirmedExtractionId = null;
let imagePreviewUrl = null;
let currentImageFile = null;
let requestInFlight = false;
let lastMessage = "";
let lastOrigin = "starter";
let imageRequestController = null;
let imageRequestToken = 0;

function renderMarkdown(rawText) {
  if (window.marked && window.DOMPurify) {
    const html = window.marked.parse(rawText, { breaks: true });
    return window.DOMPurify.sanitize(html, {
      ALLOWED_TAGS: ["p", "br", "strong", "em", "del", "ul", "ol", "li", "code", "pre", "blockquote", "h1", "h2", "h3", "h4"],
      ALLOWED_ATTR: [],
      ALLOW_DATA_ATTR: false,
    });
  }
  return rawText
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;")
    .replaceAll("\n", "<br>");
}

function scrollToNode(node, block = "start") {
  node?.scrollIntoView({ behavior: "smooth", block });
}

function showConversation() {
  starter.classList.add("hidden");
  conversation.classList.remove("hidden");
  document.body.dataset.view = "analysis";
  window.dispatchEvent(new Event("resultscope:viewchange"));
}

function showStarter() {
  conversation.classList.add("hidden");
  starter.classList.remove("hidden");
  document.body.dataset.view = "intake";
  window.dispatchEvent(new Event("resultscope:viewchange"));
}

function createElement(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function createAnalysisSurface(message) {
  runCount += 1;
  const wrapper = createElement("article", "analysis-response is-loading");
  wrapper.dataset.run = String(runCount);

  const head = createElement("header", "response-header");
  const identity = createElement("div", "response-identity");
  identity.append(
    createElement("span", "response-run", `RUN ${String(runCount).padStart(2, "0")}`),
    createElement("h2", "response-title", runCount === 1 ? "Integrated result summary" : "Follow-up in the same context")
  );

  const progress = createElement("ol", "response-progress");
  ["Read", "Check", "Explain"].forEach((label, index) => {
    const item = createElement("li", index === 0 ? "is-active" : "");
    item.dataset.step = String(index + 1);
    item.append(createElement("i", "", String(index + 1)), createElement("span", "", label));
    progress.appendChild(item);
  });
  head.append(identity, progress);

  const source = createElement("details", "source-disclosure");
  const sourceSummary = createElement("summary", "");
  sourceSummary.append(createElement("span", "", "Message sent to the system"), createElement("b", "", "View full text"));
  source.append(sourceSummary, createElement("pre", "source-text", message));

  const body = createElement("div", "response-body");
  const metricZone = createElement("section", "metric-zone");
  metricZone.setAttribute("aria-label", "Extracted and checked values");
  metricZone.innerHTML = `
    <div class="zone-heading">
      <div><span>Verified data layer</span><h3>Reading literal values</h3></div>
      <strong class="rule-version">Rules —</strong>
    </div>
    <div class="metric-loading" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
  `;

  const narrativeZone = createElement("section", "narrative-zone");
  narrativeZone.setAttribute("aria-label", "Explanation from verified data");
  narrativeZone.innerHTML = `
    <div class="zone-heading">
      <div><span>Integrated explanation</span><h3>Preparing verified facts</h3></div>
      <strong class="answer-state">Waiting for checked values</strong>
    </div>
    <div class="narrative-output"><p class="narrative-wait"><i></i> The explanation will appear after the extracted values are checked.</p></div>
  `;
  body.append(metricZone, narrativeZone);

  const citations = createElement("details", "citation-disclosure hidden");
  const citationSummary = createElement("summary", "");
  citationSummary.append(
    createElement("span", "", "Sources used"),
    createElement("b", "", "View source details")
  );
  citations.append(citationSummary, createElement("div", "citation-list"));

  const evidence = createElement("details", "rule-disclosure");
  const evidenceSummary = createElement("summary", "");
  const summaryCopy = createElement("span", "");
  summaryCopy.append(createElement("strong", "", "How this answer was formed"), createElement("small", "", "Review the rules used before the model call"));
  evidenceSummary.append(summaryCopy, createElement("b", "", "+"));
  evidence.append(evidenceSummary, createElement("div", "rule-trace"));

  wrapper.append(head, source, body, citations, evidence);
  chatWindow.insertBefore(wrapper, loadingIndicator);
  requestAnimationFrame(() => wrapper.classList.add("is-mounted"));
  scrollToNode(wrapper);
  return wrapper;
}

function formatNumber(value) {
  return Number.isInteger(value) ? String(value) : String(value);
}

function statusCopy(flag, rangeState) {
  if (rangeState === "invalid") return "Invalid reference range";
  return {
    low: "Below range",
    high: "Above range",
    within: "Within range",
    unknown: "Range unknown",
  }[flag] || "Unknown";
}

function buildRangeVisual(item) {
  const unit = item.unit ? ` ${item.unit}` : "";
  const shell = createElement("div", `range-visual range-${item.flag}`);

  if (item.range_state !== "valid") {
    const track = createElement("div", "open-range-track");
    for (let index = 0; index < 5; index += 1) track.appendChild(document.createElement("i"));
    shell.append(
      track,
      createElement(
        "p",
        "",
        item.range_state === "invalid"
          ? "The supplied reference range is reversed, so it cannot be used for comparison."
          : "No valid reference range was supplied, so the status is unknown."
      )
    );
    return shell;
  }

  const low = Number(item.reference_low);
  const high = Number(item.reference_high);
  const value = Number(item.value);
  const span = Math.max(high - low, Math.abs(high) * 0.1, 1);
  const displayLow = low - span * 0.35;
  const displayHigh = high + span * 0.35;
  const position = Math.max(2, Math.min(98, ((value - displayLow) / (displayHigh - displayLow)) * 100));
  const lowStop = ((low - displayLow) / (displayHigh - displayLow)) * 100;
  const highStop = ((high - displayLow) / (displayHigh - displayLow)) * 100;

  shell.style.setProperty("--value-position", `${position}%`);
  shell.style.setProperty("--low-stop", `${lowStop}%`);
  shell.style.setProperty("--high-stop", `${highStop}%`);
  const labels = createElement("div", "range-labels");
  labels.append(
    createElement("span", "", `${formatNumber(low)}${unit}`),
    createElement("span", "", `${formatNumber(high)}${unit}`)
  );
  const track = createElement("div", "range-track");
  track.append(
    createElement("i", "range-within"),
    createElement("b", "range-value")
  );
  track.lastElementChild.setAttribute("aria-label", "Value position");
  shell.append(labels, track, createElement("p", "", "Calculated against the reference range supplied in this message."));
  return shell;
}

function renderMetricInspector(container, item) {
  container.replaceChildren();
  const unit = item.unit ? ` ${item.unit}` : "";
  const top = createElement("div", "inspector-top");
  const reading = createElement("div", "inspector-reading");
  reading.append(
    createElement("span", "", item.marker),
    createElement("strong", "", `${formatNumber(item.value)}${unit}`)
  );
  const state = createElement("span", `metric-state state-${item.flag}`, statusCopy(item.flag, item.range_state));
  top.append(reading, state);

  const reference = createElement("div", "inspector-reference");
  const referenceText = item.range_state === "valid"
    ? `${formatNumber(item.reference_low)}–${formatNumber(item.reference_high)}${unit}`
    : item.range_state === "invalid"
      ? `${formatNumber(item.reference_low)}–${formatNumber(item.reference_high)}${unit} · invalid order`
      : "Not supplied";
  reference.append(createElement("span", "", "Report reference range"), createElement("strong", "", referenceText));

  container.append(top, buildRangeVisual(item), reference);
}

function renderMetrics(surface, meta) {
  const zone = surface.querySelector(".metric-zone");
  zone.replaceChildren();

  const heading = createElement("div", "zone-heading");
  const copy = createElement("div", "");
  copy.append(
    createElement("span", "", "Verified data layer"),
    createElement("h3", "", meta.count ? `${meta.count} numeric value${meta.count === 1 ? "" : "s"} found` : "Follow-up using the same context")
  );
  heading.append(copy, createElement("strong", "rule-version", `Rules ${meta.rulebook_version}`));
  zone.appendChild(heading);

  if (!meta.values?.length) {
    const empty = createElement("div", "metric-empty");
    empty.append(
      createElement("strong", "", "No new numeric values were extracted"),
      createElement("p", "", "The explanation can use the existing laboratory context, but no result values will be invented.")
    );
    zone.appendChild(empty);
  } else {
    const deck = createElement("div", "metric-deck");
    const inspector = createElement("div", "metric-inspector");
    meta.values.forEach((item, index) => {
      const button = createElement("button", `metric-key state-${item.flag}${index === 0 ? " is-selected" : ""}`);
      button.type = "button";
      button.setAttribute("aria-pressed", String(index === 0));
      const unit = item.unit ? ` ${item.unit}` : "";
      button.append(
        createElement("span", "", item.marker),
        createElement("strong", "", `${formatNumber(item.value)}${unit}`),
        createElement("small", "", statusCopy(item.flag, item.range_state))
      );
      button.addEventListener("click", () => {
        deck.querySelectorAll(".metric-key").forEach((key) => {
          const selected = key === button;
          key.classList.toggle("is-selected", selected);
          key.setAttribute("aria-pressed", String(selected));
        });
        inspector.classList.add("is-switching");
        window.setTimeout(() => {
          renderMetricInspector(inspector, item);
          inspector.classList.remove("is-switching");
        }, 120);
      });
      deck.appendChild(button);
    });
    renderMetricInspector(inspector, meta.values[0]);
    zone.append(deck, inspector);
  }

  const trace = surface.querySelector(".rule-trace");
  trace.replaceChildren();
  (meta.trace || []).forEach((entry) => {
    const row = createElement("article", "trace-row");
    row.append(
      createElement("span", "trace-id", entry.rule_id),
      createElement("strong", "", entry.title),
      createElement("p", "", entry.detail),
      createElement("small", "", entry.effect)
    );
    trace.appendChild(row);
  });

  const steps = surface.querySelectorAll(".response-progress li");
  steps[0]?.classList.replace("is-active", "is-done");
  steps[1]?.classList.add("is-done");
  steps[2]?.classList.add("is-active");
  surface.classList.add("has-metrics");
}

function renderLocalResponse(surface, message, intent, suggestions = []) {
  surface.classList.remove("is-loading");
  surface.classList.add("is-local");
  surface.querySelector(".response-title").textContent = intent === "outside_lab_scope" ? "Outside laboratory scope" : "ResultScope guidance";
  surface.querySelector(".response-progress").remove();
  surface.querySelector(".metric-zone").remove();
  surface.querySelector(".rule-disclosure").remove();

  const narrative = surface.querySelector(".narrative-zone");
  narrative.querySelector(".zone-heading h3").textContent = "Rule-based response";
  narrative.querySelector(".answer-state").textContent = "LLM was not called";
  const output = narrative.querySelector(".narrative-output");
  output.innerHTML = renderMarkdown(message);

  if (suggestions.length) {
    const actions = createElement("div", "guardrail-suggestions");
    suggestions.forEach((suggestion) => {
      const button = createElement("button", "", suggestion);
      button.type = "button";
      button.addEventListener("click", () => {
        followupInput.value = suggestion;
        followupInput.focus();
      });
      actions.appendChild(button);
    });
    output.appendChild(actions);
  }
}

function beginNarrative(surface) {
  const step = surface.querySelector('.response-progress li[data-step="3"]');
  step?.classList.add("is-active");
  surface.querySelector(".answer-state").textContent = "Sending an answer grounded in checked data";
  surface.querySelector(".narrative-zone .zone-heading h3").textContent = "One explanation from verified facts";
}

function finishSurface(surface) {
  surface.classList.remove("is-loading");
  if (surface.classList.contains("has-error")) {
    surface.classList.remove("is-complete");
    surface.querySelectorAll(".response-progress li").forEach((step) => step.classList.remove("is-active"));
    const answerState = surface.querySelector(".answer-state");
    if (answerState) answerState.textContent = "The answer ended with an error";
    return;
  }
  surface.classList.add("is-complete");
  surface.querySelectorAll(".response-progress li").forEach((step) => {
    step.classList.remove("is-active");
    step.classList.add("is-done");
  });
  const answerState = surface.querySelector(".answer-state");
  if (answerState) answerState.textContent = "Answer complete from verified data";
}

function showError(message, notice = false, retryMessage = null) {
  errorBanner.replaceChildren(createElement("span", "error-copy", message));
  if (retryMessage) {
    const retry = createElement("button", "error-retry", "Try again");
    retry.type = "button";
    retry.addEventListener("click", () => {
      clearError();
      sendMessage(retryMessage, lastOrigin);
    });
    errorBanner.appendChild(retry);
  }
  errorBanner.classList.remove("hidden");
  errorBanner.classList.toggle("notice", notice);
  scrollToNode(errorBanner, "nearest");
}

function clearError() {
  errorBanner.classList.add("hidden");
  errorBanner.classList.remove("notice");
  errorBanner.replaceChildren();
}

function renderCitations(surface, metadata) {
  const disclosure = surface.querySelector(".citation-disclosure");
  const list = surface.querySelector(".citation-list");
  const citations = Array.isArray(metadata?.citations) ? metadata.citations : [];
  if (!disclosure || !list || !citations.length) return;

  list.replaceChildren();
  citations.forEach((citation) => {
    const card = createElement("article", "citation-card");
    const title = citation.title || citation.source_id || "Unnamed source";
    card.appendChild(createElement("strong", "citation-title", title));
    if (citation.organisation) card.appendChild(createElement("span", "citation-organisation", citation.organisation));

    const details = [];
    if (citation.page !== undefined && citation.page !== null) details.push(`Page ${citation.page}`);
    if (citation.section) details.push(`Section ${citation.section}`);
    if (citation.version) details.push(`Version ${citation.version}`);
    if (citation.data_class) details.push(citation.data_class === "public_reference" ? "Public reference" : citation.data_class);
    if (details.length) card.appendChild(createElement("span", "citation-details", details.join(" · ")));
    if (citation.license) card.appendChild(createElement("small", "citation-license", `License: ${citation.license}`));

    const url = citation.source_url || citation.origin;
    try {
      const parsed = new URL(url);
      if (parsed.protocol === "http:" || parsed.protocol === "https:") {
        const link = createElement("a", "citation-link", "Open source");
        link.href = parsed.href;
        link.target = "_blank";
        link.rel = "noreferrer noopener";
        card.appendChild(link);
      }
    } catch {
      // Local source origins are provenance text, not browser links.
    }
    list.appendChild(card);
  });
  disclosure.classList.remove("hidden");
}

function setImageStatus(message, state = "") {
  imageStatus.textContent = message;
  imageStatus.dataset.state = state;
}

function clearImagePreview() {
  if (imagePreviewUrl) URL.revokeObjectURL(imagePreviewUrl);
  imagePreviewUrl = null;
}

function resetImageState() {
  imageRequestToken += 1;
  imageRequestController?.abort();
  imageRequestController = null;
  clearImagePreview();
  pendingExtraction = null;
  confirmedExtractionId = null;
  currentImageFile = null;
  imageInput.value = "";
  imageReview.replaceChildren();
  imageReview.classList.add("hidden");
  setImageStatus("No file selected");
}

function renderImageReview(file, extraction) {
  pendingExtraction = extraction;
  imageReview.replaceChildren();
  imageReview.classList.remove("hidden");
  clearImagePreview();
  imagePreviewUrl = URL.createObjectURL(file);

  const preview = createElement("img", "image-preview");
  preview.src = imagePreviewUrl;
  preview.alt = "Uploaded laboratory report preview";

  const panel = createElement("div", "image-review-fields");
  const heading = createElement("div", "image-review-heading");
  heading.append(
    createElement("strong", "", extraction.status === "confirmed" ? "Confirmed extracted values" : "Review values extracted from the image"),
    createElement("small", "", "Text from the image is unverified data. Edit unclear values before confirming.")
  );
  panel.appendChild(heading);

  if (!extraction.fields?.length) {
    panel.appendChild(createElement("p", "image-review-empty", "No values could be extracted. Try a clearer image or enter values manually."));
  }

  const fieldNodes = [];
  (extraction.fields || []).forEach((field) => {
    const row = createElement("fieldset", "image-field");
    row.dataset.fieldId = field.field_id;
    const legend = createElement("legend", "", field.marker || "Unknown field");
    const valueLabel = createElement("label", "", "Value");
    const value = document.createElement("input");
    value.type = "text";
    value.value = field.raw_value || "";
    value.autocomplete = "off";
    valueLabel.appendChild(value);
    const unitLabel = createElement("label", "", "Unit");
    const unit = document.createElement("input");
    unit.type = "text";
    unit.value = field.unit || "";
    unit.autocomplete = "off";
    unitLabel.appendChild(unit);
    const rangeLabel = createElement("label", "", "Reference range");
    const range = document.createElement("input");
    range.type = "text";
    range.value = field.reference_range_raw || "";
    range.placeholder = "For example, 10-15; leave blank if unavailable";
    range.autocomplete = "off";
    rangeLabel.appendChild(range);
    row.append(legend, valueLabel, unitLabel, rangeLabel);
    panel.appendChild(row);
    fieldNodes.push({ row, field, value, unit, range });
  });

  const actions = createElement("div", "image-review-actions");
  const cancel = createElement("button", "secondary-button", "Discard image");
  cancel.type = "button";
  cancel.addEventListener("click", cancelImageExtraction);
  actions.appendChild(cancel);
  if (extraction.status === "review_required" && fieldNodes.length) {
    const confirm = createElement("button", "primary-button", "Confirm values");
    confirm.type = "button";
    confirm.addEventListener("click", () => confirmImageExtraction(fieldNodes));
    actions.appendChild(confirm);
  }
  panel.appendChild(actions);

  const shell = createElement("div", "image-review-shell");
  shell.append(preview, panel);
  imageReview.appendChild(shell);
  setImageStatus(extraction.status === "confirmed" ? "Confirmed for this analysis" : "Review and edit the values", extraction.status);
}

async function cancelImageExtraction() {
  const extractionId = pendingExtraction?.extraction_id;
  if (extractionId) {
    try { await fetch(`/api/v1/images/${extractionId}`, { method: "DELETE" }); } catch (error) { console.warn("image cancel failed", error); }
  }
  resetImageState();
}

async function confirmImageExtraction(fieldNodes) {
  if (!pendingExtraction) return;
  const fields = fieldNodes.map(({ row, field, value, unit, range }) => {
    const rangeParts = range.value.match(/^\s*([^\-–]+?)\s*[-–]\s*(.+?)\s*$/);
    return {
      field_id: row.dataset.fieldId,
      marker: field.marker,
      raw_value: value.value.trim() || null,
      unit: unit.value.trim() || null,
      reference_low: rangeParts ? rangeParts[1].trim() : null,
      reference_high: rangeParts ? rangeParts[2].trim() : null,
      reference_range_raw: range.value.trim() || null,
    };
  });
  const token = imageRequestToken;
  imageRequestController = new AbortController();
  try {
    const response = await fetch(`/api/v1/images/${pendingExtraction.extraction_id}/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ revision: pendingExtraction.revision, fields }),
      signal: imageRequestController.signal,
    });
    const body = await response.json();
    if (token !== imageRequestToken) return;
    if (!response.ok) throw new Error(body.message || "The extracted fields could not be confirmed.");
    pendingExtraction = body;
    confirmedExtractionId = body.extraction_id;
    renderImageReview(currentImageFile, body);
    messageInput.value = "Please explain the values extracted from this laboratory report.";
    updateCount();
    messageInput.focus();
  } catch (error) {
    if (token === imageRequestToken && error.name !== "AbortError") {
    showError(error.message || "The extracted values could not be confirmed.");
    }
  } finally {
    if (token === imageRequestToken) imageRequestController = null;
  }
}

async function uploadImage(file) {
  resetImageState();
  const token = imageRequestToken;
  currentImageFile = file;
  setImageStatus("Reading image…", "loading");
  const form = new FormData();
  form.append("file", file, file.name);
  imageRequestController = new AbortController();
  try {
    const response = await fetch("/api/v1/images/extract", {
      method: "POST",
      body: form,
      signal: imageRequestController.signal,
    });
    const body = await response.json();
    if (token !== imageRequestToken) return;
    if (!response.ok) throw new Error(body.message || "The image could not be read.");
    renderImageReview(file, body);
  } catch (error) {
    if (token === imageRequestToken && error.name !== "AbortError") {
      resetImageState();
      setImageStatus(error.message || "The image could not be read.", "error");
    }
  } finally {
    if (token === imageRequestToken) imageRequestController = null;
  }
}

function setBusy(isBusy) {
  requestInFlight = isBusy;
  messageInput.disabled = isBusy;
  followupInput.disabled = isBusy;
  imageInput.disabled = isBusy;
  newChatButton.disabled = isBusy;
  sendButton.classList.toggle("hidden", isBusy);
  analysisStopButton.classList.toggle("hidden", !isBusy);
  followupSend.disabled = isBusy;
  loadingIndicator.classList.toggle("hidden", !isBusy);
  analysisContent?.setAttribute("aria-busy", String(isBusy));
}

async function sendMessage(message, origin = "followup") {
  if (requestInFlight || !message) return false;
  lastMessage = message;
  lastOrigin = origin;
  clearError();
  showConversation();
  const surface = createAnalysisSurface(message);
  setBusy(true);

  activeAbortController = new AbortController();
  let accumulatedText = "";
  let receivedDone = false;
  let narrativeStarted = false;
  let streamError = false;

  try {
    const response = await fetch("/api/v1/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, extraction_id: confirmedExtractionId }),
      signal: activeAbortController.signal,
    });

    if (!response.ok || !response.body) throw new Error(`The server returned ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";

      for (const rawEvent of events) {
        const dataLine = rawEvent.split("\n").find((line) => line.startsWith("data:"));
        if (!dataLine) continue;
        let payload;
        try {
          payload = JSON.parse(dataLine.slice(5).trim());
        } catch {
          continue;
        }

        if (payload.local_response) {
          renderLocalResponse(surface, payload.message, payload.intent, payload.suggestions || []);
        } else if (payload.analysis_meta) {
          renderMetrics(surface, payload.analysis_meta);
        } else if (payload.response_meta) {
          renderCitations(surface, payload.response_meta);
        } else if (payload.delta) {
          if (!narrativeStarted) {
            beginNarrative(surface);
            narrativeStarted = true;
          }
          accumulatedText += payload.delta;
          surface.querySelector(".narrative-output").innerHTML = renderMarkdown(accumulatedText);
        } else if (payload.error) {
          streamError = true;
          showError(payload.message || "An error occurred while preparing the answer.", false, message);
          surface.classList.add("has-error");
        } else if (payload.done) {
          receivedDone = true;
          finishSurface(surface);
        }
      }
    }

    if (!receivedDone) {
      showError("The answer ended early. Please try again.", false, message);
      surface.classList.add("has-error");
      finishSurface(surface);
    }
    if (streamError) finishSurface(surface);
  } catch (error) {
    surface.classList.add("has-error");
    if (error.name === "AbortError") {
      showError("Analysis stopped. You can try again.", true, message);
    } else {
      console.error(error);
      showError("The service could not be reached. Check the settings and try again.", false, message);
    }
    finishSurface(surface);
  } finally {
    activeAbortController = null;
    setBusy(false);
    scrollToNode(surface, "nearest");
    if (!errorBanner.classList.contains("hidden")) {
      errorBanner.querySelector(".error-retry")?.focus();
    } else {
      followupInput.focus();
    }
  }
  return receivedDone && !streamError && !surface.classList.contains("has-error");
}

async function resetConversation() {
  newChatButton.disabled = true;
  try {
    const response = await fetch("/api/v1/chat/reset", { method: "POST" });
    const body = await response.json().catch(() => ({}));
    if (!response.ok || body.ok !== true) {
      throw new Error(body.message || "A new analysis could not be started.");
    }
  } catch (error) {
    showError(error.message || "A new analysis could not be started.");
    newChatButton.disabled = false;
    return;
  }
  chatWindow.querySelectorAll(".analysis-response").forEach((node) => node.remove());
  clearError();
  messageInput.value = "";
  followupInput.value = "";
  resetImageState();
  runCount = 0;
  updateCount();
  showStarter();
  analysisContent?.setAttribute("aria-busy", "false");
  messageInput.focus();
  newChatButton.disabled = false;
}

function updateCount() {
  charCount.textContent = `${messageInput.value.length.toLocaleString()} / 12,000`;
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (requestInFlight) return;
  const message = messageInput.value.trim();
  const submission = message || (confirmedExtractionId ? "Please explain the values extracted from this laboratory report." : "");
  if (!submission) return;
  sendMessage(submission, "starter").then((success) => {
    if (success) {
      messageInput.value = "";
      updateCount();
    }
  });
});

followupForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (requestInFlight) return;
  const message = followupInput.value.trim();
  if (!message) return;
  sendMessage(message, "followup").then((success) => {
    if (success) followupInput.value = "";
  });
});

analysisStopButton.addEventListener("click", () => activeAbortController?.abort());
newChatButton.addEventListener("click", resetConversation);
messageInput.addEventListener("input", updateCount);
imageInput.addEventListener("change", () => {
  const file = imageInput.files?.[0];
  if (file) uploadImage(file);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && activeAbortController) activeAbortController.abort();
});

sampleButton.addEventListener("click", () => {
  messageInput.value = "CBC: Hb 10.8 g/dL (12-16), MCV 72 fL (80-100), RDW 17.2% (11.5-14.5), Ferritin 7 ng/mL (15-150). Please summarize key findings, relationships, and missing context.";
  updateCount();
  messageInput.focus();
});

document.querySelectorAll("[data-sample]").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.sample || "";
    updateCount();
    messageInput.focus();
    button.closest(".intake-console")?.classList.add("has-selection");
  });
});

document.body.dataset.view = "intake";
updateCount();
