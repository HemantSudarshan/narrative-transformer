"""
Data models for narrative transformation system.
Uses dataclasses for simple, type-safe data structures.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Character:
    """Represents a character in the narrative."""
    name: str
    role: str  # hero, mentor, villain, ally, etc.
    traits: List[str]
    desires: List[str]
    fears: List[str]
    arc: str  # character's transformation journey
    
    # For target world
    target_name: Optional[str] = None
    target_role: Optional[str] = None
    target_description: Optional[str] = None
    
    # Runtime state
    status: str = "alive"  # alive, dead, absent
    location: Optional[str] = None
    inventory: List[str] = field(default_factory=list)


@dataclass
class PlotBeat:
    """Represents a single plot beat from Save the Cat structure."""
    index: int
    name: str
    function: str
    source_events: List[str]
    target_emotion: str
    typical_length: int


@dataclass
class Conflict:
    """Represents a narrative conflict."""
    type: str  # internal, external, interpersonal
    description: str
    parties_involved: List[str]
    resolution: Optional[str] = None


@dataclass
class SourceAnalysis:
    """Complete analysis of source narrative."""
    title: str
    characters: List[Character]
    themes: List[str]
    beats: List[PlotBeat]
    conflicts: List[Conflict]
    symbols: Dict[str, str]  # symbol -> meaning
    setting: str
    tone: str
    central_question: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "title": self.title,
            "characters": [
                {
                    "name": c.name,
                    "role": c.role,
                    "traits": c.traits,
                    "desires": c.desires,
                    "fears": c.fears,
                    "arc": c.arc
                }
                for c in self.characters
            ],
            "themes": self.themes,
            "beats": [
                {
                    "name": b.name,
                    "function": b.function,
                    "source_events": b.source_events
                }
                for b in self.beats
            ],
            "conflicts": [
                {
                    "type": c.type,
                    "description": c.description,
                    "parties": c.parties_involved
                }
                for c in self.conflicts
            ],
            "symbols": self.symbols,
            "setting": self.setting,
            "tone": self.tone,
            "central_question": self.central_question
        }


@dataclass
class ElementMapping:
    """Maps a single element from source to target."""
    source: str
    target: str
    category: str  # character, location, object, concept
    narrative_function: str
    symbolic_meaning: Optional[str] = None


@dataclass
class WorldMapping:
    """Complete mapping from source world to target world."""
    genre: str
    character_mappings: List[ElementMapping]
    location_mappings: List[ElementMapping]
    object_mappings: List[ElementMapping]
    concept_mappings: List[ElementMapping]
    world_rules: List[str]
    
    def get_target_name(self, source_name: str, category: str = None) -> Optional[str]:
        """Get target name for a source element."""
        all_mappings = (
            self.character_mappings +
            self.location_mappings +
            self.object_mappings +
            self.concept_mappings
        )
        
        for mapping in all_mappings:
            if mapping.source.lower() == source_name.lower():
                if category is None or mapping.category == category:
                    return mapping.target
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "genre": self.genre,
            "character_mappings": [
                {
                    "source": m.source,
                    "target": m.target,
                    "function": m.narrative_function
                }
                for m in self.character_mappings
            ],
            "location_mappings": [
                {
                    "source": m.source,
                    "target": m.target
                }
                for m in self.location_mappings
            ],
            "object_mappings": [
                {
                    "source": m.source,
                    "target": m.target
                }
                for m in self.object_mappings
            ],
            "concept_mappings": [
                {
                    "source": m.source,
                    "target": m.target
                }
                for m in self.concept_mappings
            ],
            "world_rules": self.world_rules
        }


@dataclass
class SceneOutput:
    """Output from scene generation."""
    beat_index: int
    beat_name: str
    text: str
    characters_involved: List[str]
    location: str
    emotional_valence: float  # -1 (negative) to +1 (positive)
    tension_score: float  # NTI value
    state_updates: Dict[str, any]  # changes to apply to story state
    unresolved_hooks: List[str]  # questions/tensions left open
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "beat_index": self.beat_index,
            "beat_name": self.beat_name,
            "text": self.text,
            "characters": self.characters_involved,
            "location": self.location,
            "emotional_valence": self.emotional_valence,
            "tension_score": self.tension_score,
            "state_updates": self.state_updates,
            "hooks": self.unresolved_hooks
        }


@dataclass
class StoryState:
    """Tracks the current state of the story during generation."""
    characters: Dict[str, Character]  # name -> Character
    active_conflicts: List[Conflict]
    timeline: List[str]  # major events in order
    current_beat: int
    
    @classmethod
    def from_analysis(cls, analysis: SourceAnalysis, mapping: WorldMapping):
        """Initialize state from source analysis and world mapping."""
        characters = {}
        
        for char in analysis.characters:
            # Find mapped name
            target_name = mapping.get_target_name(char.name, "character")
            if target_name:
                char.target_name = target_name
                char.status = "alive"
                char.location = "unknown"
                characters[target_name] = char
        
        return cls(
            characters=characters,
            active_conflicts=analysis.conflicts.copy(),
            timeline=[],
            current_beat=0
        )
    
    def update_character_status(self, name: str, status: str):
        """Update a character's status."""
        if name in self.characters:
            self.characters[name].status = status
    
    def update_character_location(self, name: str, location: str):
        """Update a character's location."""
        if name in self.characters:
            self.characters[name].location = location
    
    def add_timeline_event(self, event: str):
        """Add an event to the timeline."""
        self.timeline.append(event)
    
    def resolve_conflict(self, conflict_description: str):
        """Mark a conflict as resolved."""
        for conflict in self.active_conflicts:
            if conflict_description.lower() in conflict.description.lower():
                conflict.resolution = "resolved"
    
    def get_alive_characters(self) -> List[str]:
        """Get list of characters still alive."""
        return [
            name for name, char in self.characters.items()
            if char.status == "alive"
        ]
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "characters": {
                name: {
                    "status": char.status,
                    "location": char.location,
                    "inventory": char.inventory
                }
                for name, char in self.characters.items()
            },
            "active_conflicts": [c.description for c in self.active_conflicts],
            "timeline": self.timeline,
            "current_beat": self.current_beat
        }