"""
Configuration module for narrative transformation system.
Manages API credentials, model parameters, and genre templates.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for LLM API calls."""
    
    # API Keys (loaded from environment)
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    
    # Model selection - prioritize based on available keys
    default_model: str = field(default_factory=lambda: os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview"))
    fallback_model: str = "gpt-3.5-turbo"
    
    # Generation parameters
    temperature: float = field(default_factory=lambda: float(os.getenv("TEMPERATURE", "0.7")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("MAX_TOKENS", "2000")))
    top_p: float = field(default_factory=lambda: float(os.getenv("TOP_P", "0.9")))
    
    def validate(self) -> bool:
        """Check if at least one API key is configured."""
        return bool(self.openai_api_key or self.anthropic_api_key or self.gemini_api_key)
    
    def get_primary_api(self) -> str:
        """Return which API to use."""
        if self.gemini_api_key:
            return "gemini"
        elif self.openai_api_key:
            return "openai"
        elif self.anthropic_api_key:
            return "anthropic"
        return None


@dataclass
class GenreTemplate:
    """Template defining characteristics of a target genre."""
    
    name: str
    tone: str
    technology_level: str
    naming_conventions: List[str]
    key_aesthetics: List[str]
    world_rules: List[str]
    style_guidance: str


# Genre Templates Library
GENRE_TEMPLATES = {
    "cyberpunk": GenreTemplate(
        name="Cyberpunk",
        tone="Dark, gritty, tech-noir with neon aesthetics",
        technology_level="Near-future: AI, neural implants, megacorporations, virtual reality",
        naming_conventions=[
            "Tech-inspired: Neo-, Cyber-, -tron suffixes",
            "Corporate: Corp, Industries, Systems",
            "Shortened/alphanumeric: Rom-30, J-Unit, V-Corp"
        ],
        key_aesthetics=[
            "Neon-lit urban sprawl",
            "High tech, low life",
            "Corporate dystopia",
            "Augmented humans",
            "Virtual/physical reality blur"
        ],
        world_rules=[
            "Technology is ubiquitous but creates inequality",
            "Corporations have nation-state power",
            "Privacy is extinct",
            "Human augmentation is common",
            "The digital and physical worlds are intertwined"
        ],
        style_guidance="Use vivid sensory details emphasizing neon, chrome, rain-slicked streets. Include tech jargon naturally. Show class divide through technology access."
    ),
    
    "space_opera": GenreTemplate(
        name="Space Opera",
        tone="Epic, adventurous, galaxy-spanning drama",
        technology_level="Far-future: FTL travel, alien civilizations, energy weapons, terraforming",
        naming_conventions=[
            "Cosmic: Star-, Nova-, Nebula- prefixes",
            "Military ranks: Commander, Admiral, Captain",
            "Alien-sounding: apostrophes, unusual combinations"
        ],
        key_aesthetics=[
            "Vast starscapes and alien worlds",
            "Massive starships and space stations",
            "Diverse alien species",
            "Ancient alien artifacts",
            "Galactic empires and federations"
        ],
        world_rules=[
            "Multiple intelligent species coexist",
            "Travel between star systems is routine",
            "Galactic governments span thousands of worlds",
            "Ancient civilizations left powerful artifacts",
            "Technology appears as 'sufficiently advanced magic'"
        ],
        style_guidance="Emphasize scale and grandeur. Use formal, slightly archaic dialogue for gravitas. Describe alien environments with wonder."
    ),
    
    "victorian_gothic": GenreTemplate(
        name="Victorian Gothic",
        tone="Dark, atmospheric, morally complex, repressed",
        technology_level="Victorian era: Steam power, gas lamps, early photography, telegraphs",
        naming_conventions=[
            "Period-appropriate: Lord, Lady, Doctor, Professor",
            "British surnames: -shire, -ford, -worth",
            "Formal titles and honorifics"
        ],
        key_aesthetics=[
            "Fog-shrouded London streets",
            "Gothic architecture and manor houses",
            "Gas-lit interiors",
            "Strict social hierarchies",
            "Scientific rationalism vs supernatural horror"
        ],
        world_rules=[
            "Social class is rigid and defining",
            "Reputation is paramount",
            "Science is challenging old beliefs",
            "The supernatural lurks beneath respectability",
            "Gender roles are strictly enforced"
        ],
        style_guidance="Use formal, elaborate language. Emphasize atmosphere through weather and architecture. Explore themes of duality and hidden darkness."
    ),
    
    "post_apocalyptic": GenreTemplate(
        name="Post-Apocalyptic",
        tone="Grim, survivalist, desperate hope amid ruins",
        technology_level="Regressed: Scavenged tech, makeshift weapons, lost knowledge",
        naming_conventions=[
            "Descriptive: Rust, Ash, Dust, Steel",
            "Location-based: Vault-dweller, Wastelander",
            "Practical: roles and skills as names"
        ],
        key_aesthetics=[
            "Ruined cities and wastelands",
            "Makeshift settlements",
            "Scavenged technology",
            "Mutated flora/fauna",
            "Resource scarcity everywhere"
        ],
        world_rules=[
            "Survival is the primary concern",
            "Pre-apocalypse tech is valuable but rare",
            "Communities are small and isolated",
            "Trust is earned, not given",
            "The old world's mistakes echo in the new"
        ],
        style_guidance="Keep prose lean and immediate. Focus on sensory details of decay. Show resourcefulness and resilience."
    ),
    
    "mythic_fantasy": GenreTemplate(
        name="Mythic Fantasy",
        tone="Legendary, archetypal, timeless",
        technology_level="Pre-industrial: Magic, medieval weapons, ancient wisdom",
        naming_conventions=[
            "Archaic-sounding: -iel, -wyn, -or suffixes",
            "Titles: The Wise, The Brave, The Dark",
            "Elemental: Storm-, Fire-, Shadow-"
        ],
        key_aesthetics=[
            "Enchanted forests and ancient ruins",
            "Magical creatures and beings",
            "Legendary weapons and artifacts",
            "Mystical prophecies",
            "Clear good vs evil (or complex morality)"
        ],
        world_rules=[
            "Magic follows mysterious but consistent laws",
            "Prophecies and fate play a role",
            "Heroes face trials that test character",
            "Ancient powers can be awakened",
            "Balance must be maintained"
        ],
        style_guidance="Use elevated, poetic language. Emphasize symbolic and archetypal elements. Create sense of timelessness and wonder."
    )
}


# Save the Cat Beat Structure (15-beat version)
SAVE_THE_CAT_BEATS = [
    {
        "name": "Opening Image",
        "function": "Snapshot of protagonist's world before change",
        "target_emotion": "curiosity",
        "typical_length": 300
    },
    {
        "name": "Theme Stated",
        "function": "Hint at the story's central question or moral",
        "target_emotion": "intrigue",
        "typical_length": 250
    },
    {
        "name": "Setup",
        "function": "Establish normal world, characters, relationships, stakes",
        "target_emotion": "engagement",
        "typical_length": 400
    },
    {
        "name": "Catalyst",
        "function": "The event that launches the story",
        "target_emotion": "surprise",
        "typical_length": 350
    },
    {
        "name": "Debate",
        "function": "Protagonist hesitates, weighs options",
        "target_emotion": "tension",
        "typical_length": 300
    },
    {
        "name": "Break into Two",
        "function": "Protagonist commits to the journey",
        "target_emotion": "determination",
        "typical_length": 250
    },
    {
        "name": "B Story",
        "function": "Introduce subplot or relationship that will aid transformation",
        "target_emotion": "connection",
        "typical_length": 300
    },
    {
        "name": "Fun and Games",
        "function": "The premise delivers on its promise",
        "target_emotion": "excitement",
        "typical_length": 450
    },
    {
        "name": "Midpoint",
        "function": "False victory or false defeat; stakes raised",
        "target_emotion": "shock",
        "typical_length": 350
    },
    {
        "name": "Bad Guys Close In",
        "function": "External and internal pressures mount",
        "target_emotion": "anxiety",
        "typical_length": 400
    },
    {
        "name": "All Is Lost",
        "function": "Lowest point; protagonist seems defeated",
        "target_emotion": "despair",
        "typical_length": 300
    },
    {
        "name": "Dark Night of the Soul",
        "function": "Protagonist reflects on failure, faces internal demons",
        "target_emotion": "reflection",
        "typical_length": 250
    },
    {
        "name": "Break into Three",
        "function": "Protagonist finds solution, often by synthesizing A and B stories",
        "target_emotion": "hope",
        "typical_length": 200
    },
    {
        "name": "Finale",
        "function": "Protagonist proves transformation, defeats antagonist",
        "target_emotion": "triumph",
        "typical_length": 500
    },
    {
        "name": "Final Image",
        "function": "Mirror of opening image, showing change",
        "target_emotion": "satisfaction",
        "typical_length": 250
    }
]


# Default configuration instance
DEFAULT_CONFIG = ModelConfig()