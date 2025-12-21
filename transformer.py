"""
Narrative Transformer - Phase 5
Main orchestrator that coordinates the full pipeline.
"""

from typing import Tuple, Dict, List, Optional
from analyzer import SourceAnalyzer
from mapper import WorldMapper
from generator import SceneGenerator
from tension import PacingController
from models import StoryState


class NarrativeTransformer:
    """Main class that orchestrates narrative transformation."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize all components."""
        self.analyzer = SourceAnalyzer(model)
        self.mapper = WorldMapper(model)
        self.generator = SceneGenerator(model)
        self.pacer = None  # Initialized per transformation
    
    def transform(
        self,
        source_text: str,
        source_title: str,
        target_genre: str,
        num_beats: int = 12
    ) -> Tuple[str, Dict]:
        """
        Full transformation pipeline.
        
        Args:
            source_text: Source narrative text
            source_title: Title of source work
            target_genre: Target genre (must be in GENRE_TEMPLATES)
            num_beats: Number of story beats to generate
            
        Returns:
            (final_story_text, transformation_metadata)
        """
        print(f"\n{'='*60}")
        print(f"NARRATIVE TRANSFORMATION PIPELINE")
        print(f"Source: {source_title}")
        print(f"Target: {target_genre}")
        print(f"Beats: {num_beats}")
        print(f"{'='*60}\n")
        
        # STEP 1: Analyze source
        print("STEP 1/5: Analyzing source material...")
        analysis = self.analyzer.analyze(source_text, source_title)
        print(f"  ✅ Extracted {len(analysis.characters)} characters, {len(analysis.themes)} themes\n")
        
        # STEP 2: Create world mapping
        print("STEP 2/5: Creating world mapping...")
        mapping = self.mapper.create_mapping(analysis, target_genre)
        print(f"  ✅ Mapped {len(mapping.character_mappings)} characters to {target_genre}\n")
        
        # STEP 3: Initialize story state and pacing
        print("STEP 3/5: Initializing story state...")
        state = StoryState.from_analysis(analysis, mapping)
        self.pacer = PacingController(num_beats)
        print(f"  ✅ {len(state.characters)} characters ready\n")
        
        # STEP 4: Generate scenes beat by beat
        print(f"STEP 4/5: Generating {num_beats} story beats...")
        scenes = []
        tension_history = []
        
        # Use beats from analysis if available, otherwise use num_beats
        beats_to_use = analysis.beats[:num_beats] if len(analysis.beats) >= num_beats else analysis.beats
        
        # Pad if needed
        from config import SAVE_THE_CAT_BEATS
        while len(beats_to_use) < num_beats:
            idx = len(beats_to_use)
            template = SAVE_THE_CAT_BEATS[min(idx, len(SAVE_THE_CAT_BEATS)-1)]
            from models import PlotBeat
            beats_to_use.append(PlotBeat(
                index=idx,
                name=template["name"],
                function=template["function"],
                source_events=[],
                target_emotion=template["target_emotion"],
                typical_length=template["typical_length"]
            ))
        
        for beat_idx in range(num_beats):
            beat = beats_to_use[beat_idx]
            beat.index = beat_idx  # Ensure correct index
            
            # Get pacing hint
            prev_nti = tension_history[-1] if tension_history else None
            pacing_hint = self.pacer.get_adjustment_hint(beat_idx, prev_nti)
            
            # Generate scene
            scene = self.generator.generate_scene(
                beat_info=beat,
                world_mapping=mapping,
                story_state=state,
                pacing_hint=pacing_hint,
                previous_scenes_summary=self._summarize_recent(scenes, n=3),
                target_length=self._calculate_scene_length(beat_idx, num_beats)
            )
            
            # Validate
            is_valid, errors = self.generator.validate_scene(scene, state)
            if not is_valid:
                print(f"    ⚠️  Validation warnings: {errors}")
            
            # Update state
            state = self.generator.update_story_state(state, scene)
            
            # Track
            tension_history.append(scene.tension_score)
            scenes.append(scene)
            
            print(f"    ✓ Beat {beat_idx + 1}/{num_beats}: {beat.name} (NTI: {scene.tension_score})")
        
        print("\n")
        
        # STEP 5: Assemble final story
        print("STEP 5/5: Assembling final story...")
        final_story = self._assemble_story(scenes, mapping, analysis)
        
        # Compile metadata
        metadata = {
            "source_title": source_title,
            "target_genre": target_genre,
            "total_beats": num_beats,
            "tension_curve": tension_history,
            "avg_tension": sum(tension_history) / len(tension_history),
            "character_fates": self._get_character_fates(state),
            "word_count": len(final_story.split()),
            "world_mapping": mapping.to_dict(),
            "source_analysis": analysis.to_dict()
        }
        
        print(f"  ✅ Story complete: {metadata['word_count']} words\n")
        print(f"{'='*60}\n")
        
        return final_story, metadata
    
    def _summarize_recent(self, scenes: List, n: int = 3) -> str:
        """Summarize last N scenes for context."""
        if not scenes:
            return ""
        
        recent = scenes[-n:]
        summary_parts = []
        
        for scene in recent:
            summary_parts.append(
                f"{scene.beat_name}: {scene.text[:100]}..."
            )
        
        return "\n\n".join(summary_parts)
    
    def _calculate_scene_length(self, beat_idx: int, total: int) -> int:
        """
        Calculate target scene length based on position in story.
        Shorter at start/end, longer in middle.
        """
        # Create a bell curve effect
        middle = total / 2
        distance_from_middle = abs(beat_idx - middle)
        normalized_distance = distance_from_middle / middle
        
        # Length ranges from 250 to 500 words
        min_length = 250
        max_length = 500
        length = max_length - (normalized_distance * (max_length - min_length))
        
        return int(length)
    
    def _assemble_story(self, scenes: List, mapping, analysis) -> str:
        """Assemble final story with title and transitions."""
        
        # Create title
        title = f"{analysis.title}: A {mapping.genre.title()} Reimagining"
        
        # Opening paragraph
        from config import GENRE_TEMPLATES
        genre_template = GENRE_TEMPLATES[mapping.genre]
        
        opening = f"""
{title}
{'='*len(title)}

A transformation of the classic tale into a {genre_template.name} setting.

"""
        
        # Assemble scenes with transitions
        story_parts = [opening]
        
        for i, scene in enumerate(scenes):
            # Add scene number/title
            story_parts.append(f"\n## {scene.beat_name}\n")
            story_parts.append(scene.text)
            story_parts.append("\n")
        
        # Add epilogue if final beat is not "Final Image"
        if scenes and scenes[-1].beat_name != "Final Image":
            epilogue = "\n## Epilogue\n\nAnd so our tale concludes, transformed yet timeless.\n"
            story_parts.append(epilogue)
        
        return "".join(story_parts)
    
    def _get_character_fates(self, state: StoryState) -> Dict[str, str]:
        """Get summary of what happened to each character."""
        fates = {}
        
        for name, char in state.characters.items():
            fate_parts = []
            
            # Status
            fate_parts.append(char.status)
            
            # Final location
            if char.location:
                fate_parts.append(f"last seen at {char.location}")
            
            # Notable items
            if char.inventory:
                fate_parts.append(f"possessing {', '.join(char.inventory)}")
            
            fates[name] = " - ".join(fate_parts)
        
        return fates


# Example usage
if __name__ == "__main__":
    sample_text = """
    Two households, both alike in dignity,
    In fair Verona, where we lay our scene,
    From ancient grudge break to new mutiny,
    Where civil blood makes civil hands unclean.
    From forth the fatal loins of these two foes
    A pair of star-cross'd lovers take their life.
    
    Romeo, of the Montague family, is a young man prone to passionate love.
    He meets Juliet, of the rival Capulet family, at a ball and they fall
    instantly in love, despite their families' hatred. They marry in secret,
    but tragedy strikes when Romeo is banished for killing Juliet's cousin
    Tybalt in a duel. Through a series of miscommunications and desperate
    plans, both lovers ultimately die, finally ending the feud between their
    families.
    """
    
    transformer = NarrativeTransformer()
    story, metadata = transformer.transform(
        source_text=sample_text,
        source_title="Romeo and Juliet",
        target_genre="cyberpunk",
        num_beats=8
    )
    
    print("\n=== GENERATED STORY (excerpt) ===")
    print(story[:1000])
    print("\n... [story continues] ...\n")
    
    print("=== METADATA ===")
    print(f"Word count: {metadata['word_count']}")
    print(f"Average tension: {metadata['avg_tension']:.2f}")
    print(f"Character fates: {metadata['character_fates']}")