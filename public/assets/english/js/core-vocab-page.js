(function () {
  "use strict";

  const storageKey = "datakrs_ielts_core_vocab_v1";
  const state = {
    data: null,
    mode: "theme",
    active: "全部",
    query: "",
    known: new Set(),
    unsure: new Set(),
    voices: [],
  };
  const els = {};

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

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
      state.known = new Set(saved.known || []);
      state.unsure = new Set(saved.unsure || []);
    } catch (error) {
      state.known = new Set();
      state.unsure = new Set();
    }
  }

  function saveState() {
    localStorage.setItem(
      storageKey,
      JSON.stringify({
        known: Array.from(state.known),
        unsure: Array.from(state.unsure),
      })
    );
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

  function refreshVoices() {
    if (!("speechSynthesis" in window)) return;
    state.voices = window.speechSynthesis.getVoices() || [];
  }

  function pickEnglishVoice() {
    if (!state.voices.length) refreshVoices();
    return (
      state.voices.find((voice) => /^en[-_](US|GB)/i.test(voice.lang)) ||
      state.voices.find((voice) => /^en/i.test(voice.lang)) ||
      null
    );
  }

  function speak(term, button) {
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      showToast("当前浏览器不支持系统朗读");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(term);
    utterance.lang = "en-US";
    utterance.rate = 0.82;
    const voice = pickEnglishVoice();
    if (voice) utterance.voice = voice;
    button.classList.add("playing");
    utterance.onend = () => button.classList.remove("playing");
    utterance.onerror = () => {
      button.classList.remove("playing");
      showToast("朗读被浏览器中断，请再点一次");
    };
    window.speechSynthesis.resume();
    window.speechSynthesis.speak(utterance);
  }

  function chips() {
    if (!state.data) return [];
    if (state.mode === "alpha") {
      return [{ letter: "全部", count: state.data.meta.wordCount }].concat(state.data.alphas);
    }
    if (state.mode === "review") {
      return [
        { name: "全部不熟", count: state.unsure.size },
        { name: "未标记", count: state.data.words.length - state.known.size - state.unsure.size },
        { name: "已掌握", count: state.known.size },
      ];
    }
    return [{ name: "全部", count: state.data.meta.wordCount }].concat(state.data.themes);
  }

  function filteredWords() {
    if (!state.data) return [];
    const query = state.query.trim().toLowerCase();
    return state.data.words.filter((word) => {
      const id = String(word.id);
      if (state.mode === "theme" && state.active !== "全部" && word.theme !== state.active) return false;
      if (state.mode === "alpha" && state.active !== "全部" && word.alpha !== state.active) return false;
      if (state.mode === "review") {
        if (state.active === "已掌握" && !state.known.has(id)) return false;
        if (state.active === "未标记" && (state.known.has(id) || state.unsure.has(id))) return false;
        if (state.active === "全部不熟" && !state.unsure.has(id)) return false;
      }
      if (!query) return true;
      return (
        word.term.toLowerCase().includes(query) ||
        word.definition.toLowerCase().includes(query) ||
        word.theme.includes(state.query.trim()) ||
        word.sentence.toLowerCase().includes(query) ||
        word.translation.includes(state.query.trim())
      );
    });
  }

  function renderChips() {
    els.chips.innerHTML = chips()
      .map((chip) => {
        const label = chip.name || chip.letter;
        const active = label === state.active ? " active" : "";
        return `<button class="core-chip${active}" type="button" data-core-chip="${esc(label)}">${esc(label)}<span>${chip.count}</span></button>`;
      })
      .join("");
  }

  function renderCards(words) {
    const limit = 160;
    els.list.innerHTML = words.length
      ? words
          .slice(0, limit)
          .map((word) => {
            const id = String(word.id);
            const known = state.known.has(id);
            const unsure = state.unsure.has(id);
            return `
              <article class="core-word-card${known ? " known" : ""}${unsure ? " unsure" : ""}">
                <div class="core-word-main">
                  <span class="core-word-alpha">${esc(word.alpha)}</span>
                  <div>
                    <h3>${esc(word.term)}</h3>
                    <p>${word.phonetic ? `/${esc(word.phonetic)}/` : ""}${word.phonetic && word.pos ? " · " : ""}${word.pos ? esc(word.pos) : ""}</p>
                  </div>
                  <button class="word-speak core-word-speak" type="button" data-speak="${esc(word.term)}" aria-label="播放 ${esc(word.term)} 发音"><span>play</span></button>
                </div>
                <p class="core-word-definition">${esc(word.definition)}</p>
                <div class="core-word-tags">
                  <span>${esc(word.theme)}</span>
                  <span>句 ${String(word.sentenceId).padStart(2, "0")}</span>
                </div>
                <details class="core-word-example">
                  <summary>例句</summary>
                  <p>${esc(word.sentence)}</p>
                  <small>${esc(word.translation)}</small>
                </details>
                <div class="core-word-actions">
                  <button type="button" data-known="${word.id}" class="${known ? "active" : ""}">认识</button>
                  <button type="button" data-unsure="${word.id}" class="${unsure ? "active" : ""}">不熟</button>
                </div>
              </article>
            `;
          })
          .join("") + (words.length > limit ? `<div class="vocab-more">当前显示前 ${limit} 个，使用搜索或分类可以更快定位。</div>` : "")
      : '<div class="empty-state">没有匹配的核心词。</div>';
  }

  function render() {
    if (!state.data) return;
    const words = filteredWords();
    els.summary.textContent = `${state.data.meta.wordCount} 个核心词，来自 100 句学习材料，适合先打基础再扩展主题词。`;
    els.total.textContent = `${state.data.meta.wordCount} 词`;
    els.known.textContent = `${state.known.size} 已掌握`;
    els.scope.textContent = state.mode === "alpha" ? "按 A-Z" : state.mode === "review" ? "复习" : "按主题";
    els.title.textContent = state.active;
    els.count.textContent = String(words.length);
    document.querySelectorAll("[data-core-mode]").forEach((button) => {
      button.classList.toggle("active", button.dataset.coreMode === state.mode);
    });
    renderChips();
    renderCards(words);
  }

  function bindEvents() {
    els.search.addEventListener("input", () => {
      state.query = els.search.value;
      render();
    });
    els.clear.addEventListener("click", () => {
      state.query = "";
      els.search.value = "";
      render();
    });
    document.querySelector(".core-mode-tabs").addEventListener("click", (event) => {
      const button = event.target.closest("[data-core-mode]");
      if (!button) return;
      state.mode = button.dataset.coreMode;
      state.active = state.mode === "review" ? "全部不熟" : "全部";
      render();
      els.chips.scrollLeft = 0;
    });
    els.chips.addEventListener("click", (event) => {
      const button = event.target.closest("[data-core-chip]");
      if (!button) return;
      state.active = button.dataset.coreChip;
      render();
    });
    document.querySelectorAll("[data-chip-scroll]").forEach((button) => {
      button.addEventListener("click", () => {
        const direction = button.dataset.chipScroll === "left" ? -1 : 1;
        els.chips.scrollBy({ left: direction * Math.max(180, els.chips.clientWidth * 0.8), behavior: "smooth" });
      });
    });
    els.list.addEventListener("click", (event) => {
      const speakButton = event.target.closest("[data-speak]");
      if (speakButton) {
        speak(speakButton.dataset.speak, speakButton);
        return;
      }
      const knownButton = event.target.closest("[data-known]");
      if (knownButton) {
        const id = knownButton.dataset.known;
        state.known.has(id) ? state.known.delete(id) : state.known.add(id);
        state.unsure.delete(id);
        saveState();
        render();
        return;
      }
      const unsureButton = event.target.closest("[data-unsure]");
      if (unsureButton) {
        const id = unsureButton.dataset.unsure;
        state.unsure.has(id) ? state.unsure.delete(id) : state.unsure.add(id);
        state.known.delete(id);
        saveState();
        render();
      }
    });
  }

  function boot() {
    els.summary = $("coreVocabSummary");
    els.total = $("coreVocabTotal");
    els.known = $("coreVocabKnown");
    els.search = $("coreVocabSearch");
    els.clear = $("coreVocabClear");
    els.chips = $("coreVocabChips");
    els.scope = $("coreVocabScope");
    els.title = $("coreVocabTitle");
    els.count = $("coreVocabCount");
    els.list = $("coreVocabList");
    loadState();
    bindEvents();
    refreshVoices();
    if ("speechSynthesis" in window) window.speechSynthesis.onvoiceschanged = refreshVoices;

    fetch("/assets/english/data/core-vocab.json?v=core-vocab-20260730")
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data) => {
        state.data = data;
        render();
      })
      .catch(() => {
        els.summary.textContent = "核心词数据加载失败，请刷新页面重试。";
      });
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
