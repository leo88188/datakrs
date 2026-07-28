(function () {
  "use strict";

  const state = {
    data: null,
    vocabData: null,
    readingData: null,
    sentences: [],
    days: [],
    activeId: 1,
    activeDay: 1,
    activeVocabList: 1,
    activeReadingDay: 1,
    vocabQuery: "",
    readingQuery: "",
    query: "",
    wordFilter: "all",
    done: new Set(),
    favorite: new Set(),
    drills: {},
    voices: [],
  };

  const els = {};
  const storageKey = "datakrs_ielts100_progress_v1";

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

  function audioUrl(sentence) {
    const file = sentence.audio.replace(/^audio\//, "");
    return state.data.assetConfig.audioBase + file;
  }

  function videoUrl(day) {
    return state.data.assetConfig.videoBase + `day${two(day)}.mp4`;
  }

  function setDeferredMedia(media, url) {
    if (!media || !url) return;
    if (media.dataset.src === url && !media.getAttribute("src")) return;
    if (media.dataset.src !== url) {
      media.pause();
      media.removeAttribute("src");
      media.load();
    }
    media.dataset.src = url;
  }

  function loadDeferredMedia(media) {
    if (!media || media.getAttribute("src") || !media.dataset.src) return;
    media.src = media.dataset.src;
    media.load();
  }

  function bindDeferredMedia(media) {
    if (!media) return;
    ["pointerdown", "touchstart", "keydown"].forEach((eventName) => {
      media.addEventListener(eventName, () => loadDeferredMedia(media), { passive: true });
    });
    media.addEventListener("play", () => loadDeferredMedia(media));
  }

  function activeSentence() {
    return state.sentences.find((item) => item.id === state.activeId) || state.sentences[0];
  }

  function activeDay() {
    return state.days.find((item) => item.day === state.activeDay) || state.days[0];
  }

  function activeVocabList() {
    if (!state.vocabData) return null;
    return state.vocabData.lists.find((item) => item.list === state.activeVocabList) || state.vocabData.lists[0];
  }

  function readingGroups() {
    if (!state.readingData) return [];
    const size = 20;
    const phrases = state.readingData.phrases || [];
    return Array.from({ length: Math.ceil(phrases.length / size) }, (_, index) => {
      const start = index * size;
      return {
        day: index + 1,
        start: start + 1,
        end: Math.min(start + size, phrases.length),
        phrases: phrases.slice(start, start + size),
      };
    });
  }

  function loadProgress() {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
      state.activeId = saved.activeId || 1;
      state.activeDay = saved.activeDay || 1;
      state.done = new Set(saved.done || []);
      state.favorite = new Set(saved.favorite || []);
      state.drills = saved.drills || {};
    } catch (error) {
      state.done = new Set();
      state.favorite = new Set();
      state.drills = {};
    }
  }

  function saveProgress() {
    localStorage.setItem(
      storageKey,
      JSON.stringify({
        activeId: state.activeId,
        activeDay: state.activeDay,
        done: Array.from(state.done),
        favorite: Array.from(state.favorite),
        drills: state.drills,
      })
    );
  }

  function filteredSentences() {
    const query = state.query.trim().toLowerCase();
    const base = state.sentences.filter((item) => item.day === state.activeDay || query);
    if (!query) return base;
    return base.filter((item) => {
      if (item.english.toLowerCase().includes(query)) return true;
      if (item.chinese.includes(state.query.trim())) return true;
      return item.words.some((word) => {
        return (
          word.term.toLowerCase().includes(query) ||
          word.definition.includes(state.query.trim()) ||
          word.category.includes(state.query.trim())
        );
      });
    });
  }

  function groupedWords(sentence) {
    const groups = new Map();
    sentence.words
      .filter((word) => state.wordFilter === "all" || word.section === state.wordFilter)
      .forEach((word) => {
        const key = word.category || (word.section === "core" ? "核心词表" : "主题归纳");
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(word);
      });
    return Array.from(groups.entries());
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

  function scrollStudyPanelTo(selector) {
    const panel = document.querySelector(".study-panel");
    const target = selector ? document.querySelector(selector) : null;
    if (!panel) return;

    if (!target) {
      panel.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    const panelRect = panel.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const top = panel.scrollTop + targetRect.top - panelRect.top - 10;
    panel.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
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
    utterance.volume = 1;
    const voice = pickEnglishVoice();
    if (voice) utterance.voice = voice;
    if (button) button.classList.add("playing");
    window.speechSynthesis.resume();
    utterance.onend = () => button && button.classList.remove("playing");
    utterance.onerror = () => {
      if (button) button.classList.remove("playing");
      showToast("单词发音没有启动，请确认 iPhone 未静音并再点一次");
    };
    try {
      window.speechSynthesis.speak(utterance);
    } catch (error) {
      if (button) button.classList.remove("playing");
      showToast("单词发音不可用，请稍后再试");
    }
  }

  function updateProgress() {
    const done = state.done.size;
    const percent = Math.round((done / 100) * 100);
    els.progressText.textContent = `${done} / 100`;
    els.progressPercent.textContent = `${percent}%`;
    els.progressBar.style.width = `${percent}%`;
  }

  function renderVocabJing() {
    if (!state.vocabData) {
      els.vocabJingSummary.textContent = "词汇真经数据加载失败，请刷新重试。";
      return;
    }

    const data = state.vocabData;
    const currentList = activeVocabList();
    const query = state.vocabQuery.trim().toLowerCase();
    els.vocabJingSummary.textContent = `${data.meta.listCount} 个 List，${data.meta.wordCount} 个词条；已整理为可检索词卡。`;

    els.vocabTrackSelect.innerHTML = data.audioTracks
      .map((track) => `<option value="${esc(track.url)}">${esc(track.title)}</option>`)
      .join("");
    if (!els.vocabJingAudio.dataset.src && data.audioTracks[0]) {
      setDeferredMedia(els.vocabJingAudio, data.audioTracks[0].url);
      els.vocabTrackSelect.value = data.audioTracks[0].url;
    }

    els.vocabListButtons.innerHTML = data.lists
      .map((item) => {
        const active = item.list === state.activeVocabList ? " active" : "";
        return `<button class="vocab-list-button${active}" type="button" data-vocab-list="${item.list}">L${two(item.list)}</button>`;
      })
      .join("");

    const words = query
      ? data.words.filter((item) => {
          return (
            item.word.toLowerCase().includes(query) ||
            item.definition.toLowerCase().includes(query) ||
            item.chapterName.includes(state.vocabQuery.trim())
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

    els.vocabJingWords.innerHTML = `
      <div class="vocab-result-heading">${esc(heading)}</div>
      ${words
        .slice(0, 160)
        .map((word, index) => ({ ...word, displayIndex: index + 1 }))
        .map(
          (word) => `
            <article class="vocab-jing-card">
              <span class="vocab-card-index">${word.displayIndex}</span>
              <div>
                <strong>${esc(word.word)}</strong>
                <span>List ${two(word.list)}${word.pos ? ` · ${esc(word.pos)}` : ""}</span>
              </div>
              <button class="word-speak vocab-speak" type="button" data-term="${esc(word.word)}" aria-label="播放 ${esc(word.word)} 发音"><span>play</span></button>
              <p>${esc(word.definition)}</p>
            </article>
          `
        )
        .join("")}
      ${words.length > 160 ? '<div class="vocab-more">结果较多，建议继续输入关键词缩小范围。</div>' : ""}
    `;
  }

  function renderReading() {
    if (!state.readingData) {
      els.readingSummary.textContent = "阅读短语数据加载失败，请刷新重试。";
      els.readingSourceNote.textContent = "";
      return;
    }

    const data = state.readingData;
    const groups = readingGroups();
    const currentGroup = groups.find((item) => item.day === state.activeReadingDay) || groups[0];
    const query = state.readingQuery.trim().toLowerCase();

    els.readingSummary.textContent = `${data.meta.phraseCount} 条高频短语，按 5 组学习，每组 20 条；支持检索和英文朗读。`;
    els.readingSourceNote.innerHTML = `
      <strong>${esc(data.readingBook.title)}</strong>
      <span>${esc(data.readingBook.pageCount || 0)} 页本地资料已记录；网页不加载原文件，也不展示页面图片。</span>
    `;

    els.readingDayButtons.innerHTML = groups
      .map((group) => {
        const active = group.day === state.activeReadingDay ? " active" : "";
        return `<button class="vocab-list-button${active}" type="button" data-reading-day="${group.day}">R${two(group.day)} ${group.start}-${group.end}</button>`;
      })
      .join("");

    const phrases = query
      ? data.phrases.filter((item) => {
          return item.phrase.toLowerCase().includes(query) || item.meaning.includes(state.readingQuery.trim());
        })
      : currentGroup.phrases;

    const heading = query ? `搜索结果 ${phrases.length} 条` : `第 ${currentGroup.day} 组 · ${currentGroup.start}-${currentGroup.end}`;

    els.readingPhraseCards.innerHTML = `
      <div class="vocab-result-heading">${esc(heading)}</div>
      ${phrases
        .map(
          (item) => `
            <article class="reading-phrase-card">
              <span class="reading-phrase-id">${two(item.id)}</span>
              <div>
                <strong>${esc(item.phrase)}</strong>
                <p>${esc(item.meaning)}</p>
              </div>
              <button class="word-speak reading-speak" type="button" data-term="${esc(item.phrase)}" aria-label="播放 ${esc(item.phrase)} 发音" title="播放发音"><span>play</span></button>
            </article>
          `
        )
        .join("")}
    `;
  }

  function renderDays() {
    els.dayButtons.innerHTML = state.days
      .map((day) => {
        const done = day.sentenceIds.filter((id) => state.done.has(id)).length;
        const active = day.day === state.activeDay ? " active" : "";
        return `<button class="day-button${active}" type="button" data-day="${day.day}">D${two(day.day)} ${done}/${day.sentenceIds.length}</button>`;
      })
      .join("");
  }

  function renderSentenceList() {
    const items = filteredSentences();
    els.resultCount.textContent = String(items.length);
    els.sentenceList.innerHTML = items
      .map((item) => {
        const active = item.id === state.activeId ? " active" : "";
        const done = state.done.has(item.id) ? "已掌握" : "";
        const fav = state.favorite.has(item.id) ? "重点" : "";
        return `
          <button class="sentence-item${active}" type="button" data-id="${item.id}">
            <span class="sentence-no">${two(item.id)}</span>
            <span class="sentence-preview">
              <strong>${esc(item.english)}</strong>
              <span>${esc(item.chinese)}</span>
            </span>
            <span class="sentence-flags">
              <span>D${two(item.day)}</span>
              <span>${done || fav}</span>
            </span>
          </button>
        `;
      })
      .join("");
  }

  function renderWords(sentence) {
    const groups = groupedWords(sentence);
    els.wordGroups.innerHTML = groups
      .map(([category, words]) => {
        return `
          <section class="word-group">
            <div class="word-group-title">
              <strong>${esc(category)}</strong>
              <span>${words.length} 词条</span>
            </div>
            <div class="word-cards">
              ${words
                .map((word) => {
                  const notes = (word.notes || []).slice(0, 3);
                  return `
                    <article class="word-card">
                      <div class="word-head">
                        <div>
                          <strong>${esc(word.term)}</strong>
                          ${word.phonetic ? `<em>/${esc(word.phonetic)}/</em>` : ""}
                        </div>
                        <button class="word-speak" type="button" data-term="${esc(word.term)}" aria-label="播放 ${esc(word.term)} 发音" title="播放发音">
                          <span>play</span>
                        </button>
                      </div>
                      <p>${word.pos ? `<small>${esc(word.pos)}</small> ` : ""}${esc(word.definition)}</p>
                      ${
                        notes.length
                          ? `<ul>${notes.map((note) => `<li>${esc(note)}</li>`).join("")}</ul>`
                          : ""
                      }
                    </article>
                  `;
                })
                .join("")}
            </div>
          </section>
        `;
      })
      .join("");
  }

  function renderStudy() {
    const sentence = activeSentence();
    state.activeDay = sentence.day;
    const day = activeDay();

    els.sentenceBadge.textContent = `Sentence ${two(sentence.id)}`;
    els.dayBadge.textContent = `第${two(sentence.day)}天`;
    els.wordCountBadge.textContent = `${sentence.words.length} 词条`;
    els.englishSentence.textContent = sentence.english;
    els.chineseSentence.textContent = sentence.chinese;
    els.grammarNote.textContent = sentence.grammar || "当前句子未提取到语法笔记。";
    els.wordSummary.textContent = `核心词 ${sentence.wordStats.core} 个，主题扩展 ${sentence.wordStats.theme} 个。`;
    setDeferredMedia(els.sentenceAudio, audioUrl(sentence));
    els.audioStatus.textContent = "";
    els.sentenceAudio.loop = els.loopAudio.checked;
    els.sentenceAudio.playbackRate = Number(els.playbackRate.value);
    els.markDone.textContent = state.done.has(sentence.id) ? "取消已掌握" : "标记已掌握";
    els.toggleFavorite.textContent = state.favorite.has(sentence.id) ? "取消重点" : "加入重点";
    els.toggleFavorite.classList.toggle("active", state.favorite.has(sentence.id));

    els.videoTitle.textContent = `第${two(day.day)}天精讲`;
    els.videoRange.textContent = day.start && day.end ? `Sentence ${two(day.start)}-${two(day.end)}` : "";
    setDeferredMedia(els.dayVideo, videoUrl(sentence.day));

    document.querySelectorAll("[data-drill]").forEach((checkbox) => {
      const key = `${sentence.id}:${checkbox.dataset.drill}`;
      checkbox.checked = Boolean(state.drills[key]);
    });

    renderWords(sentence);
    renderDays();
    renderSentenceList();
    updateProgress();
    saveProgress();
  }

  function selectSentence(id, autoplay) {
    const sentence = state.sentences.find((item) => item.id === id);
    if (!sentence) return;
    state.activeId = sentence.id;
    state.activeDay = sentence.day;
    renderStudy();
    if (autoplay) {
      loadDeferredMedia(els.sentenceAudio);
      els.sentenceAudio.play().catch(() => {});
    }
  }

  function bindEvents() {
    els.searchInput.addEventListener("input", () => {
      state.query = els.searchInput.value;
      renderSentenceList();
    });

    els.clearSearch.addEventListener("click", () => {
      state.query = "";
      els.searchInput.value = "";
      renderSentenceList();
    });

    els.dayButtons.addEventListener("click", (event) => {
      const button = event.target.closest("[data-day]");
      if (!button) return;
      const day = Number(button.dataset.day);
      const model = state.days.find((item) => item.day === day);
      if (!model || !model.sentenceIds.length) return;
      state.activeDay = day;
      selectSentence(model.sentenceIds[0], false);
    });

    els.sentenceList.addEventListener("click", (event) => {
      const button = event.target.closest("[data-id]");
      if (button) selectSentence(Number(button.dataset.id), false);
    });

    els.prevSentence.addEventListener("click", () => selectSentence(Math.max(1, state.activeId - 1), false));
    els.nextSentence.addEventListener("click", () => selectSentence(Math.min(100, state.activeId + 1), false));

    els.loopAudio.addEventListener("change", () => {
      els.sentenceAudio.loop = els.loopAudio.checked;
    });

    els.playbackRate.addEventListener("change", () => {
      els.sentenceAudio.playbackRate = Number(els.playbackRate.value);
    });

    els.markDone.addEventListener("click", () => {
      if (state.done.has(state.activeId)) state.done.delete(state.activeId);
      else state.done.add(state.activeId);
      renderStudy();
    });

    els.toggleFavorite.addEventListener("click", () => {
      if (state.favorite.has(state.activeId)) state.favorite.delete(state.activeId);
      else state.favorite.add(state.activeId);
      renderStudy();
    });

    document.querySelectorAll("[data-word-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll("[data-word-filter]").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        state.wordFilter = button.dataset.wordFilter;
        renderWords(activeSentence());
      });
    });

    document.querySelectorAll("[data-panel-trigger]").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll("[data-panel-trigger]").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        if (button.dataset.panelTrigger === "learn") {
          scrollStudyPanelTo(null);
        }
        if (button.dataset.panelTrigger === "words") {
          scrollStudyPanelTo(".word-section");
        }
        if (button.dataset.panelTrigger === "jing") {
          window.location.href = "/english-vocab.html";
          return;
        }
        if (button.dataset.panelTrigger === "roots") {
          window.location.href = "/english-roots.html";
          return;
        }
        if (button.dataset.panelTrigger === "reading") {
          window.location.href = "/english-reading.html";
          return;
        }
        if (button.dataset.panelTrigger === "video") {
          document.querySelector(".media-panel").classList.add("active-mobile");
          document.querySelector(".media-panel").scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
          document.querySelector(".media-panel").classList.remove("active-mobile");
        }
      });
    });

    document.querySelectorAll("[data-drill]").forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        const key = `${state.activeId}:${checkbox.dataset.drill}`;
        state.drills[key] = checkbox.checked;
        saveProgress();
      });
    });

    els.wordGroups.addEventListener("click", (event) => {
      const button = event.target.closest(".word-speak");
      if (!button) return;
      event.preventDefault();
      event.stopPropagation();
      speakTerm(button.dataset.term, button);
    });

    els.vocabJingWords.addEventListener("click", (event) => {
      const button = event.target.closest(".word-speak");
      if (!button) return;
      event.preventDefault();
      event.stopPropagation();
      speakTerm(button.dataset.term, button);
    });

    els.vocabListButtons.addEventListener("click", (event) => {
      const button = event.target.closest("[data-vocab-list]");
      if (!button) return;
      state.activeVocabList = Number(button.dataset.vocabList);
      state.vocabQuery = "";
      els.vocabSearchInput.value = "";
      renderVocabJing();
    });

    els.vocabSearchInput.addEventListener("input", () => {
      state.vocabQuery = els.vocabSearchInput.value;
      renderVocabJing();
    });

    els.vocabTrackSelect.addEventListener("change", () => {
      setDeferredMedia(els.vocabJingAudio, els.vocabTrackSelect.value);
    });

    els.readingDayButtons.addEventListener("click", (event) => {
      const button = event.target.closest("[data-reading-day]");
      if (!button) return;
      state.activeReadingDay = Number(button.dataset.readingDay);
      state.readingQuery = "";
      els.readingSearchInput.value = "";
      renderReading();
    });

    els.readingSearchInput.addEventListener("input", () => {
      state.readingQuery = els.readingSearchInput.value;
      renderReading();
    });

    els.readingPhraseCards.addEventListener("click", (event) => {
      const button = event.target.closest(".word-speak");
      if (!button) return;
      event.preventDefault();
      event.stopPropagation();
      speakTerm(button.dataset.term, button);
    });

    els.sentenceAudio.addEventListener("ended", () => {
      if (!els.loopAudio.checked && state.activeId < 100) selectSentence(state.activeId + 1, false);
    });

    els.sentenceAudio.addEventListener("loadstart", () => {
      els.audioStatus.textContent = "音频准备中...";
    });

    els.sentenceAudio.addEventListener("canplay", () => {
      els.audioStatus.textContent = "";
    });

    els.sentenceAudio.addEventListener("error", () => {
      const code = els.sentenceAudio.error ? els.sentenceAudio.error.code : 0;
      const messages = {
        1: "音频加载已取消",
        2: "网络中断，音频没有加载成功",
        3: "音频解码失败",
        4: "音频地址不可用或权限被拦截",
      };
      els.audioStatus.textContent = messages[code] || "音频播放失败，请刷新后重试";
    });

    bindDeferredMedia(els.sentenceAudio);
    bindDeferredMedia(els.vocabJingAudio);
    bindDeferredMedia(els.dayVideo);
  }

  function cacheElements() {
    [
      "loadingState",
      "studyCard",
      "searchInput",
      "clearSearch",
      "dayButtons",
      "progressText",
      "resultCount",
      "sentenceList",
      "sentenceBadge",
      "dayBadge",
      "wordCountBadge",
      "englishSentence",
      "chineseSentence",
      "sentenceAudio",
      "audioStatus",
      "prevSentence",
      "nextSentence",
      "loopAudio",
      "playbackRate",
      "markDone",
      "toggleFavorite",
      "grammarNote",
      "wordSummary",
      "wordGroups",
      "vocabJingSummary",
      "vocabTrackSelect",
      "vocabJingAudio",
      "vocabSearchInput",
      "vocabListButtons",
      "vocabJingWords",
      "readingSummary",
      "readingSourceNote",
      "readingSearchInput",
      "readingDayButtons",
      "readingPhraseCards",
      "progressPercent",
      "progressBar",
      "videoTitle",
      "videoRange",
      "dayVideo",
    ].forEach((id) => {
      els[id] = $(id);
    });
  }

  async function init() {
    cacheElements();
    loadProgress();
    refreshVoices();
    if ("speechSynthesis" in window) {
      window.speechSynthesis.onvoiceschanged = refreshVoices;
    }
    bindEvents();

    try {
      const response = await fetch("/assets/english/data/ielts100.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      state.data = await response.json();
      state.sentences = state.data.sentences;
      state.days = state.data.days;
      fetch("/assets/english/data/vocab-jing.json", { cache: "no-cache" })
        .then((res) => (res.ok ? res.json() : Promise.reject(new Error(`HTTP ${res.status}`))))
        .then((data) => {
          state.vocabData = data;
          renderVocabJing();
        })
        .catch(() => {
          els.vocabJingSummary.textContent = "词汇真经数据暂时不可用。";
        });
      fetch("/assets/english/data/reading-phrases.json", { cache: "no-cache" })
        .then((res) => (res.ok ? res.json() : Promise.reject(new Error(`HTTP ${res.status}`))))
        .then((data) => {
          state.readingData = data;
          renderReading();
        })
        .catch(() => {
          els.readingSummary.textContent = "阅读短语数据暂时不可用。";
          els.readingSourceNote.textContent = "";
        });
      if (!state.sentences.some((item) => item.id === state.activeId)) state.activeId = 1;
      state.activeDay = activeSentence().day;
      els.loadingState.classList.add("hidden");
      els.studyCard.classList.remove("hidden");
      renderStudy();
    } catch (error) {
      els.loadingState.textContent = `学习数据加载失败：${error.message}`;
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
