# ⚔️ AI Debate Arena

> *Two AI models walk into a room. Only one walks out with the trophy.*

A multi-agent debate engine built with **LangGraph** where GPT and Gemini go head-to-head on any topic you throw at them — while a third AI referee keeps things honest.

---

## 🧠 The Contenders

| Role | Model | Personality |
|------|-------|-------------|
| 🟢 **PRO** | GPT-5 | Argues *for* the motion. Crisp. Technical. Relentless. |
| 🔴 **CON** | Gemini-3.5-flash | Argues *against* the motion. Highlights risks. Finds the holes. |
| ⚖️ **JUDGE** | GPT-5.4 | Scores each round on logic, rebuttals, and clarity. No mercy. |

---

## 🔁 How It Works

```
Round 1 ──► PRO argues ──► CON rebuts ──► JUDGE scores
Round 2 ──► PRO argues ──► CON rebuts ──► JUDGE scores
Round 3 ──► PRO argues ──► CON rebuts ──► JUDGE scores
                                               │
                                        FINAL VERDICT
                                     (winner + conclusion)
```

Each agent sees the **previous round's arguments and judge feedback**, so the debate actually evolves. No repeat talking points. No hollow monologues.

---

## 🚀 Quickstart

**1. Clone & install**
```bash
git clone https://github.com/yourname/ai-debate-arena
cd ai-debate-arena
pip install -r requirements.txt
```

**2. Set up your API keys**
```bash
# .env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

**3. Start the debate**
```bash
python debate.py
```

```
Enter a debate topic: Remote work is better than office work
```

**4. Watch the chaos unfold**
```
════════════════════════════════════════════════════════════════════════
ROUND 1 - PRO
════════════════════════════════════════════════════════════════════════
Remote work eliminates commute overhead, returning 1-2 productive hours
to employees daily...

════════════════════════════════════════════════════════════════════════
ROUND 1 - CON
════════════════════════════════════════════════════════════════════════
PRO ignores the collaboration tax. Serendipitous hallway conversations
drive 30% of innovation in knowledge work...
```

---

## 🏗️ Architecture

Built on **LangGraph** with a stateful graph that loops until the debate is done:

```
[pro_node] → [con_node] → [judge_node]
                               │
               ┌───────────────┴──────────────┐
          more rounds?                    last round?
               │                               │
         [next_round_node]             [final_round_node]
               │                               │
             [pro]                           [END]
```

The `DebateState` TypedDict carries the full debate history, round counter, and running scores across every node — no external memory needed.

---

## 📦 Project Structure

```
ai-debate-arena/
├── debate.py          # Everything. One file. No fluff.
├── .env               # Your API keys (never commit this)
├── requirements.txt
└── README.md
```

---

## 🔧 Configuration

Tweak these in `debate.py` to adjust the experience:

| Setting | Default | What it does |
|---------|---------|-------------|
| `max_rounds` | `3` | Number of debate rounds |
| `temperature` | `0.7` | Higher = spicier arguments |
| `5 lines` (in prompt) | — | Per-argument length cap |

---

## 💡 Good Topics to Try

- *"AI will replace software engineers within 10 years"*
- *"Microservices are always better than monoliths"*
- *"Social media does more harm than good"*
- *"Pineapple belongs on pizza"* *(classic)*

---

## 🛠️ Requirements

- Python 3.10+
- `langgraph`
- `langchain-openai`
- `langchain-google-genai`
- `python-dotenv`

---

## ⚠️ Known Quirks

- The judge has opinions. Strong ones. Don't take it personally.
- Gemini's response format differs slightly from OpenAI — the `con_node` extracts `.content[0]["text"]` accordingly.
- This is a single-file project by design. Keeping it lean.

---

## 📜 License

MIT. Fork it. Extend it. Make the models argue about whether they should have been forked.

---

*Built with LangGraph, caffeine, and a genuine curiosity about which AI argues better.*
