# Daily AI Intelligence Dashboard

A stand-alone, daily-refreshed web dashboard summarizing artificial intelligence developments across 14 key sources in **Business & Enterprise**, **Higher Education**, and **Cross-Sector**.

---

## 🎨 Design & Palette
Built strictly adhering to the requested executive theme:
* **Primary Colors:** Crimson (`#990000`) and Cream (`#F8EFE2`)
* **Palette Accents:**
  * Light Crimson: `#F41C40`
  * Dark Crimson: `#6D0808`
  * Warm/Dark Cream: `#F5E3CC`
  * Light Grey: `#EEEEF0`
  * Dark Grey: `#B9C1C6`
  * IU Black: `#072332`

---

## 📚 14 Tracked Sources & Pipeline

### Business & Enterprise
1. **VentureBeat (AI)** — Web / RSS
2. **Fortune — Eye on AI** — Web & Newsletter
3. **Harvard Business Review — AI and Machine Learning** — Web / Journal
4. **MIT Sloan — AI at Work** — Web / Newsletter
5. **The Batch (DeepLearning.AI)** — Web / Newsletter
6. **The Neuron** — Direct Gmail Inbox Newsletter (`theneuron@newsletter.theneurondaily.com`)
7. **TLDR AI** — Direct Gmail Inbox Newsletter (`dan@tldrnewsletter.com`)
8. **AlphaSignal AI** — Direct Gmail Inbox Newsletter (`news@alphasignal.ai`)

### Higher Education
9. **The Chronicle of Higher Education — Jagged Intelligence** — Web / Newsletter
10. **EDUCAUSE Review** — Web / Journal
11. **Inside Higher Ed — Artificial Intelligence** — Web / Journal
12. **Campus Technology** — Web / RSS
13. **Jisc — Artificial Intelligence Community** — Web / Community

### Cross-Sector
14. **One Useful Thing (Ethan Mollick)** — Substack / Web

---

## 🚀 How to Open the Dashboard

The dashboard is completely self-contained in `index.html` with zero external dependencies and embedded data, meaning it can be opened immediately via file URL in any browser with no CORS restrictions or local server required:

### Option A: From Terminal
```bash
open /Users/lrego/.gemini/users/user1/ai_brief_dashboard/index.html
```

### Option B: From Finder
Navigate to `ai_brief_dashboard` in your home folder and double-click `index.html`.

---

## ⚙️ Key Features

1. **Card Grid & Structured Table Views:** Toggle between interactive executive cards and a high-density tabular view with one click.
2. **1–2 Sentence Bullet Takeaways:** Every story is distilled into concise, actionable takeaways with topic tags and read-time indicators.
3. **Multi-Facet Filtering & Search:**
   - Real-time keyword search across headlines, takeaways, tags, and source names.
   - One-click sector filter tabs (*All 14*, *Business & Enterprise 8*, *Higher Education 5*, *Cross-Sector 1*).
4. **Latest Pull + 5-Day Rolling Archive:**
   - Displays the latest morning briefing (today: `2026-10-09`).
   - Archive selector lets you instantly browse previous daily pulls (`2026-10-08`, `2026-10-07`, `2026-10-06`, `2026-10-05`, `2026-10-04`).
5. **Export & Sharing Capabilities:**
   - **📋 Copy Digest:** One-click copy of an email-ready Markdown executive brief directly to your clipboard.
   - **📥 Export Modal:** Export to Markdown (`.md`), Spreadsheet (`.csv`), or Raw Data (`.json`) with both copy and download file options.

---

## ⏰ Automated Daily 7:00 AM Refresh

An automated schedule has been configured:
* **Schedule Cadence:** Daily around 7:00 AM EDT.
* **Workflow:**
  1. Inspects Gmail inbox for new editions of *The Neuron*, *TLDR AI*, *AlphaSignal AI*, and any forwarded issues.
  2. Scans web feeds and RSS updates for the remaining 11 publications.
  3. Executes `scripts/refresh_dashboard.py` to synthesize 1–2 sentence bullet points per story, rotate the 5-day rolling archive, and rebuild `index.html`.
  4. Delivers the morning executive briefing directly to your chat.

### Manual Refresh
To manually run the ingestion and rebuild script at any time:
```bash
python3 /Users/lrego/.gemini/users/user1/ai_brief_dashboard/scripts/refresh_dashboard.py
python3 /Users/lrego/.gemini/users/user1/ai_brief_dashboard/scripts/build_html.py
```
