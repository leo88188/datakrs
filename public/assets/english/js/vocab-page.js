(function () {
  "use strict";

  const state = {
    data: null,
    activeList: 1,
    query: "",
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

  function two(number) {
    return String(number).padStart(2, "0");
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
      showToast("当前浏览器不支持单词朗读");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(term);
    utterance.lang = "en-US";
    utterance.rate = 0.82;
    utterance.pitch = 1;
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

  function activeList() {
    if (!state.data) return null;
    return state.data.lists.find((item) => item.list === state.activeList) || state.data.lists[0];
  }

  function setActiveList(list) {
    const model = state.data && state.data.lists.find((item) => item.list === list);
    if (!model) return;
    state.activeList = model.list;
    state.query = "";
    els.search.value = "";
    render();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function render() {
    if (!state.data) return;
    const data = state.data;
    const currentList = activeList();
    const query = state.query.trim().toLowerCase();

    els.summary.textContent = `${data.meta.listCount} 个 List，${data.meta.wordCount} 个词条，按主题分组学习。`;
    els.listStat.textContent = `L${two(currentList.list)}`;
    els.wordStat.textContent = `${data.meta.wordCount} 词`;
    els.audioStat.textContent = `${data.audioTracks.length} 音频`;
    els.chapter.textContent = currentList.chapterName || "当前 List";
    els.title.textContent = `List ${two(currentList.list)}`;
    els.range.textContent = `${currentList.entries.length} 个词条，来自 Chapter ${currentList.chapter || "-"}`;

    if (!els.trackSelect.options.length) {
      els.trackSelect.innerHTML = data.audioTracks
        .map((track) => `<option value="${esc(track.url)}">${esc(track.title)}</option>`)
        .join("");
    }
    if (!els.audio.src && data.audioTracks[0]) {
      els.audio.src = data.audioTracks[0].url;
      els.trackSelect.value = data.audioTracks[0].url;
    }

    if (!els.listSelect.options.length) {
      els.listSelect.innerHTML = data.lists
        .map((item) => `<option value="${item.list}">List ${two(item.list)} · ${esc(item.chapterName || "词汇")}</option>`)
        .join("");
    }
    els.listSelect.value = String(currentList.list);
    els.prev.disabled = currentList.list <= 1;
    els.next.disabled = currentList.list >= data.meta.listCount;

    const words = query
      ? data.words.filter((item) => {
          return (
            item.word.toLowerCase().includes(query) ||
            item.definition.toLowerCase().includes(query) ||
            item.chapterName.includes(state.query.trim())
          );
        })
      : currentList.entries.map((item) => ({
          ...item,
          list: currentList.list,
          chapter: currentList.chapter,
          chapterName: currentList.chapterName,
        }));

    const heading = query
      ? `搜索结果 ${words.length} 条`
      : `${currentList.chapterName || "词汇"} · List ${currentList.list} · ${words.length} 词`;

    els.resultTitle.textContent = heading;
    els.visibleCount.textContent = query ? `${Math.min(words.length, 120)} / ${words.length}` : String(words.length);
    els.words.innerHTML = `
      ${words
        .slice(0, query ? 120 : 80)
        .map((word, index) => ({ ...word, displayIndex: index + 1 }))
        .map(
          (word) => `
            <article class="vocab-jing-card">
              <span class="vocab-card-index">${word.displayIndex}</span>
              <div>
                <strong>${esc(word.word)}</strong>
                <span>List ${two(word.list)}${word.pos ? ` · ${esc(word.pos)}` : ""}</span>
              </div>
              <button class="word-speak vocab-speak" type="button" data-term="${esc(word.word)}" aria-label="播放 ${esc(word.word)} 发音" title="播放发音"><span>play</span></button>
              <p>${esc(word.definition)}</p>
            </article>
          `
        )
        .join("")}
      ${words.length > (query ? 120 : 80) ? '<div class="vocab-more">结果较多，建议继续输入关键词缩小范围。</div>' : ""}
    `;
  }

  function bindEvents() {
    els.listSelect.addEventListener("change", () => {
      setActiveList(Number(els.listSelect.value));
    });

    els.prev.addEventListener("click", () => {
      setActiveList(Math.max(1, state.activeList - 1));
    });

    els.next.addEventListener("click", () => {
      setActiveList(Math.min(state.data.meta.listCount, state.activeList + 1));
    });

    els.search.addEventListener("input", () => {
      state.query = els.search.value;
      render();
    });

    els.clearSearch.addEventListener("click", () => {
      state.query = "";
      els.search.value = "";
      render();
    });

    els.trackSelect.addEventListener("change", () => {
      els.audio.src = els.trackSelect.value;
      els.audio.play().catch(() => {});
    });

    els.words.addEventListener("click", (event) => {
      const button = event.target.closest(".word-speak");
      if (!button) return;
      event.preventDefault();
      event.stopPropagation();
      speakTerm(button.dataset.term, button);
    });
  }

  async function init() {
    els.summary = $("standaloneVocabSummary");
    els.listStat = $("standaloneVocabListStat");
    els.wordStat = $("standaloneVocabWordStat");
    els.audioStat = $("standaloneVocabAudioStat");
    els.chapter = $("standaloneVocabChapter");
    els.title = $("standaloneVocabTitle");
    els.range = $("standaloneVocabRange");
    els.prev = $("standaloneVocabPrev");
    els.next = $("standaloneVocabNext");
    els.listSelect = $("standaloneVocabListSelect");
    els.trackSelect = $("standaloneVocabTrackSelect");
    els.audio = $("standaloneVocabAudio");
    els.search = $("standaloneVocabSearchInput");
    els.clearSearch = $("standaloneVocabClearSearch");
    els.resultTitle = $("standaloneVocabResultTitle");
    els.visibleCount = $("standaloneVocabVisibleCount");
    els.words = $("standaloneVocabWords");
    refreshVoices();
    if ("speechSynthesis" in window) {
      window.speechSynthesis.onvoiceschanged = refreshVoices;
    }
    bindEvents();

    try {
      const response = await fetch("/assets/english/data/vocab-jing.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      state.data = await response.json();
      render();
    } catch (error) {
      els.summary.textContent = `词汇真经数据加载失败：${error.message}`;
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
