(function () {
  "use strict";

  const state = {
    data: null,
    tab: "listening",
    speakingIndex: 0,
    writingIndex: 0,
    timerSeconds: 0,
    timerId: null,
    recorder: null,
    chunks: [],
  };

  const els = {};
  const storageKey = "datakrs_ielts_skills_v1";

  function $(id) {
    return document.getElementById(id);
  }

  function esc(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function showToast(message) {
    let toast = document.querySelector(".app-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "app-toast";
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.remove("show"), 2200);
  }

  function loadProgress() {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
      state.tab = saved.tab || "listening";
      state.speakingIndex = saved.speakingIndex || 0;
      state.writingIndex = saved.writingIndex || 0;
      document.querySelectorAll("[data-daily-check]").forEach((input) => {
        input.checked = Boolean(saved.checks && saved.checks[input.dataset.dailyCheck]);
      });
    } catch (error) {
      state.tab = "listening";
    }
  }

  function saveProgress() {
    const checks = {};
    document.querySelectorAll("[data-daily-check]").forEach((input) => {
      checks[input.dataset.dailyCheck] = input.checked;
    });
    localStorage.setItem(
      storageKey,
      JSON.stringify({
        tab: state.tab,
        speakingIndex: state.speakingIndex,
        writingIndex: state.writingIndex,
        checks,
      })
    );
  }

  function formatTime(seconds) {
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${String(min).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  }

  function stopTimer() {
    window.clearInterval(state.timerId);
    state.timerId = null;
  }

  function startTimer(seconds) {
    stopTimer();
    state.timerSeconds = seconds;
    const timer = document.querySelector("[data-skill-timer]");
    if (timer) timer.textContent = formatTime(state.timerSeconds);
    state.timerId = window.setInterval(() => {
      state.timerSeconds = Math.max(0, state.timerSeconds - 1);
      const current = document.querySelector("[data-skill-timer]");
      if (current) current.textContent = formatTime(state.timerSeconds);
      if (state.timerSeconds <= 0) {
        stopTimer();
        showToast("计时结束");
      }
    }, 1000);
  }

  function renderListening() {
    els.panel.innerHTML = `
      <div class="skill-card-grid">
        ${state.data.listening
          .map(
            (item) => `
              <article class="skill-card">
                <span>${esc(item.mode)}</span>
                <h2>${esc(item.title)}</h2>
                <ol>${item.steps.map((step) => `<li>${esc(step)}</li>`).join("")}</ol>
                <a class="skill-action" href="${esc(item.link)}">开始训练</a>
              </article>
            `
          )
          .join("")}
      </div>
    `;
  }

  function renderReading() {
    const item = state.data.reading[0];
    els.panel.innerHTML = `
      <article class="skill-card">
        <span>Reading</span>
        <h2>${esc(item.title)}</h2>
        <ol>${item.steps.map((step) => `<li>${esc(step)}</li>`).join("")}</ol>
        <a class="skill-action" href="${esc(item.link)}">进入 230 篇阅读库</a>
      </article>
    `;
  }

  function activeSpeaking() {
    return state.data.speaking[state.speakingIndex] || state.data.speaking[0];
  }

  function renderSpeaking() {
    const item = activeSpeaking();
    const questionHtml = item.cue
      ? `<p class="skill-prompt">${esc(item.cue)}</p>`
      : `<ol>${item.questions.map((question) => `<li>${esc(question)}</li>`).join("")}</ol>`;
    els.panel.innerHTML = `
      <article class="skill-card">
        <span>${esc(item.part)}</span>
        <h2>${esc(item.topic)}</h2>
        ${questionHtml}
        <p class="skill-focus">${esc(item.focus)}</p>
        <div class="skill-timer-row">
          <strong data-skill-timer>00:00</strong>
          <button type="button" data-start-timer="60">准备 1 分钟</button>
          <button type="button" data-start-timer="120">回答 2 分钟</button>
        </div>
        <div class="skill-recorder">
          <button type="button" data-record-speaking>开始录音</button>
          <button type="button" data-stop-speaking disabled>停止</button>
          <div id="speakingPlayback"></div>
        </div>
        <div class="skill-nav-row">
          <button type="button" data-prev-speaking>上一题</button>
          <button type="button" data-next-speaking>下一题</button>
        </div>
      </article>
    `;
  }

  function activeWriting() {
    return state.data.writing[state.writingIndex] || state.data.writing[0];
  }

  function draftKey(item) {
    return `${storageKey}_draft_${item.task}_${item.title}`.replace(/\s+/g, "_");
  }

  function renderWriting() {
    const item = activeWriting();
    const draft = localStorage.getItem(draftKey(item)) || "";
    els.panel.innerHTML = `
      <article class="skill-card">
        <span>${esc(item.task)} · ${item.minutes} min · ${item.targetWords}+ words</span>
        <h2>${esc(item.title)}</h2>
        <p class="skill-prompt">${esc(item.prompt)}</p>
        <div class="skill-timer-row">
          <strong data-skill-timer>${formatTime(item.minutes * 60)}</strong>
          <button type="button" data-start-timer="${item.minutes * 60}">开始计时</button>
        </div>
        <textarea id="writingDraft" class="skill-writing-box" placeholder="直接在这里写，自动保存在本机浏览器。">${esc(draft)}</textarea>
        <div class="skill-writing-meta">
          <span id="writingWordCount">0 words</span>
          <button type="button" data-clear-draft>清空草稿</button>
        </div>
        <div class="skill-checklist">
          ${item.checklist.map((check) => `<label><input type="checkbox"> ${esc(check)}</label>`).join("")}
        </div>
        <div class="skill-nav-row">
          <button type="button" data-prev-writing>上一题</button>
          <button type="button" data-next-writing>下一题</button>
        </div>
      </article>
    `;
    updateWordCount();
  }

  function updateWordCount() {
    const box = $("writingDraft");
    const count = $("writingWordCount");
    if (!box || !count) return;
    const words = box.value.trim() ? box.value.trim().split(/\s+/).length : 0;
    count.textContent = `${words} words`;
  }

  function render() {
    stopTimer();
    document.querySelectorAll("[data-skill-tab]").forEach((button) => {
      button.classList.toggle("active", button.dataset.skillTab === state.tab);
    });
    if (state.tab === "listening") renderListening();
    if (state.tab === "speaking") renderSpeaking();
    if (state.tab === "reading") renderReading();
    if (state.tab === "writing") renderWriting();
    saveProgress();
  }

  async function startRecording() {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      showToast("当前浏览器不支持录音");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      state.chunks = [];
      state.recorder = new MediaRecorder(stream);
      state.recorder.ondataavailable = (event) => {
        if (event.data.size) state.chunks.push(event.data);
      };
      state.recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        const blob = new Blob(state.chunks, { type: "audio/webm" });
        const url = URL.createObjectURL(blob);
        const target = $("speakingPlayback");
        if (target) target.innerHTML = `<audio controls src="${url}"></audio>`;
      };
      state.recorder.start();
      document.querySelector("[data-record-speaking]").disabled = true;
      document.querySelector("[data-stop-speaking]").disabled = false;
    } catch (error) {
      showToast("无法启动录音，请检查麦克风权限");
    }
  }

  function stopRecording() {
    if (state.recorder && state.recorder.state !== "inactive") state.recorder.stop();
    const start = document.querySelector("[data-record-speaking]");
    const stop = document.querySelector("[data-stop-speaking]");
    if (start) start.disabled = false;
    if (stop) stop.disabled = true;
  }

  function bindEvents() {
    document.querySelectorAll("[data-skill-tab]").forEach((button) => {
      button.addEventListener("click", () => {
        state.tab = button.dataset.skillTab;
        render();
      });
    });
    document.querySelectorAll("[data-daily-check]").forEach((input) => {
      input.addEventListener("change", saveProgress);
    });
    els.panel.addEventListener("click", (event) => {
      const timerButton = event.target.closest("[data-start-timer]");
      if (timerButton) {
        startTimer(Number(timerButton.dataset.startTimer));
        return;
      }
      if (event.target.closest("[data-record-speaking]")) {
        startRecording();
        return;
      }
      if (event.target.closest("[data-stop-speaking]")) {
        stopRecording();
        return;
      }
      if (event.target.closest("[data-next-speaking]")) {
        state.speakingIndex = (state.speakingIndex + 1) % state.data.speaking.length;
        render();
        return;
      }
      if (event.target.closest("[data-prev-speaking]")) {
        state.speakingIndex = (state.speakingIndex - 1 + state.data.speaking.length) % state.data.speaking.length;
        render();
        return;
      }
      if (event.target.closest("[data-next-writing]")) {
        state.writingIndex = (state.writingIndex + 1) % state.data.writing.length;
        render();
        return;
      }
      if (event.target.closest("[data-prev-writing]")) {
        state.writingIndex = (state.writingIndex - 1 + state.data.writing.length) % state.data.writing.length;
        render();
        return;
      }
      if (event.target.closest("[data-clear-draft]")) {
        const item = activeWriting();
        localStorage.removeItem(draftKey(item));
        renderWriting();
      }
    });
    els.panel.addEventListener("input", (event) => {
      if (event.target.id !== "writingDraft") return;
      const item = activeWriting();
      localStorage.setItem(draftKey(item), event.target.value);
      updateWordCount();
    });
  }

  async function init() {
    els.panel = $("skillsPanel");
    loadProgress();
    bindEvents();
    try {
      const response = await fetch("/assets/english/data/skills-practice.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      state.data = await response.json();
      render();
    } catch (error) {
      els.panel.innerHTML = `<div class="loading-state">四科训练数据加载失败：${esc(error.message)}</div>`;
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
