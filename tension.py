"""
Narrative Tension Index (NTI) Calculator - Phase 3
YOUR CLEVER DIFFERENTIATOR: Quantitative pacing control
"""

import re
import numpy as np
from typing import List, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import SAVE_THE_CAT_BEATS


class TensionAnalyzer:
    """Calculates Narrative Tension Index for scenes."""
    
    def __init__(self):
        """Initialize with sentiment analyzer."""
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
    
    def calculate_nti(self, text: str) -> float:
        """
        Calculate Narrative Tension Index.
        
        Formula: NTI = (1 - certainty) × (1 - sentiment)
        
        Where:
        - certainty: 0 (uncertain) to 1 (predictable)
        - sentiment: -1 (negative) to +1 (positive)
        
        Returns:
            Float between 0.0 (calm) and 2.0+ (extreme tension)
        """
        sentiment = self._calculate_sentiment(text)
        uncertainty = self._estimate_uncertainty(text)
        
        # NTI formula
        # High tension = uncertain + negative emotion
        # Low tension = certain + positive emotion
        nti = (1 - uncertainty) * (1 - sentiment)
        
        # Normalize to 0-2 range (can exceed 2 for extreme tension)
        nti = max(0.0, nti)
        
        return round(nti, 2)
    
    def _calculate_sentiment(self, text: str) -> float:
        """
        Calculate emotional valence using VADER.
        
        Returns:
            Float from -1 (negative) to +1 (positive)
        """
        scores = self.sentiment_analyzer.polarity_scores(text)
        return scores['compound']
    
    def _estimate_uncertainty(self, text: str) -> float:
        """
        Estimate narrative uncertainty using linguistic markers.
        
        Uncertainty indicators:
        - Questions (direct uncertainty)
        - Conditional language ("if", "maybe", "could", "might")
        - Incomplete information
        - Cliffhangers
        
        Returns:
            Float from 0.0 (certain) to 1.0 (uncertain)
        """
        text_lower = text.lower()
        sentences = re.split(r'[.!?]+', text)
        sentence_count = max(len([s for s in sentences if s.strip()]), 1)
        
        # Count uncertainty markers
        question_count = text.count('?')
        conditional_words = ['if', 'maybe', 'perhaps', 'could', 'might', 
                            'possibly', 'uncertain', 'unclear', 'wonder']
        conditional_count = sum(text_lower.count(word) for word in conditional_words)
        
        # Check for cliffhangers (ends with question or ellipsis)
        has_cliffhanger = text.strip().endswith(('?', '...', '…'))
        
        # Check for incomplete actions
        incomplete_markers = ['suddenly', 'before', 'just then', 'interrupted']
        incomplete_count = sum(text_lower.count(marker) for marker in incomplete_markers)
        
        # Calculate uncertainty score
        uncertainty = (
            (question_count / sentence_count) * 0.4 +
            (conditional_count / sentence_count) * 0.3 +
            (incomplete_count / sentence_count) * 0.2 +
            (0.1 if has_cliffhanger else 0)
        )
        
        return min(1.0, uncertainty)


class PacingController:
    """Controls story pacing using NTI feedback."""
    
    def __init__(self, num_beats: int = 15):
        """Initialize with target beat count."""
        self.num_beats = num_beats
        self.tension_history = []
        self.target_curve = self._generate_target_curve()
    
    def _generate_target_curve(self) -> List[float]:
        """
        Generate ideal tension curve based on Save the Cat structure.
        
        Returns:
            List of target NTI values for each beat
        """
        # Map beats to tension levels
        beat_tensions = {
            "Opening Image": 0.3,
            "Theme Stated": 0.35,
            "Setup": 0.4,
            "Catalyst": 0.7,
            "Debate": 0.6,
            "Break into Two": 0.75,
            "B Story": 0.5,
            "Fun and Games": 0.6,
            "Midpoint": 1.5,  # Major spike
            "Bad Guys Close In": 1.0,
            "All Is Lost": 1.3,
            "Dark Night of the Soul": 0.8,  # Brief respite
            "Break into Three": 1.0,
            "Finale": 1.8,  # Climax
            "Final Image": 0.2  # Resolution
        }
        
        curve = []
        for i in range(self.num_beats):
            if i < len(SAVE_THE_CAT_BEATS):
                beat_name = SAVE_THE_CAT_BEATS[i]["name"]
                curve.append(beat_tensions.get(beat_name, 0.5))
            else:
                # For extra beats, interpolate
                curve.append(0.5)
        
        return curve
    
    def get_adjustment_hint(
        self,
        beat_index: int,
        actual_nti: Optional[float] = None
    ) -> str:
        """
        Get pacing adjustment hint based on tension curve.
        
        Args:
            beat_index: Current beat number
            actual_nti: Actual NTI of previous scene (if available)
            
        Returns:
            String with pacing guidance for next scene
        """
        if beat_index >= len(self.target_curve):
            return "Maintain current pacing."
        
        target_nti = self.target_curve[beat_index]
        
        # If we have history, compare
        if actual_nti is not None:
            self.tension_history.append(actual_nti)
            
            # Check recent trend
            recent_avg = np.mean(self.tension_history[-3:]) if len(self.tension_history) >= 3 else actual_nti
            
            # Too low tension sustained
            if recent_avg < target_nti - 0.3:
                return "INJECT CONFLICT: Add unexpected complication, obstacle, or threat. Raise stakes."
            
            # Too high tension sustained
            elif recent_avg > target_nti + 0.3:
                return "PROVIDE RESPITE: Include moment of reflection, small victory, or emotional connection."
            
            # Tension is flat (boring)
            elif len(self.tension_history) >= 3 and np.std(self.tension_history[-3:]) < 0.1:
                return "ADD VARIETY: Introduce surprising element or shift emotional tone."
        
        # Default guidance based on beat type
        if target_nti > 1.2:
            return "HIGH TENSION: Escalate conflict dramatically. Make outcomes uncertain."
        elif target_nti > 0.7:
            return "RISING ACTION: Build tension steadily. Introduce complications."
        elif target_nti < 0.4:
            return "CALM RESOLUTION: Provide emotional closure. Tie up loose ends."
        else:
            return "BALANCED PACING: Maintain steady narrative momentum."
    
    def plot_curve(self, actual_history: Optional[List[float]] = None):
        """
        Generate plot data for tension curve visualization.
        
        Args:
            actual_history: Actual NTI values from generated scenes
            
        Returns:
            Dict with plot data
        """
        beats = list(range(len(self.target_curve)))
        
        plot_data = {
            "beats": beats,
            "target": self.target_curve,
            "actual": actual_history if actual_history else []
        }
        
        return plot_data


# Example usage and testing
if __name__ == "__main__":
    analyzer = TensionAnalyzer()
    
    # Test different scene types
    test_scenes = {
        "Action (High Tension)": """
            The explosion rocked the building. Glass shattered everywhere. 
            She ducked behind cover, heart pounding. How many were out there? 
            The footsteps drew closer. She checked her weapon—only two rounds left. 
            This might be it.
        """,
        
        "Romance (Low Tension)": """
            They sat together watching the sunset, her head on his shoulder. 
            The warm breeze carried the scent of jasmine. Everything felt perfect, 
            exactly as it should be. She smiled, knowing she'd found her home.
        """,
        
        "Tense Negotiation (Medium-High)": """
            "You have two choices," he said, sliding the contract across the table. 
            She read it carefully, mind racing. The terms were harsh, but refusal 
            could mean disaster. What would she sacrifice? Her principles or her people?
        """,
        
        "Resolution (Very Low)": """
            The war was over. The village began to rebuild. Children played in the 
            streets again, their laughter echoing off the restored walls. She stood 
            watching, finally at peace, knowing they had won something worth keeping.
        """
    }
    
    print("=== NARRATIVE TENSION INDEX TESTS ===\n")
    
    for scene_type, text in test_scenes.items():
        nti = analyzer.calculate_nti(text)
        print(f"{scene_type}")
        print(f"  NTI: {nti}")
        print(f"  Interpretation: ", end="")
        
        if nti < 0.3:
            print("Very calm, peaceful")
        elif nti < 0.6:
            print("Low tension, steady")
        elif nti < 1.0:
            print("Moderate tension, engaging")
        elif nti < 1.5:
            print("High tension, gripping")
        else:
            print("Extreme tension, climactic")
        
        print()
    
    # Test pacing controller
    print("\n=== PACING CONTROLLER TEST ===\n")
    controller = PacingController(num_beats=15)
    
    # Simulate some beats
    simulated_ntis = [0.3, 0.4, 0.5, 0.8, 0.6]
    
    for i, nti in enumerate(simulated_ntis):
        hint = controller.get_adjustment_hint(i, nti)
        target = controller.target_curve[i]
        print(f"Beat {i+1}: Actual={nti}, Target={target}")
        print(f"  Guidance: {hint}\n")