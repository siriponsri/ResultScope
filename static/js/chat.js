const starter = document.getElementById("starter");
const conversation = document.getElementById("conversation");
const chatWindow = document.getElementById("chat-window");
const loadingIndicator = document.getElementById("loading-indicator");
const errorBanner = document.getElementById("error-banner");
const analysisContent = document.querySelector(".analysis-content");

const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const stopButton = document.getElementById("stop-button");
const sampleButton = document.getElementById("sample-button");
const charCount = document.getElementById("char-count");

const followupForm = document.getElementById("followup-form");
const followupInput = document.getElementById("followup-input");
const followupSend = document.getElementById("followup-send");
const newChatButton = document.getElementById("new-chat-button");

let activeAbortController = null;
let runCount = 0;

function renderMarkdown(rawText) {
  if (window.marked && window.DOMPurify) {
    const html = window.marked.parse(rawText, { breaks: true });
    return window.DOMPurify.sanitize(html);
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
    createElement("h2", "response-title", runCount === 1 ? "Integrated result analysis" : "Contextual follow-up")
  );

  const progress = createElement("ol", "response-progress");
  ["Read", "Verify", "Explain"].forEach((label, index) => {
    const item = createElement("li", index === 0 ? "is-active" : "");
    item.dataset.step = String(index + 1);
    item.append(createElement("i", "", String(index + 1)), createElement("span", "", label));
    progress.appendChild(item);
  });
  head.append(identity, progress);

  const source = createElement("details", "source-disclosure");
  const sourceSummary = createElement("summary", "");
  sourceSummary.append(createElement("span", "", "Source input"), createElement("b", "", "View exact text"));
  source.append(sourceSummary, createElement("pre", "source-text", message));

  const body = createElement("div", "response-body");
  const metricZone = createElement("section", "metric-zone");
  metricZone.setAttribute("aria-label", "Deterministically extracted values");
  metricZone.innerHTML = `
    <div class="zone-heading">
      <div><span>Verified layer</span><h3>Reading literal values</h3></div>
      <strong class="rule-version">Rulebook —</strong>
    </div>
    <div class="metric-loading" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
  `;

  const narrativeZone = createElement("section", "narrative-zone");
  narrativeZone.setAttribute("aria-label", "Integrated explanation");
  narrativeZone.innerHTML = `
    <div class="zone-heading">
      <div><span>Integrated explanation</span><h3>Grounding the narrative</h3></div>
      <strong class="answer-state">Waiting for verified facts</strong>
    </div>
    <div class="narrative-output"><p class="narrative-wait"><i></i> The model receives the deterministic contract before writing.</p></div>
  `;
  body.append(metricZone, narrativeZone);

  const evidence = createElement("details", "rule-disclosure");
  const evidenceSummary = createElement("summary", "");
  const summaryCopy = createElement("span", "");
  summaryCopy.append(createElement("strong", "", "How this answer was grounded"), createElement("small", "", "Inspect the rules applied before the LLM call"));
  evidenceSummary.append(summaryCopy, createElement("b", "", "+"));
  evidence.append(evidenceSummary, createElement("div", "rule-trace"));

  wrapper.append(head, source, body, evidence);
  chatWindow.insertBefore(wrapper, loadingIndicator);
  requestAnimationFrame(() => wrapper.classList.add("is-mounted"));
  scrollToNode(wrapper);
  return wrapper;
}

function formatNumber(value) {
  return Number.isInteger(value) ? String(value) : String(value);
}

function statusCopy(flag, rangeState) {
  if (rangeState === "invalid") return "INVALID RANGE";
  return {
    low: "BELOW RANGE",
    high: "ABOVE RANGE",
    within: "WITHIN RANGE",
    unknown: "RANGE UNKNOWN",
  }[flag] || "UNKNOWN";
}

function buildRangeVisual(item) {
  const unit = item.unit ? ` ${item.unit}` : "";
  const shell = createElement("div", `range-visual range-${item.flag}`);

  if (item.range_state !== "valid") {
    shell.innerHTML = `
      <div class="open-range-track"><i></i><i></i><i></i><i></i><i></i></div>
      <p>${item.range_state === "invalid" ? "The supplied interval is reversed and cannot be used." : "No valid report range was supplied. Status stays unknown."}</p>
    `;
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
  shell.innerHTML = `
    <div class="range-labels"><span>${formatNumber(low)}${unit}</span><span>${formatNumber(high)}${unit}</span></div>
    <div class="range-track"><i class="range-within"></i><b class="range-value" aria-label="Value position"></b></div>
    <p>Compared arithmetically with the interval supplied in this message.</p>
  `;
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
  reference.append(createElement("span", "", "Report reference"), createElement("strong", "", referenceText));

  container.append(top, buildRangeVisual(item), reference);
}

function renderMetrics(surface, meta) {
  const zone = surface.querySelector(".metric-zone");
  zone.replaceChildren();

  const heading = createElement("div", "zone-heading");
  const copy = createElement("div", "");
  copy.append(
    createElement("span", "", "Verified layer"),
    createElement("h3", "", meta.count ? `${meta.count} literal value${meta.count === 1 ? "" : "s"} found` : "Context-only follow-up")
  );
  heading.append(copy, createElement("strong", "rule-version", `Rules ${meta.rulebook_version}`));
  zone.appendChild(heading);

  if (!meta.values?.length) {
    const empty = createElement("div", "metric-empty");
    empty.append(
      createElement("strong", "", "No new numeric value was extracted."),
      createElement("p", "", "The explanation can use prior laboratory context, but it cannot invent a new deterministic result.")
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
  surface.querySelector(".response-title").textContent = intent === "outside_lab_scope" ? "Outside the lab boundary" : "ResultScope guidance";
  surface.querySelector(".response-progress").remove();
  surface.querySelector(".metric-zone").remove();
  surface.querySelector(".rule-disclosure").remove();

  const narrative = surface.querySelector(".narrative-zone");
  narrative.querySelector(".zone-heading h3").textContent = "Deterministic local response";
  narrative.querySelector(".answer-state").textContent = "No LLM called";
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
  surface.querySelector(".answer-state").textContent = "Streaming grounded answer";
  surface.querySelector(".narrative-zone .zone-heading h3").textContent = "One answer, grounded in verified facts";
}

function finishSurface(surface) {
  surface.classList.remove("is-loading");
  surface.classList.add("is-complete");
  surface.querySelectorAll(".response-progress li").forEach((step) => {
    step.classList.remove("is-active");
    step.classList.add("is-done");
  });
  const answerState = surface.querySelector(".answer-state");
  if (answerState) answerState.textContent = "Grounded response complete";
}

function showError(message, notice = false) {
  errorBanner.textContent = message;
  errorBanner.classList.remove("hidden");
  errorBanner.classList.toggle("notice", notice);
  scrollToNode(errorBanner, "nearest");
}

function clearError() {
  errorBanner.classList.add("hidden");
  errorBanner.classList.remove("notice");
  errorBanner.textContent = "";
}

function setBusy(isBusy) {
  messageInput.disabled = isBusy;
  followupInput.disabled = isBusy;
  sendButton.classList.toggle("hidden", isBusy);
  stopButton.classList.toggle("hidden", !isBusy);
  followupSend.disabled = isBusy;
  loadingIndicator.classList.toggle("hidden", !isBusy);
  analysisContent?.setAttribute("aria-busy", String(isBusy));
}

async function sendMessage(message) {
  clearError();
  showConversation();
  const surface = createAnalysisSurface(message);
  setBusy(true);

  activeAbortController = new AbortController();
  let accumulatedText = "";
  let receivedDone = false;
  let narrativeStarted = false;

  try {
    const response = await fetch("/api/v1/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal: activeAbortController.signal,
    });

    if (!response.ok || !response.body) throw new Error(`Server returned ${response.status}`);

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
        } else if (payload.delta) {
          if (!narrativeStarted) {
            beginNarrative(surface);
            narrativeStarted = true;
          }
          accumulatedText += payload.delta;
          surface.querySelector(".narrative-output").innerHTML = renderMarkdown(accumulatedText);
        } else if (payload.error) {
          showError(payload.message || "Something went wrong while preparing the analysis.");
          surface.classList.add("has-error");
        } else if (payload.done) {
          receivedDone = true;
          finishSurface(surface);
        }
      }
    }

    if (!receivedDone) showError("The response ended early. Please try again.");
  } catch (error) {
    surface.classList.remove("is-loading");
    if (error.name === "AbortError") {
      showError("Analysis stopped.", true);
    } else {
      console.error(error);
      showError("Could not reach the service. Check your setup and try again.");
    }
  } finally {
    activeAbortController = null;
    setBusy(false);
    scrollToNode(surface, "nearest");
    followupInput.focus();
  }
}

async function resetConversation() {
  newChatButton.disabled = true;
  try {
    await fetch("/api/v1/chat/reset", { method: "POST" });
  } catch (error) {
    console.warn("reset request failed", error);
  }
  chatWindow.querySelectorAll(".analysis-response").forEach((node) => node.remove());
  clearError();
  messageInput.value = "";
  followupInput.value = "";
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
  const message = messageInput.value.trim();
  if (!message) return;
  messageInput.value = "";
  updateCount();
  sendMessage(message);
});

followupForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = followupInput.value.trim();
  if (!message) return;
  followupInput.value = "";
  sendMessage(message);
});

stopButton.addEventListener("click", () => activeAbortController?.abort());
newChatButton.addEventListener("click", resetConversation);
messageInput.addEventListener("input", updateCount);

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && activeAbortController) activeAbortController.abort();
});

sampleButton.addEventListener("click", () => {
  messageInput.value = "CBC: Hb 10.8 g/dL (12-16), MCV 72 fL (80-100), RDW 17.2% (11.5-14.5), Ferritin 7 ng/mL (15-150). Please summarize what stands out, how the values relate, and what context is still missing.";
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
