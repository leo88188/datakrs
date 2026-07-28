# Datakrs English Module Ops

Last updated: 2026-07-28

## Scope

The IELTS H5 module is a static frontend under `public/` and is deployed to:

- `https://www.datakrs.com/english.html`
- `https://www.datakrs.com/english-vocab.html`
- `https://www.datakrs.com/english-roots.html`
- `https://www.datakrs.com/english-reading.html`
- `https://www.datakrs.com/english-skills.html`
- `https://www.datakrs.com/english-sentences.html`

The main goal is mobile-first personal IELTS practice. Keep implementation lightweight. Prioritise content, clear interaction, local progress, and avoiding unnecessary OSS traffic.

## Important Files

- `public/english.html`: IELTS 100 sentences entry.
- `public/english-vocab.html`: vocabulary module.
- `public/english-roots.html`: roots/prefixes/suffixes module.
- `public/english-reading.html`: reading article module.
- `public/english-skills.html`: Listening/Speaking/Reading/Writing practice hub.
- `public/english-sentences.html`: classic sentence card module.
- `public/assets/english/css/english.css`: shared styles.
- `public/assets/english/js/english.js`: main page logic.
- `public/assets/english/js/vocab-page.js`: vocabulary page logic.
- `public/assets/english/js/roots-page.js`: roots page logic.
- `public/assets/english/js/reading-page.js`: reading page logic.
- `public/assets/english/js/skills-page.js`: four-skill hub logic.
- `public/assets/english/js/sentences-page.js`: classic sentence page logic and local sentence data generator.
- `public/assets/english/data/reading-articles.json`: 230 original IELTS-style reading articles. Not real exam text.
- `public/assets/english/data/skills-practice.json`: four-skill practice prompts and routines.

## Deployment

Deployment script lives outside this repo:

```bash
cd /Users/luocheng/aliyun
python3 deploy_english_module.py --commit <git-commit-sha>
```

It deploys via Alibaba Cloud RunCommand to ECS:

- Instance: `i-uf61vjwybcnxs9o3wrx8`
- Region: `华东2（上海）`
- Public IP: `139.196.7.238`
- Site: `https://www.datakrs.com/`

The deploy script pulls from GitHub archive:

- GitHub repo: `https://github.com/leo88188/datakrs`

Do not store plaintext server passwords, GitHub tokens, or cloud secrets in this repo.

## OSS Media Rule

Opening pages must not download OSS audio/video.

Current rule:

- `<audio>` and `<video>` use `preload="none"`.
- JS stores media URLs in `data-src`.
- Real `src` is assigned only after the user interacts with the media control.

Relevant resources are on OSS Guangzhou bucket/path:

- `https://engilish.oss-cn-guangzhou.aliyuncs.com/assets/audio/`
- `https://engilish.oss-cn-guangzhou.aliyuncs.com/assets/videos/`
- `https://engilish.oss-cn-guangzhou.aliyuncs.com/assets/vocab-audio/`

## Validation

Static checks:

```bash
cd /Users/luocheng/aliyun/datakrs_repo
node --check public/assets/english/js/english.js
node --check public/assets/english/js/vocab-page.js
node --check public/assets/english/js/roots-page.js
node --check public/assets/english/js/reading-page.js
node --check public/assets/english/js/skills-page.js
node --check public/assets/english/js/sentences-page.js
python3 -c 'import json; d=json.load(open("public/assets/english/data/reading-articles.json", encoding="utf-8")); assert len(d["articles"]) >= 200; assert all(len(a["keywords"]) >= 16 for a in d["articles"])'
```

Local browser smoke test:

```bash
cd /Users/luocheng/aliyun/datakrs_repo
python3 -m http.server 8794 -d public
```

Then test:

- `/english.html` opens without OSS media requests.
- `/english-skills.html` switches tabs and writing word count updates.
- `/english-reading.html` shows 200+ articles and keyword popovers work.

Production smoke test:

- `https://www.datakrs.com/english.html`
- `https://www.datakrs.com/english-reading.html`
- `https://www.datakrs.com/english-skills.html`

## Current Product State

- Latest deployed commit: `f99b91c` Add sentence grammar combination notes.
- Reading module: 230 original IELTS-style articles, 16 keywords per article, Chinese paragraph translations, Band 5/6/7/8-9 filters, topic filters, answer explanations.
- Skills hub: lightweight four-skill practice workflow.
  - Listening links to 100 sentences and vocabulary audio practice.
  - Speaking has prompt cards, timer, and local browser recording.
  - Reading links to the reading article library.
  - Writing has timed prompts, local draft autosave, word count, and checklist.
- Classic sentences module: defaults to IELTS complex-sentence training, with 2,006 sentence cards total, 1,008 IELTS complex-sentence cards across 84 topics and 998 quote/golden-expression cards, clear learning labels, grammar-pattern filters, topic filters, simple grammar-combination notes, search, random card, browser speech synthesis, clickable IELTS/professional vocabulary IPA phonetics, Chinese meanings and Chinese usage notes, local favorites and read progress.

## Next Improvements

Keep changes content-first:

- Add more speaking cue cards and Part 3 question sets.
- Add more writing prompts by IELTS topic and task type.
- Add simple daily plan generator using local data only.
- Add review queue for wrong reading questions and saved words.
