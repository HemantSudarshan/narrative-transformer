"""
Scene Generation Engine - Phase 4
Generates individual scenes with full context awareness.
"""

import json
import re
from typing import List, Tuple, Optional
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

from config import DEFAULT_CONFIG, GENRE_TEMPLATES
from models import (
    SceneOutput, StoryState, WorldMapping, PlotBeat
)
from tension import TensionAnalyzer


class SceneGenerator:
    """Generates narrative scenes with context awareness."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize generator."""
        self.config = DEFAULT_CONFIG
        self.model = model or self.config.default_model
        self.tension_analyzer = TensionAnalyzer()
        
        if self.config.get_primary_api() == "gemini":
            genai.configure(api_key=self.config.gemini_api_key)
            self.client = genai.GenerativeModel(self.model)
            self.api_type = "gemini"
        elif self.config.get_primary_api() == "openai":
            client_kwargs = {"api_key": self.config.openai_api_key}
            if self.config.openai_base_url:
                client_kwargs["base_url"] = self.config.openai_base_url
                # OpenRouter requires these headers
                client_kwargs["default_headers"] = {
                    "HTTP-Referer": "https://github.com/narrative-transformer",
                    "X-Title": "Narrative Transformer"
                }
            self.client = OpenAI(**client_kwargs)
            self.api_type = "openai"
        elif self.config.get_primary_api() == "anthropic":
            self.client = Anthropic(api_key=self.config.anthropic_api_key)
            self.api_type = "anthropic"
        else:
            raise ValueError("No valid API key configured.")
    
    def generate_scene(
        self,
        beat_info: PlotBeat,
        world_mapping: WorldMapping,
        story_state: StoryState,
        pacing_hint: str,
        previous_scenes_summary: str,
        target_length: int = 400
    ) -> SceneOutput:
        """
        Generate a single scene with full context.
        
        Args:
            beat_info: Information about current beat
            world_mapping: World element mappings
            story_state: Current story state
            pacing_hint: Guidance from pacing controller
            previous_scenes_summary: Summary of recent scenes
            target_length: Target word count
            
        Returns:
            SceneOutput with generated text and metadata
        """
        print(f"  ✍️  Generating: {beat_info.name}...")
        
        # Get genre template
        genre_template = GENRE_TEMPLATES[world_mapping.genre]
        
        # Build comprehensive context
        prompt = self._build_generation_prompt(
            beat_info=beat_info,
            genre_template=genre_template,
            world_mapping=world_mapping,
            story_state=story_state,
            pacing_hint=pacing_hint,
            previous_summary=previous_scenes_summary,
            target_length=target_length
        )
        
        # Generate scene
        response_text = self._call_llm(prompt)
        
        # Parse output
        scene_output = self._parse_scene_output(
            response_text,
            beat_info,
            story_state
        )
        
        return scene_output
    
    def _build_generation_prompt(
        self,
        beat_info: PlotBeat,
        genre_template,
        world_mapping: WorldMapping,
        story_state: StoryState,
        pacing_hint: str,
        previous_summary: str,
        target_length: int
    ) -> str:
        """Build the master generation prompt with all context."""
        
        # Format character states
        char_states = []
        for name, char in story_state.characters.items():
            state_str = f"{name} ({char.role}): {char.status}"
            if char.location:
                state_str += f", currently at {char.location}"
            if char.inventory:
                state_str += f", has {', '.join(char.inventory)}"
            char_states.append(state_str)
        
        # Format active conflicts
        conflicts = [c.description for c in story_state.active_conflicts 
                    if not c.resolution]
        
        # Build prompt
        prompt = f"""You are writing a scene for a {genre_template.name} narrative transformation.

<world_rules>
Genre: {genre_template.name}
Tone: {genre_template.tone}
Technology: {genre_template.technology_level}
Aesthetics: {', '.join(genre_template.key_aesthetics)}

World Rules:
{chr(10).join(f'- {rule}' for rule in world_mapping.world_rules)}
</world_rules>

<story_state>
Active Characters:
{chr(10).join(char_states)}

Active Conflicts:
{chr(10).join(f'- {c}' for c in conflicts)}

Timeline So Far:
{chr(10).join(f'- {event}' for event in story_state.timeline[-5:])}
</story_state>

<narrative_context>
Current Beat: {beat_info.index + 1}/15 - {beat_info.name}
Beat Function: {beat_info.function}
Target Emotion: {beat_info.target_emotion}
Source Events: {', '.join(beat_info.source_events) if beat_info.source_events else 'None specified'}

PACING DIRECTIVE: {pacing_hint}
</narrative_context>

<previous_context>
{previous_summary if previous_summary else "This is the opening scene."}
</previous_context>

<character_mappings>
{chr(10).join(f'{m.source} → {m.target} ({m.narrative_function})' for m in world_mapping.character_mappings)}
</character_mappings>

<generation_instructions>
Write a scene that:
- Is approximately {target_length} words
- Uses {genre_template.name} aesthetic (show, don't tell)
- Advances the plot toward: {beat_info.function}
- Maintains continuity with previous scenes
- Respects character states (dead characters cannot act or speak)
- Uses ONLY the mapped target names (never source names)
- Follows the pacing directive above
- Evokes the target emotion: {beat_info.target_emotion}

Writing Style: {genre_template.style_guidance}

CRITICAL: Use immersive, vivid prose that matches the genre. Include sensory details.
Make dialogue natural and character-appropriate.

After writing the scene, provide metadata in this format:

<metadata>
CHARACTERS: [comma-separated list of characters who appear]
LOCATION: [where this scene takes place]
EMOTION: [primary emotion: positive/negative/neutral]
STATE_CHANGES: [any changes - deaths, location moves, item transfers, etc.]
HOOKS: [unresolved questions or tensions that propel story forward]
</metadata>
</generation_instructions>

Write the scene now:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM API for generation."""
        try:
            if self.api_type == "gemini":
                # For Gemini, prepend system instruction to prompt
                full_prompt = "You are a creative writer specializing in immersive storytelling.\n\n" + prompt
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.8,
                        max_output_tokens=1500,
                    )
                )
                return response.text
            
            elif self.api_type == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a creative writer specializing in immersive storytelling."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,  # Higher for creativity
                    max_tokens=1500
                )
                return response.choices[0].message.content
            
            elif self.api_type == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.8,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
        
        except Exception as e:
            print(f"    ❌ Generation error: {e}")
            raise
    
    def _parse_scene_output(
        self,
        response_text: str,
        beat_info: PlotBeat,
        story_state: StoryState
    ) -> SceneOutput:
        """Parse generated scene and extract metadata."""
        
        # Split scene text from metadata
        if "<metadata>" in response_text:
            parts = response_text.split("<metadata>")
            scene_text = parts[0].strip()
            metadata_text = parts[1].split("</metadata>")[0] if "</metadata>" in parts[1] else parts[1]
        else:
            scene_text = response_text.strip()
            metadata_text = ""
        
        # Parse metadata
        characters = self._extract_field(metadata_text, "CHARACTERS")
        location = self._extract_field(metadata_text, "LOCATION", default="Unknown")
        emotion_str = self._extract_field(metadata_text, "EMOTION", default="neutral")
        state_changes_str = self._extract_field(metadata_text, "STATE_CHANGES")
        hooks_str = self._extract_field(metadata_text, "HOOKS")
        
        # Parse emotion
        emotional_valence = 0.0
        if "positive" in emotion_str.lower():
            emotional_valence = 0.5
        elif "negative" in emotion_str.lower():
            emotional_valence = -0.5
        
        # Calculate NTI
        tension_score = self.tension_analyzer.calculate_nti(scene_text)
        
        # Parse state updates
        state_updates = self._parse_state_changes(state_changes_str)
        
        # Parse characters and hooks
        characters_list = [c.strip() for c in characters.split(',')] if characters else []
        hooks_list = [h.strip() for h in hooks_str.split(';')] if hooks_str else []
        
        return SceneOutput(
            beat_index=beat_info.index,
            beat_name=beat_info.name,
            text=scene_text,
            characters_involved=characters_list,
            location=location,
            emotional_valence=emotional_valence,
            tension_score=tension_score,
            state_updates=state_updates,
            unresolved_hooks=hooks_list
        )
    
    def _extract_field(self, text: str, field_name: str, default: str = "") -> str:
        """Extract a field from metadata text."""
        pattern = f"{field_name}:\\s*(.+?)(?=\\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else default
    
    def _parse_state_changes(self, changes_str: str) -> dict:
        """Parse state changes from string."""
        changes = {}
        
        if not changes_str:
            return changes
        
        # Look for death mentions
        if "dies" in changes_str.lower() or "killed" in changes_str.lower() or "death" in changes_str.lower():
            changes["deaths"] = []
            # Try to extract names
            for line in changes_str.split(','):
                if any(word in line.lower() for word in ["dies", "killed", "death"]):
                    changes["deaths"].append(line.strip())
        
        # Look for location changes
        if "moves to" in changes_str.lower() or "travels to" in changes_str.lower():
            changes["location_changes"] = changes_str
        
        # Look for item transfers
        if "gets" in changes_str.lower() or "receives" in changes_str.lower() or "finds" in changes_str.lower():
            changes["item_transfers"] = changes_str
        
        return changes
    
    def validate_scene(
        self,
        scene: SceneOutput,
        state: StoryState
    ) -> Tuple[bool, List[str]]:
        """
        Validate scene for logical consistency.
        
        Args:
            scene: Generated scene
            state: Current story state
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check 1: Dead characters shouldn't appear
        for char_name in scene.characters_involved:
            if char_name in state.characters:
                if state.characters[char_name].status == "dead":
                    errors.append(f"Dead character '{char_name}' appears in scene")
        
        # Check 2: Characters should exist in mapping
        for char_name in scene.characters_involved:
            if char_name not in state.characters:
                errors.append(f"Unknown character '{char_name}' appears")
        
        # Check 3: Scene should have content
        if len(scene.text.split()) < 50:
            errors.append("Scene is too short")
        
        # Check 4: Should advance the story
        if not scene.text.strip():
            errors.append("Scene is empty")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def update_story_state(
        self,
        current_state: StoryState,
        scene_output: SceneOutput
    ) -> StoryState:
        """
        Apply state changes from a scene.
        
        Args:
            current_state: Current state
            scene_output: Scene with updates
            
        Returns:
            Updated StoryState
        """
        # Apply deaths
        if "deaths" in scene_output.state_updates:
            for death_desc in scene_output.state_updates["deaths"]:
                # Try to extract character name
                for char_name in current_state.characters.keys():
                    if char_name.lower() in death_desc.lower():
                        current_state.update_character_status(char_name, "dead")
                        current_state.add_timeline_event(f"{char_name} died")
        
        # Apply location changes
        if "location_changes" in scene_output.state_updates:
            for char_name in scene_output.characters_involved:
                current_state.update_character_location(char_name, scene_output.location)
        
        # Add scene to timeline
        summary = f"{scene_output.beat_name}: {scene_output.location}"
        current_state.add_timeline_event(summary)
        
        # Update current beat
        current_state.current_beat = scene_output.beat_index
        
        return current_state


# Example usage
if __name__ == "__main__":
    from models import Character, PlotBeat, Conflict, SourceAnalysis, WorldMapping, ElementMapping, StoryState
    
    # Mock data for testing
    test_beat = PlotBeat(
        index=0,
        name="Opening Image",
        function="Show protagonist's world before change",
        source_events=["Romeo pines for Rosaline"],
        target_emotion="curiosity",
        typical_length=300
    )
    
    test_mapping = WorldMapping(
        genre="cyberpunk",
        character_mappings=[
            ElementMapping("Romeo", "Rom-30", "character", "young hacker")
        ],
        location_mappings=[
            ElementMapping("Verona", "Neo-Verona", "location", "megacity")
        ],
        object_mappings=[],
        concept_mappings=[],
        world_rules=["High tech, low life"]
    )
    
    test_state = StoryState(
        characters={
            "Rom-30": Character(
                name="Rom-30",
                role="hero",
                traits=["impulsive", "skilled"],
                desires=["recognition"],
                fears=["loneliness"],
                arc="learns patience",
                status="alive",
                location="Neo-Verona slums"
            )
        },
        active_conflicts=[],
        timeline=[],
        current_beat=0
    )
    
    generator = SceneGenerator()
    
    scene = generator.generate_scene(
        beat_info=test_beat,
        world_mapping=test_mapping,
        story_state=test_state,
        pacing_hint="Establish world and character",
        previous_scenes_summary="",
        target_length=300
    )
    
    print("=== GENERATED SCENE ===")
    print(scene.text)
    print(f"\n=== METADATA ===")
    print(f"Tension: {scene.tension_score}")
    print(f"Characters: {scene.characters_involved}")
    print(f"Location: {scene.location}")
    
    # Validate
    is_valid, errors = generator.validate_scene(scene, test_state)
    print(f"\nValid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")