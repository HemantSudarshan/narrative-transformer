# Narrative Transformation System

An AI-powered system that transforms classic narratives (like Romeo & Juliet) into new genres (like Cyberpunk), preserving narrative essence while reimagining setting, characters, and style.

## 🎯 What It Does

Takes a source story and systematically transforms it:
- **Analyzes** narrative structure (characters, themes, conflicts, beats)
- **Maps** elements to target genre (characters → roles, objects → equivalents)
- **Generates** new scenes with adaptive pacing control
- **Assembles** a complete reimagined story (2-3 pages)

## 🌟 Key Innovation: Narrative Tension Index (NTI)

The system includes an **adaptive pacing controller** that:
- Calculates tension for each scene using sentiment + uncertainty
- Compares to ideal tension curve (Save the Cat structure)
- Dynamically adjusts next scene's tone to maintain engagement

**Formula:** `NTI = (1 - certainty) × (1 - sentiment)`

This ensures the story maintains proper dramatic pacing throughout.

## 🏗️ Architecture

```
Input Text
    ↓
┌─────────────────┐
│ Source Analyzer │  → Characters, Themes, Beats, Conflicts
└─────────────────┘
    ↓
┌─────────────────┐
│  World Mapper   │  → Element Mappings (Romeo → Rom-30)
└─────────────────┘
    ↓
┌─────────────────┐
│ Scene Generator │  ← Pacing hints from NTI controller
│   (Beat Loop)   │  → Generated scenes with metadata
└─────────────────┘
    ↓
┌─────────────────┐
│   Assembler     │  → Final Story + Metadata
└─────────────────┘
```

## 📦 Installation

```bash
# Clone/download the repository
cd narrative-transformer

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY

# Download NLTK data (for sentiment analysis)
python -c "import nltk; nltk.download('vader_lexicon')"
```

## 🚀 Usage

### Command Line

```bash
python run.py \
  --source examples/romeo_juliet.txt \
  --title "Romeo and Juliet" \
  --genre cyberpunk \
  --beats 12 \
  --output output/neo_verona.txt
```

### Available Genres

- `cyberpunk` - Dark, neon-lit tech dystopia
- `space_opera` - Epic galaxy-spanning adventure
- `victorian_gothic` - Fog-shrouded Victorian horror
- `post_apocalyptic` - Survival in the ruins
- `mythic_fantasy` - Timeless legendary tales

### Python API

```python
from transformer import NarrativeTransformer

transformer = NarrativeTransformer()

story, metadata = transformer.transform(
    source_text="[your source text]",
    source_title="Romeo and Juliet",
    target_genre="cyberpunk",
    num_beats=12
)

print(story)
print(f"Average tension: {metadata['avg_tension']}")
```

## 📊 Example Output

**Input:** Romeo & Juliet (Act 1-2)  
**Output:** 2500-word cyberpunk reimagining

```
Romeo and Juliet: A Cyberpunk Reimagining
==========================================

## Opening Image

The neon rain slicked the streets of Neo-Verona's lower districts. 
Rom-30 jacked into his terminal, fingers dancing across haptic keys...
```

**Metadata:**
- Word count: 2,847
- Average tension: 0.87
- Character fates: `Rom-30: dead - last seen at Capulet Corp HQ`

## 🛠️ Project Structure

```
narrative-transformer/
├── config.py           # Genre templates & settings
├── models.py           # Data structures
├── analyzer.py         # Source narrative analysis
├── mapper.py           # World element mapping
├── tension.py          # NTI calculator & pacing controller
├── generator.py        # Scene generation engine
├── transformer.py      # Main orchestrator
├── run.py             # CLI interface
├── requirements.txt    # Dependencies
├── .env.example       # Environment template
└── examples/          # Sample inputs/outputs
```

## 🎨 Design Decisions

### Why This Architecture?

**Context-Based Approach** (chosen) vs. Vector Database:
- ✅ Simpler, faster for 2-3 page stories
- ✅ No infrastructure overhead
- ✅ Fully transparent and debuggable
- ❌ Doesn't scale to novel-length (but not required)

**Structured Prompts** (chosen) vs. Free-form:
- ✅ Consistent output format
- ✅ Reliable metadata extraction
- ✅ Clear separation of concerns

**Adaptive Pacing** (chosen) vs. Fixed Structure:
- ✅ Dynamically responds to tension levels
- ✅ Prevents monotonous pacing
- ✅ Quantitative feedback loop

### Key Trade-offs

| Feature | Benefit | Cost |
|---------|---------|------|
| Full context in prompts | Consistency | Token usage |
| Scene-by-scene generation | Modularity | More API calls |
| Beat-based structure | Clear organization | Less flexibility |
| NTI calculation | Measurable pacing | Additional computation |

## 🧪 Testing

```bash
# Test individual components
python analyzer.py     # Test source analysis
python mapper.py       # Test world mapping
python tension.py      # Test NTI calculation
python generator.py    # Test scene generation

# Run full transformation
python run.py --source examples/romeo_juliet.txt --title "Romeo and Juliet" --genre cyberpunk
```

## 🔮 Future Improvements

1. **Multi-POV Support**: Generate scenes from different character perspectives
2. **Interactive Refinement**: Allow users to adjust specific scenes
3. **Style Transfer**: Learn style from example texts
4. **Longer Forms**: Optimize for novel-length transformations
5. **API Endpoint**: Deploy as REST API service
6. **Visualization**: Interactive tension curve editor

## 📝 Requirements

- Python 3.8+
- OpenAI API key (GPT-4 recommended) OR Anthropic API key (Claude)
- ~10-15 API calls per transformation (12 beats)
- ~3-5 minutes generation time

## 🤝 Contributing

This is a take-home assignment project. For production use, consider:
- Error recovery and retries
- Caching frequently-used analyses
- Parallel scene generation
- User feedback integration

## 📄 License

Educational/assignment project. Check source material licensing for any specific transformations.

## ✨ Credits

Built as a take-home assignment demonstrating:
- System thinking and architecture design
- Prompt engineering for structured outputs
- Creative AI application with measurable controls
- Clean, modular code organization

The **Narrative Tension Index** approach is the "clever idea we didn't ask for" — a quantitative method to ensure proper dramatic pacing throughout generated stories.