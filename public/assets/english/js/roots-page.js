(function () {
  "use strict";

  const state = {
    data: null,
    filter: "all",
    query: "",
    onlyDue: false,
    mastered: new Set(),
    voices: [],
  };

  const els = {};
  const storageKey = "datakrs_roots_affixes_progress_v1";

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

  function speakTerm(term, button) {
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      showToast("当前浏览器不支持发音");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(term);
    utterance.lang = "en-US";
    utterance.rate = 0.82;
    const voice = pickEnglishVoice();
    if (voice) utterance.voice = voice;
    if (button) button.classList.add("playing");
    window.speechSynthesis.resume();
    utterance.onend = () => button && button.classList.remove("playing");
    utterance.onerror = () => {
      if (button) button.classList.remove("playing");
      showToast("发音没有启动，请确认 iPhone 未静音并再点一次");
    };
    try {
      window.speechSynthesis.speak(utterance);
    } catch (error) {
      if (button) button.classList.remove("playing");
      showToast("发音不可用，请稍后再试");
    }
  }

  function loadProgress() {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
      state.mastered = new Set(saved.mastered || []);
    } catch (error) {
      state.mastered = new Set();
    }
  }

  function saveProgress() {
    localStorage.setItem(storageKey, JSON.stringify({ mastered: Array.from(state.mastered) }));
  }

  function matchesQuery(item, query) {
    if (!query) return true;
    const haystack = [
      item.morpheme,
      item.meaning,
      item.memoryTip,
      item.typeLabel,
      ...item.examples.flatMap((example) => [example.word, example.meaning, example.phonetic]),
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(query.toLowerCase());
  }

  function filteredItems() {
    if (!state.data) return [];
    return state.data.items.filter((item) => {
      if (state.filter !== "all" && item.type !== state.filter) return false;
      if (state.onlyDue && state.mastered.has(item.id)) return false;
      return matchesQuery(item, state.query.trim());
    });
  }

  function updateSummary(items) {
    const meta = state.data.meta;
    els.summary.textContent = `${meta.rootCount} 个词根，${meta.prefixCount} 个前缀，${meta.suffixCount} 个后缀；共 ${meta.totalCount} 张记忆卡。`;
    els.progress.textContent = `${state.mastered.size} / ${meta.totalCount} 已掌握`;
    els.showDue.textContent = state.onlyDue ? "查看全部" : "只看未掌握";
    els.cards.dataset.count = String(items.length);
  }

  function render() {
    if (!state.data) return;
    const items = filteredItems();
    updateSummary(items);

    els.cards.innerHTML = `
      <div class="roots-result-heading">当前 ${items.length} 张</div>
      ${items
        .map((item) => {
          const mastered = state.mastered.has(item.id);
          return `
            <article class="roots-card${mastered ? " mastered" : ""}">
              <div class="roots-card-head">
                <span>${esc(item.typeLabel)}</span>
                <button class="roots-master-button" type="button" data-master-id="${esc(item.id)}">${mastered ? "已掌握" : "标记掌握"}</button>
              </div>
              <h2>${esc(item.morpheme)}</h2>
              <p class="roots-meaning">${esc(item.meaning)}</p>
              <p class="roots-tip">${esc(item.memoryTip)}</p>
              <div class="roots-examples">
                ${item.examples
                  .map(
                    (example) => `
                      <div class="roots-example">
                        <button class="word-speak roots-speak" type="button" data-term="${esc(example.word)}" aria-label="播放 ${esc(example.word)} 发音" title="播放发音"><span>play</span></button>
                        <div>
                          <strong>${esc(example.word)}</strong>
                          <em>${example.phonetic ? `/${esc(example.phonetic)}/` : "音标待补"}</em>
                          <p>${example.pos ? `<small>${esc(example.pos)}</small> ` : ""}${esc(example.meaning)}</p>
                        </div>
                      </div>
                    `
                  )
                  .join("")}
              </div>
            </article>
          `;
        })
        .join("")}
    `;
  }

  function bindEvents() {
    document.querySelectorAll("[data-roots-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll("[data-roots-filter]").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        state.filter = button.dataset.rootsFilter;
        render();
      });
    });

    els.search.addEventListener("input", () => {
      state.query = els.search.value;
      render();
    });

    els.showDue.addEventListener("click", () => {
      state.onlyDue = !state.onlyDue;
      render();
    });

    els.cards.addEventListener("click", (event) => {
      const speakButton = event.target.closest(".word-speak");
      if (speakButton) {
        event.preventDefault();
        speakTerm(speakButton.dataset.term, speakButton);
        return;
      }

      const masterButton = event.target.closest("[data-master-id]");
      if (!masterButton) return;
      const id = masterButton.dataset.masterId;
      if (state.mastered.has(id)) state.mastered.delete(id);
      else state.mastered.add(id);
      saveProgress();
      render();
    });
  }

  async function init() {
    els.summary = $("rootsSummary");
    els.search = $("rootsSearchInput");
    els.progress = $("rootsProgressText");
    els.showDue = $("rootsShowDue");
    els.cards = $("rootsCards");
    loadProgress();
    refreshVoices();
    if ("speechSynthesis" in window) {
      window.speechSynthesis.onvoiceschanged = refreshVoices;
    }
    bindEvents();

    try {
      const response = await fetch("/assets/english/data/roots-affixes.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      state.data = await response.json();
      render();
    } catch (error) {
      els.summary.textContent = `词根词缀数据加载失败：${error.message}`;
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
