---
description: How to run narrative transformations
---

# Narrative Transformer Workflow

## Quick Start

// turbo-all

1. **Install dependencies** (first time only):
   ```bash
   pip install -r requirements.txt
   python -c "import nltk; nltk.download('vader_lexicon')"
   ```

2. **Configure API key**:
   - Copy `.env.example` to `.env`
   - Add your OpenRouter API key: `OPENAI_API_KEY=sk-or-v1-your-key`

3. **Run a transformation**:
   ```bash
   python run.py --source examples/tortoise_hare.txt --title "The Tortoise and the Hare" --genre cyberpunk --beats 3 --output output/story.txt
   ```

## Available Genres
- `cyberpunk` - Neon-lit tech dystopia
- `space_opera` - Epic galactic adventure
- `victorian_gothic` - Fog-shrouded horror
- `post_apocalyptic` - Survival in ruins
- `mythic_fantasy` - Legendary tales

## Run All Tests
```bash
python run_tests.py
```

This runs 3 transformations:
- Cinderella → Space Opera
- Tortoise & Hare → Cyberpunk  
- Icarus → Post-Apocalyptic

## Python API Usage
```python
from transformer import NarrativeTransformer

transformer = NarrativeTransformer()
story, metadata = transformer.transform(
    source_text="Your story text here...",
    source_title="My Story",
    target_genre="cyberpunk",
    num_beats=5
)

print(story)
print(f"Words: {metadata['word_count']}")
print(f"Tension: {metadata['avg_tension']}")
```
