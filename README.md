# 🎭 Narrative Transformation System

> **An AI-powered system that transforms classic stories into new genres** — preserving narrative essence while reimagining setting, characters, and style using Large Language Models.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technical Innovation](#technical-innovation)
- [System Architecture](#system-architecture)
- [Test Results](#test-results)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Usage](#api-usage)
- [Design Decisions](#design-decisions)

---

## 🎯 Overview

This project demonstrates **advanced prompt engineering**, **system design**, and **creative AI application development**. It takes any source narrative and systematically transforms it into a completely different genre while preserving the core story elements.

### The Problem
Transforming stories across genres isn't just "rewriting" — it requires:
- Understanding narrative structure (characters, arcs, themes)
- Mapping elements to genre-appropriate equivalents
- Maintaining continuity and consistency
- Ensuring proper dramatic pacing

### The Solution
A **5-stage pipeline** that breaks down the complex transformation into manageable, testable steps with a novel **pacing control system** that ensures output quality.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Genre Support** | Cyberpunk, Space Opera, Victorian Gothic, Post-Apocalyptic, Mythic Fantasy |
| **Narrative Tension Index** | Quantitative pacing control using sentiment analysis |
| **Context-Aware Generation** | Full state tracking prevents character/plot inconsistencies |
| **Save the Cat Structure** | Industry-standard 15-beat story structure |
| **Retry Logic** | Exponential backoff for API reliability |
| **Centralized LLM Client** | Unified interface for OpenAI, Anthropic, Gemini |

---

## 💡 Technical Innovation

### Narrative Tension Index (NTI)

The standout innovation of this project: **a quantitative method to ensure proper dramatic pacing**.

```
NTI = (1 - certainty) × (1 - sentiment)

Where:
• Certainty: Predictability from modal verbs, questions, hedge words
• Sentiment: Emotional tone from VADER sentiment analysis (-1 to +1)
```

**How It Works:**
1. Each generated scene is analyzed for tension score
2. Score is compared against target (based on Save the Cat beat)
3. Deviation triggers pacing adjustments for next scene
4. Result: Natural dramatic arc without manual tuning

**Example Tension Curve:**
```
Opening Image:  ████░░░░░░ 0.40  (hook the reader)
Catalyst:       ███████░░░ 0.70  (inciting incident)
Midpoint:       █████████░ 1.50  (major revelation)
All Is Lost:    ████████░░ 1.30  (lowest point)
Finale:         ██████████ 1.80  (climax)
Resolution:     ██░░░░░░░░ 0.20  (denouement)
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INPUT LAYER                                  │
│   Source Text + Title + Target Genre + Beat Count                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: SOURCE ANALYZER                                             │
│  • Extract characters, themes, conflicts, plot beats                 │
│  • Identify Save the Cat structure                                   │
│  • Parse character arcs and relationships                            │
│  Output: SourceAnalysis (structured JSON)                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: WORLD MAPPER                                                │
│  • Map characters → genre equivalents (Romeo → Rom-30)               │
│  • Translate settings, objects, concepts                             │
│  • Apply genre-specific world rules                                  │
│  Output: WorldMapping (character/location/object mappings)           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: SCENE GENERATOR (Beat Loop)                                 │
│  FOR EACH BEAT:                                                      │
│    1. Calculate target NTI from Save the Cat structure               │
│    2. Generate scene with full context injection                     │
│    3. Calculate actual NTI via sentiment + uncertainty analysis      │
│    4. Provide pacing hints for next beat                             │
│    5. Update story state (deaths, locations, events)                 │
│  Output: List of scenes + tension metrics                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: STORY ASSEMBLER                                             │
│  • Combine scenes with formatting                                    │
│  • Add title, metadata, statistics                                   │
│  Output: Complete story (markdown) + quality metrics                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Test Results

**100% Success Rate** across all test transformations:

| Source Story | Target Genre | Words | Avg NTI | Status |
|--------------|--------------|-------|---------|--------|
| Cinderella | Space Opera | 932 | 0.60 | ✅ Pass |
| Tortoise & Hare | Cyberpunk | 874 | 0.63 | ✅ Pass |
| Icarus | Post-Apocalyptic | 940 | 1.33 | ✅ Pass |

**Consistency:** All outputs within 70 words of each other  
**Quality:** Professional-grade narrative with proper pacing  
**Speed:** ~30-60 seconds per 3-beat story

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenRouter or OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/HemantSudarshan/narrative-transformer.git
cd narrative-transformer

# Install dependencies
pip install -r requirements.txt

# Download NLTK data for sentiment analysis
python -c "import nltk; nltk.download('vader_lexicon')"

# Configure API key
cp .env.example .env
# Edit .env and add your API key
```

### Run Your First Transformation

```bash
python run.py \
  --source examples/tortoise_hare.txt \
  --title "The Tortoise and the Hare" \
  --genre cyberpunk \
  --beats 3 \
  --output output/story.txt
```

### Available Genres

| Genre | Aesthetic |
|-------|-----------|
| `cyberpunk` | Neon-lit tech dystopia, corporate intrigue |
| `space_opera` | Epic galaxy-spanning adventure |
| `victorian_gothic` | Fog-shrouded Victorian horror |
| `post_apocalyptic` | Survival in the ruins |
| `mythic_fantasy` | Timeless legendary tales |

---

## 📁 Project Structure

```
narrative-transformer/
├── llm_client.py      # Centralized LLM client with retry logic
├── analyzer.py        # Source narrative analysis (Phase 1)
├── mapper.py          # World element mapping (Phase 2)
├── generator.py       # Scene generation engine (Phase 3)
├── tension.py         # NTI calculator & pacing controller
├── transformer.py     # Main orchestrator
├── config.py          # Genre templates & model settings
├── models.py          # Pydantic-style data structures
├── run.py             # CLI interface
├── run_tests.py       # Automated test suite
│
├── examples/          # Sample input stories
│   ├── cinderella.txt
│   ├── tortoise_hare.txt
│   └── icarus.txt
│
├── output/            # Generated story outputs
│   ├── test1_cinderella_space.txt
│   ├── test2_tortoise_cyber.txt
│   └── test3_icarus_postapoc.txt
│
├── SOLUTION.md        # Detailed technical documentation
├── APPROACH.md        # Design rationale & alternatives
└── requirements.txt   # Python dependencies
```

---

## � API Usage

### Python Interface

```python
from transformer import NarrativeTransformer

# Initialize transformer
transformer = NarrativeTransformer()

# Transform a story
story, metadata = transformer.transform(
    source_text="Your story text here...",
    source_title="My Story",
    target_genre="cyberpunk",
    num_beats=5
)

# Access results
print(story)
print(f"Word Count: {metadata['word_count']}")
print(f"Average Tension: {metadata['avg_tension']:.2f}")
print(f"Character States: {metadata['character_states']}")
```

### Metadata Output

```python
{
    "word_count": 932,
    "avg_tension": 0.63,
    "character_states": {
        "Neo-Cinder": {"status": "alive", "location": "Starbase Omega"},
        "Prince Orion": {"status": "alive", "location": "Royal Cruiser"}
    },
    "tension_scores": [0.03, 1.74, 0.04]
}
```

---

## 🎯 Design Decisions

### Why This Architecture?

| Decision | Alternative | Why Chosen |
|----------|-------------|------------|
| **Context-based approach** | Vector database RAG | Simpler, faster for short stories, fully transparent |
| **Structured JSON prompts** | Free-form generation | Consistent outputs, reliable parsing |
| **Beat-by-beat generation** | Full story at once | Better control, state tracking, pacing adjustment |
| **Quantitative NTI** | Subjective quality | Measurable, reproducible, automated |

### Trade-offs Considered

| Feature | Benefit | Trade-off |
|---------|---------|-----------|
| Full context in prompts | Consistency | Higher token usage |
| Scene-by-scene generation | Modularity | More API calls |
| NTI calculation | Measurable pacing | Additional computation |
| Centralized LLM client | Maintainability | Extra abstraction layer |

---

## 🔧 Technical Stack

- **Language:** Python 3.8+
- **LLM APIs:** OpenAI, Anthropic, Google Gemini (via OpenRouter)
- **NLP:** NLTK, VADER Sentiment Analysis
- **Data Validation:** Dataclasses with type hints
- **Configuration:** python-dotenv

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| API calls per transformation | 10-15 |
| Generation time (3 beats) | 30-60 seconds |
| Average output length | 800-1000 words |
| Retry resilience | 3 attempts with exponential backoff |
| Success rate | 100% (in testing) |

---

## 🔮 Future Enhancements

- [ ] **Multi-POV Support:** Generate scenes from multiple character perspectives
- [ ] **Interactive Mode:** Allow users to approve/edit at each stage
- [ ] **Style Transfer:** Learn writing style from example texts
- [ ] **Web Interface:** REST API with streaming output
- [ ] **Novel-length:** Optimize for longer transformations

---

## 📚 Documentation

- **[SOLUTION.md](SOLUTION.md)** — Full technical documentation with code examples
- **[APPROACH.md](APPROACH.md)** — Design rationale and alternatives considered

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Hemant Sudarshan**

Built as a demonstration of:
- 🧠 System design and architecture
- ✍️ Advanced prompt engineering
- 🎨 Creative AI applications
- 📊 Quantitative quality control
- 🔧 Clean, modular Python code

---

<p align="center">
  <i>The <b>Narrative Tension Index</b> is the innovative solution — a quantitative method to ensure proper dramatic pacing in AI-generated stories.</i>
</p>