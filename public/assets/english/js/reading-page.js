(function () {
  "use strict";

  const state = {
    data: null,
    activeId: "",
    topic: "all",
    query: "",
    fontSize: "normal",
    completed: new Set(),
    voices: [],
  };

  const els = {};
  const storageKey = "datakrs_reading_progress_v1";

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

  function speak(text, button) {
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      showToast("当前浏览器不支持英文朗读");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = text.split(/\s+/).length > 12 ? 0.9 : 0.82;
    const voice = pickEnglishVoice();
    if (voice) utterance.voice = voice;
    if (button) button.classList.add("playing");
    window.speechSynthesis.resume();
    utterance.onend = () => button && button.classList.remove("playing");
    utterance.onerror = () => {
      if (button) button.classList.remove("playing");
      showToast("朗读没有启动，请确认 iPhone 未静音并再点一次");
    };
    try {
      window.speechSynthesis.speak(utterance);
    } catch (error) {
      if (button) button.classList.remove("playing");
      showToast("朗读不可用，请稍后再试");
    }
  }

  function loadProgress() {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
      state.activeId = saved.activeId || "";
      state.fontSize = saved.fontSize || "normal";
      state.completed = new Set(saved.completed || []);
    } catch (error) {
      state.completed = new Set();
    }
  }

  function saveProgress() {
    localStorage.setItem(
      storageKey,
      JSON.stringify({
        activeId: state.activeId,
        fontSize: state.fontSize,
        completed: Array.from(state.completed),
      })
    );
  }

  function topics() {
    const set = new Set((state.data.articles || []).map((article) => article.topic));
    return ["all", ...Array.from(set)];
  }

  function activeArticle() {
    return state.data.articles.find((article) => article.id === state.activeId) || state.data.articles[0];
  }

  function articleHaystack(article) {
    return [
      article.title,
      article.topic,
      article.level,
      article.summary,
      ...article.paragraphs,
      ...article.keywords.flatMap((item) => [item.term, item.meaning, item.note]),
    ]
      .join(" ")
      .toLowerCase();
  }

  function filteredArticles() {
    const query = state.query.trim().toLowerCase();
    return state.data.articles.filter((article) => {
      if (state.topic !== "all" && article.topic !== state.topic) return false;
      if (!query) return true;
      return articleHaystack(article).includes(query);
    });
  }

  function renderTopicTabs() {
    els.topicTabs.innerHTML = topics()
      .map((topic) => {
        const active = topic === state.topic ? " active" : "";
        const label = topic === "all" ? "全部" : topic;
        return `<button class="vocab-chapter-tab${active}" type="button" data-topic="${esc(topic)}">${esc(label)}</button>`;
      })
      .join("");
  }

  function renderArticleList() {
    const articles = filteredArticles();
    if (articles.length && !articles.some((article) => article.id === state.activeId)) {
      state.activeId = articles[0].id;
    }
    els.articleList.innerHTML = articles
      .map((article, index) => {
        const active = article.id === state.activeId ? " active" : "";
        const done = state.completed.has(article.id) ? " done" : "";
        return `
          <button class="reading-article-chip${active}${done}" type="button" data-article-id="${esc(article.id)}">
            <span>${String(index + 1).padStart(2, "0")}</span>
            <strong>${esc(article.title)}</strong>
            <small>${esc(article.topic)} · ${esc(article.minutes)} min</small>
          </button>
        `;
      })
      .join("");
    if (!articles.length) {
      els.articleList.innerHTML = '<div class="reading-empty">没有匹配文章，换一个关键词试试。</div>';
    }
  }

  function renderArticle() {
    const article = activeArticle();
    if (!article) {
      els.article.innerHTML = '<div class="loading-state">没有可阅读的文章。</div>';
      return;
    }
    const completed = state.completed.has(article.id);
    els.article.classList.toggle("reading-large", state.fontSize === "large");
    els.article.innerHTML = `
      <div class="reading-article-head">
        <div>
          <div class="reading-tags">
            <span>${esc(article.topic)}</span>
            <span>${esc(article.level)}</span>
            <span>${esc(article.minutes)} min</span>
          </div>
          <h1>${esc(article.title)}</h1>
          <p>${esc(article.summary)}</p>
        </div>
        <button class="reading-complete-button${completed ? " active" : ""}" type="button" data-complete-article="${esc(article.id)}">
          ${completed ? "已读完" : "标记读完"}
        </button>
      </div>

      <section class="reading-passage">
        ${article.paragraphs
          .map(
            (paragraph, index) => `
              <p>
                <span class="reading-para-no">P${index + 1}</span>
                ${esc(paragraph)}
              </p>
            `
          )
          .join("")}
      </section>

      <section class="reading-keywords">
        <div class="reading-section-title">
          <h2>核心词汇</h2>
          <span>${article.keywords.length} 词</span>
        </div>
        <div class="reading-keyword-grid">
          ${article.keywords
            .map(
              (keyword) => `
                <article class="reading-keyword-card">
                  <div>
                    <strong>${esc(keyword.term)}</strong>
                    ${keyword.phonetic ? `<em>/${esc(keyword.phonetic)}/</em>` : ""}
                  </div>
                  <button class="word-speak reading-speak" type="button" data-speak="${esc(keyword.term)}" aria-label="播放 ${esc(keyword.term)} 发音" title="播放发音"><span>play</span></button>
                  <p>${esc(keyword.meaning)}</p>
                  <small>${esc(keyword.note)}</small>
                </article>
              `
            )
            .join("")}
        </div>
      </section>

      <section class="reading-questions">
        <div class="reading-section-title">
          <h2>题型训练</h2>
          <span>${article.questions.length} 题</span>
        </div>
        ${article.questions
          .map(
            (question, index) => `
              <article class="reading-question-card">
                <div class="reading-question-meta">
                  <span>Q${index + 1}</span>
                  <strong>${esc(question.type)}</strong>
                </div>
                <h3>${esc(question.question)}</h3>
                ${
                  question.options
                    ? `<div class="reading-options">${question.options.map((option) => `<span>${esc(option)}</span>`).join("")}</div>`
                    : ""
                }
                <button class="reading-answer-toggle" type="button" data-answer-toggle="${esc(question.id)}">查看答案</button>
                <div class="reading-answer" id="answer-${esc(question.id)}">
                  <strong>${esc(question.answer)}</strong>
                  <p>${esc(question.explanation)}</p>
                </div>
              </article>
            `
          )
          .join("")}
      </section>
    `;
    saveProgress();
  }

  function render() {
    if (!state.data) return;
    renderTopicTabs();
    renderArticleList();
    renderArticle();
    document.querySelectorAll("[data-font-size]").forEach((button) => {
      button.classList.toggle("active", button.dataset.fontSize === state.fontSize);
    });
  }

  function bindEvents() {
    els.search.addEventListener("input", () => {
      state.query = els.search.value;
      render();
    });

    els.clearSearch.addEventListener("click", () => {
      state.query = "";
      els.search.value = "";
      render();
    });

    els.topicTabs.addEventListener("click", (event) => {
      const button = event.target.closest("[data-topic]");
      if (!button) return;
      state.topic = button.dataset.topic;
      render();
    });

    els.articleList.addEventListener("click", (event) => {
      const button = event.target.closest("[data-article-id]");
      if (!button) return;
      state.activeId = button.dataset.articleId;
      render();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    document.querySelectorAll("[data-font-size]").forEach((button) => {
      button.addEventListener("click", () => {
        state.fontSize = button.dataset.fontSize;
        render();
      });
    });

    els.article.addEventListener("click", (event) => {
      const speakButton = event.target.closest("[data-speak]");
      if (speakButton) {
        event.preventDefault();
        speak(speakButton.dataset.speak, speakButton);
        return;
      }

      const completeButton = event.target.closest("[data-complete-article]");
      if (completeButton) {
        const id = completeButton.dataset.completeArticle;
        if (state.completed.has(id)) state.completed.delete(id);
        else state.completed.add(id);
        render();
        return;
      }

      const answerButton = event.target.closest("[data-answer-toggle]");
      if (!answerButton) return;
      const answer = document.getElementById(`answer-${answerButton.dataset.answerToggle}`);
      if (!answer) return;
      answer.classList.toggle("show");
      answerButton.textContent = answer.classList.contains("show") ? "收起答案" : "查看答案";
    });
  }

  async function init() {
    els.search = $("readingArticleSearch");
    els.clearSearch = $("readingClearSearch");
    els.topicTabs = $("readingTopicTabs");
    els.articleList = $("readingArticleList");
    els.article = $("readingArticle");
    loadProgress();
    refreshVoices();
    if ("speechSynthesis" in window) {
      window.speechSynthesis.onvoiceschanged = refreshVoices;
    }
    bindEvents();

    try {
      const response = await fetch("/assets/english/data/reading-articles.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      state.data = await response.json();
      if (!state.activeId || !state.data.articles.some((article) => article.id === state.activeId)) {
        state.activeId = state.data.articles[0] && state.data.articles[0].id;
      }
      render();
    } catch (error) {
      els.article.innerHTML = `<div class="loading-state">阅读文章加载失败：${esc(error.message)}</div>`;
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
