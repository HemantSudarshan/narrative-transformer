"""
Source Analysis Engine - Phase 1
Extracts narrative DNA from source material.
"""

import json
import re
from typing import Optional
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

from config import DEFAULT_CONFIG, SAVE_THE_CAT_BEATS
from models import (
    SourceAnalysis, Character, PlotBeat, Conflict
)


class SourceAnalyzer:
    """Analyzes source narratives to extract structural elements."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize analyzer with API client."""
        self.config = DEFAULT_CONFIG
        self.model = model or self.config.default_model
        
        # Initialize appropriate client
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
            raise ValueError("No valid API key configured. Check your .env file.")
    
    def analyze(self, source_text: str, source_title: str) -> SourceAnalysis:
        """
        Extract narrative structure from source material.
        
        Args:
            source_text: The text to analyze
            source_title: Title of the source work
            
        Returns:
            SourceAnalysis object with extracted elements
        """
        print(f"📖 Analyzing '{source_title}'...")
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(source_text, source_title)
        
        # Call LLM
        response_text = self._call_llm(prompt)
        
        # Parse response
        analysis = self._parse_analysis(response_text, source_title)
        
        print(f"✅ Analysis complete: {len(analysis.characters)} characters, {len(analysis.beats)} beats")
        return analysis
    
    def _create_analysis_prompt(self, source_text: str, source_title: str) -> str:
        """Create the analysis prompt with structured output format."""
        
        prompt = f"""You are a narrative structure analyst. Analyze the following text systematically and extract its narrative DNA.

SOURCE: {source_title}
TEXT:
{source_text[:8000]}  

TASK: Perform a comprehensive narrative analysis following these steps:

STEP 1: IDENTIFY CHARACTERS
For each major character, extract:
- Name
- Role (hero, mentor, villain, ally, love interest, etc.)
- Key personality traits (3-5 traits)
- Desires (what they want)
- Fears (what they're afraid of)
- Character arc (how they change or should change)

STEP 2: EXTRACT THEMES
Identify 3-5 universal themes this narrative explores.
Examples: love vs duty, individual vs society, power corrupts, redemption, etc.

STEP 3: MAP PLOT STRUCTURE
Map the narrative to Save the Cat beat structure (15 beats).
For each beat that applies to this story:
- Beat name (from Save the Cat structure)
- What happens in the source text for this beat
- Key events

STEP 4: IDENTIFY CONFLICTS
List all major conflicts:
- Type (internal, external, interpersonal)
- Description
- Who is involved

STEP 5: SYMBOLS AND MEANINGS
Identify key symbols and what they represent.

STEP 6: SETTING AND TONE
- Where/when does this take place?
- What is the overall emotional tone?

STEP 7: CENTRAL QUESTION
What is the central dramatic question this narrative asks?

OUTPUT FORMAT:
Provide your analysis as a JSON object with this EXACT structure:

{{
  "characters": [
    {{
      "name": "Character Name",
      "role": "hero/mentor/villain/etc",
      "traits": ["trait1", "trait2", "trait3"],
      "desires": ["desire1", "desire2"],
      "fears": ["fear1", "fear2"],
      "arc": "description of character transformation"
    }}
  ],
  "themes": ["theme1", "theme2", "theme3"],
  "beats": [
    {{
      "name": "Opening Image",
      "source_events": ["event1", "event2"]
    }}
  ],
  "conflicts": [
    {{
      "type": "internal/external/interpersonal",
      "description": "conflict description",
      "parties": ["party1", "party2"]
    }}
  ],
  "symbols": {{
    "symbol1": "meaning1",
    "symbol2": "meaning2"
  }},
  "setting": "setting description",
  "tone": "tone description",
  "central_question": "the central dramatic question"
}}

IMPORTANT:
- Output ONLY valid JSON, no other text
- No markdown formatting or code blocks
- Be thorough but concise
- Focus on elements that are narratively essential

Begin analysis:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API with error handling."""
        try:
            if self.api_type == "gemini":
                # For Gemini, prepend system instruction to prompt
                full_prompt = "You are a narrative analysis expert. Always respond with valid JSON.\n\n" + prompt
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=self.config.temperature,
                        max_output_tokens=self.config.max_tokens,
                    )
                )
                return response.text
            
            elif self.api_type == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a narrative analysis expert. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                return response.choices[0].message.content
            
            elif self.api_type == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
        
        except Exception as e:
            print(f"❌ API Error: {e}")
            raise
    
    def _parse_analysis(self, response_text: str, title: str) -> SourceAnalysis:
        """Parse LLM response into SourceAnalysis object."""
        
        # Extract JSON from response (handle markdown code blocks)
        json_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if json_text.startswith("```"):
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'```\s*$', '', json_text)
        
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response was: {response_text[:500]}...")
            raise
        
        # Parse characters
        characters = []
        for char_data in data.get("characters", []):
            characters.append(Character(
                name=char_data["name"],
                role=char_data["role"],
                traits=char_data.get("traits", []),
                desires=char_data.get("desires", []),
                fears=char_data.get("fears", []),
                arc=char_data.get("arc", "")
            ))
        
        # Parse beats
        beats = []
        beat_data_list = data.get("beats", [])
        for i, beat_data in enumerate(beat_data_list):
            # Match to Save the Cat structure
            beat_name = beat_data["name"]
            matching_beat = next(
                (b for b in SAVE_THE_CAT_BEATS if b["name"] == beat_name),
                SAVE_THE_CAT_BEATS[min(i, len(SAVE_THE_CAT_BEATS)-1)]
            )
            
            beats.append(PlotBeat(
                index=i,
                name=beat_name,
                function=matching_beat["function"],
                source_events=beat_data.get("source_events", []),
                target_emotion=matching_beat["target_emotion"],
                typical_length=matching_beat["typical_length"]
            ))
        
        # Parse conflicts
        conflicts = []
        for conf_data in data.get("conflicts", []):
            conflicts.append(Conflict(
                type=conf_data["type"],
                description=conf_data["description"],
                parties_involved=conf_data.get("parties", [])
            ))
        
        return SourceAnalysis(
            title=title,
            characters=characters,
            themes=data.get("themes", []),
            beats=beats,
            conflicts=conflicts,
            symbols=data.get("symbols", {}),
            setting=data.get("setting", ""),
            tone=data.get("tone", ""),
            central_question=data.get("central_question", "")
        )


# Example usage
if __name__ == "__main__":
    # Test with Romeo & Juliet excerpt
    sample_text = """
    Two households, both alike in dignity,
    In fair Verona, where we lay our scene,
    From ancient grudge break to new mutiny,
    Where civil blood makes civil hands unclean.
    From forth the fatal loins of these two foes
    A pair of star-cross'd lovers take their life;
    
    [Act 1, Scene 1: A public square in Verona. Servants of the Capulet and Montague
    households brawl in the streets. Prince Escalus intervenes and threatens death
    to anyone who disturbs the peace again.]
    
    [Act 1, Scene 5: The Capulet ball. Romeo, a Montague, sneaks in and sees Juliet
    for the first time. They fall instantly in love, then discover they are from
    rival families.]
    """
    
    analyzer = SourceAnalyzer()
    analysis = analyzer.analyze(sample_text, "Romeo and Juliet")
    
    print("\n=== ANALYSIS RESULTS ===")
    print(f"Characters: {[c.name for c in analysis.characters]}")
    print(f"Themes: {analysis.themes}")
    print(f"Beats: {[b.name for b in analysis.beats]}")
    print(f"Central Question: {analysis.central_question}")