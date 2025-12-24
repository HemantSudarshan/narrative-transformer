# 🎭 Narrative Transformation System

> **Transform classic stories into new genres using AI** — preserving narrative essence while reimagining setting, characters, and style.

**Built by [Hemant Sudarshan](https://github.com/HemantSudarshan)** 

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🎯 What This Does

Takes any classic story and systematically transforms it into a completely different genre:

```
Cinderella → Space Opera        (fairy godmother → AI hologram mentor)
Tortoise & Hare → Cyberpunk     (race → data heist competition)
Icarus → Post-Apocalyptic       (wax wings → makeshift glider)
```

> 💡 **The system is demonstrated on Cinderella, Icarus, and Tortoise & Hare as examples, but is designed to generalize to any public-domain work** — Shakespeare, Greek myths, folk tales, or classic literature.

**Not just "rewriting"** — the system analyzes narrative structure, maps elements systematically, and generates with adaptive pacing control.

---

## ⚡ Quick Demo

```bash
# Install
pip install -r requirements.txt
python -c "import nltk; nltk.download('vader_lexicon')"

# Configure (add your OpenRouter API key)
cp .env.example .env

# Transform!
python run.py \
  --source examples/tortoise_hare.txt \
  --title "The Tortoise and the Hare" \
  --genre cyberpunk \
  --beats 3 \
  --output output/story.txt
```

**Output:** 800-1000 word story in ~60 seconds

---

## 🏗️ How It Works

### 5-Phase Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   ANALYZE    │ →  │     MAP      │ →  │   GENERATE   │ →  │   ASSEMBLE   │ →  │    OUTPUT    │
│              │    │              │    │   (loop)     │    │              │    │              │
│ Extract:     │    │ Translate:   │    │ Per beat:    │    │ Combine:     │    │ Final:       │
│ • Characters │    │ • Names      │    │ • Context    │    │ • Scenes     │    │ • Story      │
│ • Themes     │    │ • Locations  │    │ • NTI check  │    │ • Formatting │    │ • Metrics    │
│ • Conflicts  │    │ • Objects    │    │ • Pacing     │    │ • Metadata   │    │              │
│ • Beats      │    │ • Concepts   │    │ • State      │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### Example Character Mapping

| Source | Cyberpunk Equivalent | Preserved Function |
|--------|---------------------|-------------------|
| Hare | **Blitz** — elite speed-hacker with neural overclocking | Overconfident protagonist |
| Tortoise | **Shell** — methodical old-school coder | Underestimated underdog |
| Race | Data heist competition on the Grid | Central conflict/challenge |
| Nap | Neural cooldown (overclocked brain forces shutdown) | Hubris leading to downfall |

---

## 💡 Key Innovation: Narrative Tension Index (NTI)

**The Problem:** LLMs generate creative text but struggle with consistent pacing — stories often feel flat or peak too early.

**The Solution:** Quantitative tension measurement with adaptive feedback:

```
NTI = (1 - certainty) × (1 - sentiment)

High NTI = uncertain outcome + negative emotion → TENSION
Low NTI  = clear outcome + positive emotion → RESOLUTION
```

**How it works:**
1. Generate scene
2. Calculate actual NTI using sentiment analysis
3. Compare to target (based on Save the Cat beat structure)
4. Adjust next scene's pacing hints

```
Target Tension Curve (Save the Cat):

2.0 |                               ★ ← Climax
    |                          ★
1.5 |            ★        ★            ← Midpoint
    |        ★       ★
1.0 |    ★                    ★
    |★                            ★
0.5 |                                 ★ ← Resolution
    +----------------------------------------
     1  2  3  4  5  6  7  8  9  10 11 12
                     BEATS
```

---

## 📊 Test Results

| Story | Target Genre | Words | Avg NTI | Status |
|-------|--------------|-------|---------|--------|
| Cinderella | Space Opera | 932 | 0.60 | ✅ |
| Tortoise & Hare | Cyberpunk | 874 | 0.63 | ✅ |
| Icarus | Post-Apocalyptic | 940 | 1.33 | ✅ |

**100% success rate** across all test transformations

---

## 🎨 Available Genres

| Genre | Aesthetic | Example Elements |
|-------|-----------|------------------|
| `cyberpunk` | Neon-lit tech dystopia | Neural jacks, megacorps, data heists |
| `space_opera` | Epic galactic adventure | Starships, alien councils, hyperspace |
| `victorian_gothic` | Fog-shrouded horror | Gas lamps, séances, dark secrets |
| `post_apocalyptic` | Survival in ruins | Scavengers, wasteland, lost tech |
| `mythic_fantasy` | Legendary tales | Ancient magic, prophecies, quests |

---

## 📁 Project Structure

```
narrative-transformer/
├── llm_client.py          # Centralized LLM client (retry logic, JSON mode)
├── analyzer.py            # Phase 1: Source analysis
├── mapper.py              # Phase 2: World mapping
├── generator.py           # Phase 3: Scene generation
├── tension.py             # NTI calculator & pacing controller
├── transformer.py         # Main orchestrator
├── config.py              # Genre templates & settings
├── models.py              # Data structures
├── run.py                 # CLI interface
├── run_tests.py           # Test suite (3 stories)
│
├── examples/              # Sample inputs
│   ├── cinderella.txt
│   ├── tortoise_hare.txt
│   ├── icarus.txt
│   └── SAMPLE_TRANSFORMATION.md   # Intermediate data example
│
├── output/                # Generated stories
│
├── SOLUTION.md            # Technical documentation
└── APPROACH.md            # Design decisions & alternatives
```

---

## 💻 Python API

```python
from transformer import NarrativeTransformer

transformer = NarrativeTransformer()

story, metadata = transformer.transform(
    source_text="Your story here...",
    source_title="My Story",
    target_genre="cyberpunk",
    num_beats=5
)

print(story)
print(f"Words: {metadata['word_count']}")
print(f"Tension: {metadata['avg_tension']:.2f}")
```

---

## 🔧 Configuration

Create `.env` file:

```env
# OpenRouter (recommended)
OPENAI_API_KEY=sk-or-v1-your-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=openai/gpt-3.5-turbo

# Settings
TEMPERATURE=0.7
MAX_TOKENS=2000
```

---

## 🎯 Design Decisions

| Decision | Why |
|----------|-----|
| **Context-based (not RAG)** | 2-3 pages fit in context; simpler, faster, debuggable |
| **Beat-by-beat generation** | Enables state tracking + pacing control |
| **Save the Cat structure** | Industry-standard framework with clear targets |
| **Quantitative NTI** | Measurable quality → feedback loop |
| **Centralized LLM client** | Retry logic, JSON mode, consistent interface |

See [APPROACH.md](APPROACH.md) for full analysis of alternatives considered.

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Generation time (3 beats) | ~30-60 seconds |
| API calls per transformation | 10-15 |
| Output length | 800-1000 words |
| Retry resilience | 3 attempts + exponential backoff |

---

## 📚 Documentation

- **[SOLUTION.md](SOLUTION.md)** — Full technical walkthrough with architecture diagrams
- **[APPROACH.md](APPROACH.md)** — Design rationale, alternatives, challenges
- **[examples/SAMPLE_TRANSFORMATION.md](examples/SAMPLE_TRANSFORMATION.md)** — Intermediate transformation data

---

## 🔮 Future Improvements

**Core Features:**
- [ ] Multi-POV support (scenes from different character perspectives)
- [ ] Interactive mode (approve/edit at each stage)
- [ ] Novel-length optimization
- [ ] Style transfer from example texts

**Optional Extensions (for contributors):**
- [ ] **Streamlit UI** — Web interface with live progress and tension visualization
- [ ] **MLOps Integration** — Experiment tracking (MLflow/W&B), cost monitoring, A/B testing
- [ ] **GitHub Actions CI** — Automated testing on every push
- [ ] **REST API** — FastAPI endpoint for programmatic access
- [ ] **Docker** — Containerized deployment

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>🧠 The Narrative Tension Index</b> — quantitative pacing control for AI-generated stories
  <br><br>
  <i>Built as a demonstration of system design, prompt engineering, and creative AI applications.</i>
</p>