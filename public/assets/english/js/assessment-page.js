(function () {
  "use strict";

  const storageKey = "datakrs_ielts_assessment_v1";
  const labels = {
    listening: "听力",
    reading: "阅读",
    writing: "写作",
    speaking: "口语",
  };
  const plans = {
    listening: ["每天精听 15 分钟，先听主旨，再补数字、专名、转折信号。", "做题后复盘错因：没听到、听到了但没反应、同义替换没识别。"],
    reading: ["每天至少读 1 篇文章，先练定位和题干改写，再处理生词。", "把错题按判断题、匹配题、填空题分开记录。"],
    writing: ["先固定 Task 2 观点展开模板，再补连接、例证和反驳句型。", "每周至少完整写 2 篇，重点改逻辑和句子准确性。"],
    speaking: ["Part 2 每天录 1 题，先保证 90 秒不断，再补细节和例子。", "Part 3 用原因、对比、例子、让步四步扩展答案。"],
  };

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));

  function roundHalf(value) {
    return Math.round(value * 2) / 2;
  }

  function readState() {
    const writingText = document.querySelector("[data-text='writing']").value.trim();
    const speakingText = document.querySelector("[data-text='speaking']").value.trim();
    return {
      scores: {
        listening: Number($("[data-task='listening']").value) || 4.5,
        reading: Number($("[data-task='reading']").value) || 4.5,
        writing: textScore(writingText, "writing"),
        speaking: textScore(speakingText, "speaking"),
      },
      answers: {
        listening: $("[data-task='listening']").value,
        reading: $("[data-task='reading']").value,
        writing: writingText,
        speaking: speakingText,
      },
      target: Number($("#targetBand").value),
      minutes: Number($("#dailyMinutes").value),
      weeks: Number($("#weeks").value),
    };
  }

  function textScore(text, type) {
    const words = text.split(/\s+/).filter(Boolean);
    if (!words.length) return 4.5;
    const hasReason = /\b(because|since|as|therefore|so|due to)\b/i.test(text);
    const hasContrast = /\b(however|although|while|whereas|but|nevertheless)\b/i.test(text);
    const hasExample = /\b(for example|for instance|such as|in my experience)\b/i.test(text);
    const hasTopic = type === "writing" ? /\b(public transport|government|roads|congestion|investment|commuting)\b/i.test(text) : /\b(convenient|privacy|flexible|comfort|status|time)\b/i.test(text);
    let score = words.length >= 70 ? 5.5 : 5;
    if (words.length >= 90) score += 0.5;
    if (hasReason) score += 0.5;
    if (hasContrast) score += 0.5;
    if (hasExample) score += 0.5;
    if (hasTopic) score += 0.5;
    return Math.min(7.5, roundHalf(score));
  }

  function saveState() {
    const state = readState();
    localStorage.setItem(storageKey, JSON.stringify(state));
  }

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
      if (saved.answers) {
        if (saved.answers.listening) $("[data-task='listening']").value = saved.answers.listening;
        if (saved.answers.reading) $("[data-task='reading']").value = saved.answers.reading;
        if (saved.answers.writing) $("[data-text='writing']").value = saved.answers.writing;
        if (saved.answers.speaking) $("[data-text='speaking']").value = saved.answers.speaking;
      }
      if (saved.target) $("#targetBand").value = String(saved.target);
      if (saved.minutes) $("#dailyMinutes").value = String(saved.minutes);
      if (saved.weeks) $("#weeks").value = String(saved.weeks);
    } catch (error) {
      localStorage.removeItem(storageKey);
    }
  }

  function render() {
    const state = readState();
    const entries = Object.entries(state.scores).sort((a, b) => a[1] - b[1]);
    const average = roundHalf(entries.reduce((sum, item) => sum + item[1], 0) / entries.length);
    const gap = Math.max(0, roundHalf(state.target - average));
    const weak = entries.slice(0, 2);
    const totalHours = Math.round((state.minutes * 7 * state.weeks) / 60);
    const priority = weak.map(([key]) => labels[key]).join(" / ");
    const answerNotes = [
      state.scores.listening >= 7 ? "听力定位题正确，说明能抓住时间变更信息。" : "听力需要重点练日期、时间、地点变更以及否定转折。",
      state.scores.reading >= 7 ? "阅读主旨判断正确，能识别作者对“扩路”的真实态度。" : "阅读需要练段落主旨，不要只抓单个词判断答案。",
      state.scores.writing >= 6 ? "写作回答已有基本展开，可以继续提升论证层次和句子准确性。" : "写作目前需要先补观点句、原因句和例子句。",
      state.scores.speaking >= 6 ? "口语回答已有一定长度和原因，可以继续补细节与自然表达。" : "口语目前需要先做到不断句，再补原因、例子和对比。",
    ];

    $("#estimatedBand").textContent = average.toFixed(1);
    $("#bandGap").textContent = gap.toFixed(1);
    $("#prioritySkill").textContent = priority;

    const weeklyFocus = gap >= 1 ? "先补短板，再做整套模考。" : "保持四科稳定，增加限时训练。";
    $("#assessmentPlan").innerHTML = `
      <article>
        <h3>${priority}</h3>
        <p>未来 ${state.weeks} 周约 ${totalHours} 小时可用。${weeklyFocus}</p>
        <ul>
          ${answerNotes.map((item) => `<li>${item}</li>`).join("")}
          ${weak.flatMap(([key]) => plans[key]).map((item) => `<li>${item}</li>`).join("")}
        </ul>
      </article>
      <article>
        <h3>本周安排</h3>
        <p>每天先完成最弱科目，再做 100 句、核心词和阅读文章。每周末重新评测一次，观察分数是否稳定上移。</p>
      </article>
    `;
  }

  function bind() {
    $$("select, textarea").forEach((field) => {
      field.addEventListener(field.tagName === "TEXTAREA" ? "input" : "change", () => {
        saveState();
        render();
      });
    });
    $("#resetAssessment").addEventListener("click", () => {
      localStorage.removeItem(storageKey);
      $$("[data-task]").forEach((select) => { select.value = "0"; });
      $$("[data-text]").forEach((textarea) => { textarea.value = ""; });
      $("#targetBand").value = "6.5";
      $("#dailyMinutes").value = "60";
      $("#weeks").value = "8";
      render();
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    loadState();
    bind();
    render();
  });
})();
