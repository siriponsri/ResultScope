const starter = document.getElementById("starter");
const conversation = document.getElementById("conversation");
const chatWindow = document.getElementById("chat-window");
const loadingIndicator = document.getElementById("loading-indicator");
const errorBanner = document.getElementById("error-banner");

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

function renderMarkdown(rawText) {
  const html = marked.parse(rawText, { breaks: true });
  return DOMPurify.sanitize(html);
}

function scrollToLatest() {
  const latest = chatWindow.querySelector(".message:last-of-type");
  latest?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showConversation() {
  starter.classList.add("hidden");
  conversation.classList.remove("hidden");
}

function showStarter() {
  conversation.classList.add("hidden");
  starter.classList.remove("hidden");
}

function appendUserMessage(text) {
  const wrapper = document.createElement("article");
  wrapper.className = "message user";
  wrapper.innerHTML = `
    <div class="message-label">SUBMITTED RESULT / QUESTION</div>
    <div class="bubble"></div>
  `;
  wrapper.querySelector(".bubble").textContent = text;
  chatWindow.insertBefore(wrapper, loadingIndicator);
  scrollToLatest();
}

function createAiMessage() {
  const wrapper = document.createElement("article");
  wrapper.className = "message ai";
  wrapper.innerHTML = `
    <div class="message-label">RESULTSCOPE INTERPRETATION</div>
    <div class="bubble"></div>
  `;
  chatWindow.insertBefore(wrapper, loadingIndicator);
  scrollToLatest();
  return wrapper.querySelector(".bubble");
}


function appendSymbolicReadout(meta) {
  const wrapper = document.createElement("section");
  wrapper.className = "symbolic-readout";

  const head = document.createElement("div");
  head.className = "symbolic-head";
  const flaggedText = meta.flagged_count
    ? `${meta.flagged_count} outside supplied range`
    : "no deterministic out-of-range flag";
  head.innerHTML = `
    <div>
      <div class="message-label">DETERMINISTIC READ</div>
      <strong>${meta.count} value${meta.count === 1 ? "" : "s"} parsed</strong>
    </div>
    <span>${flaggedText}</span>
  `;
  wrapper.appendChild(head);

  const grid = document.createElement("div");
  grid.className = "value-grid";
  (meta.values || []).forEach((item) => {
    const row = document.createElement("div");
    row.className = "value-row";
    const unit = item.unit ? ` ${item.unit}` : "";
    let reference = "No supplied range";
    if (item.reference_low !== null && item.reference_high !== null) {
      reference = `${item.reference_low}–${item.reference_high}${unit}`;
    }
    row.innerHTML = `
      <strong>${item.marker}</strong>
      <span>${item.value}${unit}</span>
      <span>${reference}</span>
      <span class="flag flag-${item.flag}">${item.flag}</span>
    `;
    grid.appendChild(row);
  });
  wrapper.appendChild(grid);
  chatWindow.insertBefore(wrapper, loadingIndicator);
}

function appendGuardrail(message, suggestions = []) {
  const wrapper = document.createElement("article");
  wrapper.className = "message guardrail";
  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = "LAB-ONLY SCOPE GATE";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = renderMarkdown(message);
  wrapper.append(label, bubble);

  if (suggestions.length) {
    const actions = document.createElement("div");
    actions.className = "guardrail-suggestions";
    suggestions.forEach((suggestion) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = suggestion;
      button.addEventListener("click", () => {
        followupInput.value = suggestion;
        followupInput.focus();
      });
      actions.appendChild(button);
    });
    wrapper.appendChild(actions);
  }
  chatWindow.insertBefore(wrapper, loadingIndicator);
  scrollToLatest();
}

function showError(message, notice = false) {
  errorBanner.textContent = message;
  errorBanner.classList.remove("hidden");
  errorBanner.classList.toggle("notice", notice);
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
}

async function sendMessage(message) {
  clearError();
  showConversation();
  appendUserMessage(message);
  setBusy(true);

  activeAbortController = new AbortController();
  let aiBubble = null;
  let accumulatedText = "";
  let receivedDone = false;

  try {
    const response = await fetch("/api/v1/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal: activeAbortController.signal,
    });

    if (!response.ok || !response.body) {
      throw new Error(`Server returned ${response.status}`);
    }

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

        if (payload.guardrail) {
          appendGuardrail(payload.message, payload.suggestions || []);
        } else if (payload.analysis_meta) {
          appendSymbolicReadout(payload.analysis_meta);
        } else if (payload.delta) {
          if (!aiBubble) aiBubble = createAiMessage();
          accumulatedText += payload.delta;
          aiBubble.innerHTML = renderMarkdown(accumulatedText);
        } else if (payload.error) {
          showError(payload.message || "เกิดข้อผิดพลาดระหว่างประมวลผล");
        } else if (payload.done) {
          receivedDone = true;
        }
      }
    }

    if (!receivedDone) {
      showError("การเชื่อมต่อถูกตัดกลางทาง กรุณาลองใหม่อีกครั้ง");
    }
  } catch (error) {
    if (error.name === "AbortError") {
      showError("หยุดการตอบกลับแล้ว", true);
    } else {
      console.error(error);
      showError("เชื่อมต่อ backend ไม่สำเร็จ กรุณาตรวจสอบการตั้งค่าและลองใหม่");
    }
  } finally {
    activeAbortController = null;
    setBusy(false);
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
  chatWindow.querySelectorAll(".message, .symbolic-readout").forEach((node) => node.remove());
  clearError();
  messageInput.value = "";
  followupInput.value = "";
  updateCount();
  showStarter();
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

sampleButton.addEventListener("click", () => {
  messageInput.value = "CBC: Hb 10.8 g/dL (12–16), MCV 72 fL (80–100), RDW 17.2% (11.5–14.5), Ferritin 7 ng/mL (15–150). ช่วยสรุปว่าค่าไหนเด่น เชื่อมโยงกันอย่างไร และข้อมูลอะไรที่ยังขาด";
  updateCount();
  messageInput.focus();
});

document.querySelectorAll("[data-prefix]").forEach((button) => {
  button.addEventListener("click", () => {
    const prefix = button.dataset.prefix || "";
    messageInput.value = prefix + messageInput.value;
    updateCount();
    messageInput.focus();
  });
});

document.querySelectorAll("[data-sample]").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.sample || "";
    updateCount();
    messageInput.focus();
    document.querySelector(".analysis-panel")?.scrollIntoView({ behavior: "smooth" });
  });
});

updateCount();
