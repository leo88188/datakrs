(function () {
  "use strict";

  const state = {
    data: null,
    activeId: "",
    topic: "all",
    level: "all",
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

  function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
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

  function closeKeywordInfo() {
    const panel = document.querySelector(".reading-word-popover");
    if (panel) panel.classList.remove("show");
  }

  function showKeywordInfo(keyword) {
    let panel = document.querySelector(".reading-word-popover");
    if (!panel) {
      panel = document.createElement("div");
      panel.className = "reading-word-popover";
      document.body.appendChild(panel);
    }
    panel.innerHTML = `
      <div class="reading-word-popover-head">
        <div>
          <strong>${esc(keyword.term)}</strong>
          ${keyword.phonetic ? `<em>/${esc(keyword.phonetic)}/</em>` : ""}
        </div>
        <button type="button" data-close-keyword>关闭</button>
      </div>
      <p>${esc(keyword.meaning)}</p>
      <small>${esc(keyword.note || "阅读时注意它所在的搭配和句子功能。")}</small>
    `;
    panel.classList.add("show");
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

  function levelLabel(level) {
    const labels = {
      all: "全部难度",
      band5: "Band 5",
      band6: "Band 6",
      band7: "Band 7",
      band8: "Band 8-9",
    };
    return labels[level] || level;
  }

  function levels() {
    const order = ["band5", "band6", "band7", "band8"];
    const set = new Set((state.data.articles || []).map((article) => article.bandGroup).filter(Boolean));
    return ["all", ...order.filter((level) => set.has(level))];
  }

  function activeArticle() {
    return state.data.articles.find((article) => article.id === state.activeId) || state.data.articles[0];
  }

  function activeArticlePosition() {
    const articles = filteredArticles();
    const index = articles.findIndex((article) => article.id === state.activeId);
    return {
      articles,
      index: index >= 0 ? index : 0,
    };
  }

  function articleHaystack(article) {
    return [
      article.title,
      article.topic,
      article.level,
      article.summary,
      ...article.paragraphs,
      ...(article.translations || []),
      ...article.keywords.flatMap((item) => [item.term, item.meaning, item.note]),
    ]
      .join(" ")
      .toLowerCase();
  }

  function filteredArticles() {
    const query = state.query.trim().toLowerCase();
    return state.data.articles.filter((article) => {
      if (state.topic !== "all" && article.topic !== state.topic) return false;
      if (state.level !== "all" && article.bandGroup !== state.level) return false;
      if (!query) return true;
      return articleHaystack(article).includes(query);
    });
  }

  function keywordMap(article) {
    const map = new Map();
    article.keywords.forEach((keyword) => {
      map.set(keyword.term.toLowerCase(), keyword);
    });
    return map;
  }

  function renderParagraphText(paragraph, article) {
    const keywords = article.keywords
      .map((keyword) => keyword.term)
      .filter((term) => term && term.length > 2)
      .sort((a, b) => b.length - a.length);
    if (!keywords.length) return esc(paragraph);
    const map = keywordMap(article);
    const pattern = new RegExp(`\\b(${keywords.map(escapeRegExp).join("|")})\\b`, "gi");
    let cursor = 0;
    let html = "";
    paragraph.replace(pattern, (match, term, offset) => {
      html += esc(paragraph.slice(cursor, offset));
      const keyword = map.get(String(term).toLowerCase());
      html += keyword
        ? `<button class="reading-inline-word" type="button" data-keyword="${esc(keyword.term)}">${esc(match)}</button>`
        : esc(match);
      cursor = offset + match.length;
      return match;
    });
    html += esc(paragraph.slice(cursor));
    return html;
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

  function renderLevelTabs() {
    els.levelTabs.innerHTML = levels()
      .map((level) => {
        const active = level === state.level ? " active" : "";
        return `<button class="vocab-chapter-tab${active}" type="button" data-level="${esc(level)}">${esc(levelLabel(level))}</button>`;
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
            <small>${esc(article.topic)} · ${esc(levelLabel(article.bandGroup))} · ${esc(article.minutes)} min</small>
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
    const position = activeArticlePosition();
    const currentNo = position.index + 1;
    const total = position.articles.length;
    const hasPrev = position.index > 0;
    const hasNext = position.index >= 0 && position.index < total - 1;
    els.article.classList.toggle("reading-large", state.fontSize === "large");
    els.article.innerHTML = `
      <div class="reading-article-head">
        <div>
          <div class="reading-tags">
            <span>${esc(article.topic)}</span>
            <span>${esc(article.level)}</span>
            <span>${esc(article.minutes)} min</span>
            <span class="reading-progress-pill">${esc(currentNo)} / ${esc(total)}</span>
          </div>
          <h1>${esc(article.title)}</h1>
          <p>${esc(article.summary)}</p>
        </div>
        <div class="reading-article-actions">
          <button class="reading-list-jump" type="button" data-scroll-reading-list>文章目录</button>
          <button class="reading-nav-button" type="button" data-reading-nav="prev"${hasPrev ? "" : " disabled"}>上一篇</button>
          <button class="reading-nav-button primary" type="button" data-reading-nav="next"${hasNext ? "" : " disabled"}>下一篇</button>
          <button class="reading-complete-button${completed ? " active" : ""}" type="button" data-complete-article="${esc(article.id)}">
            ${completed ? "已读完" : "标记读完"}
          </button>
        </div>
      </div>

      <section class="reading-passage">
        ${article.paragraphs
          .map(
            (paragraph, index) => `
              <div class="reading-paragraph-block">
                <p>
                  <span class="reading-para-no">P${index + 1}</span>
                  ${renderParagraphText(paragraph, article)}
                </p>
                ${
                  article.translations && article.translations[index]
                    ? `<p class="reading-translation">${esc(article.translations[index])}</p>`
                    : ""
                }
              </div>
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
                  <button class="reading-keyword-detail" type="button" data-keyword="${esc(keyword.term)}">查看解释</button>
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

      <nav class="reading-bottom-nav" aria-label="阅读篇章导航">
        <button type="button" data-reading-nav="prev"${hasPrev ? "" : " disabled"}>上一篇</button>
        <button type="button" data-scroll-reading-list>文章目录</button>
        <button type="button" data-reading-nav="next"${hasNext ? "" : " disabled"}>下一篇</button>
      </nav>
    `;
    saveProgress();
  }

  function render() {
    if (!state.data) return;
    renderTopicTabs();
    renderLevelTabs();
    renderArticleList();
    renderArticle();
    document.querySelectorAll("[data-font-size]").forEach((button) => {
      button.classList.toggle("active", button.dataset.fontSize === state.fontSize);
    });
  }

  function scrollToElement(element) {
    if (!element) return;
    const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
    window.requestAnimationFrame(() => {
      element.scrollIntoView({ behavior, block: "start" });
    });
  }

  function switchArticle(direction) {
    const position = activeArticlePosition();
    if (!position.articles.length) return;
    const nextIndex = direction === "prev" ? position.index - 1 : position.index + 1;
    const nextArticle = position.articles[nextIndex];
    if (!nextArticle) return;
    state.activeId = nextArticle.id;
    render();
    const activeChip = els.articleList.querySelector(".reading-article-chip.active");
    if (activeChip) activeChip.scrollIntoView({ block: "nearest" });
    scrollToElement(els.article);
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

    els.levelTabs.addEventListener("click", (event) => {
      const button = event.target.closest("[data-level]");
      if (!button) return;
      state.level = button.dataset.level;
      render();
    });

    els.articleList.addEventListener("click", (event) => {
      const button = event.target.closest("[data-article-id]");
      if (!button) return;
      state.activeId = button.dataset.articleId;
      render();
      scrollToElement(els.article);
    });

    document.querySelectorAll("[data-font-size]").forEach((button) => {
      button.addEventListener("click", () => {
        state.fontSize = button.dataset.fontSize;
        render();
      });
    });

    els.article.addEventListener("click", (event) => {
      const listButton = event.target.closest("[data-scroll-reading-list]");
      if (listButton) {
        scrollToElement(document.querySelector(".reading-workbench"));
        return;
      }

      const navButton = event.target.closest("[data-reading-nav]");
      if (navButton) {
        switchArticle(navButton.dataset.readingNav);
        return;
      }

      const speakButton = event.target.closest("[data-speak]");
      if (speakButton) {
        event.preventDefault();
        event.stopPropagation();
        speak(speakButton.dataset.speak, speakButton);
        return;
      }

      const keywordButton = event.target.closest("[data-keyword]");
      if (keywordButton) {
        event.preventDefault();
        const article = activeArticle();
        const keyword = keywordMap(article).get(keywordButton.dataset.keyword.toLowerCase());
        if (keyword) showKeywordInfo(keyword);
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

    document.addEventListener("click", (event) => {
      if (event.target.closest("[data-close-keyword]")) {
        closeKeywordInfo();
      }
    });
  }

  async function init() {
    els.search = $("readingArticleSearch");
    els.clearSearch = $("readingClearSearch");
    els.topicTabs = $("readingTopicTabs");
    els.levelTabs = $("readingLevelTabs");
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
