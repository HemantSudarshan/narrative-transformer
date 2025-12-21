"""
World Mapping Engine - Phase 2
Maps source elements to target genre systematically.
"""

import json
import re
from typing import Optional
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

from config import DEFAULT_CONFIG, GENRE_TEMPLATES
from models import SourceAnalysis, WorldMapping, ElementMapping


class WorldMapper:
    """Maps source narrative elements to target genre."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize mapper with API client."""
        self.config = DEFAULT_CONFIG
        self.model = model or self.config.default_model
        
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
    
    def create_mapping(
        self,
        analysis: SourceAnalysis,
        target_genre: str
    ) -> WorldMapping:
        """
        Create systematic mapping from source to target world.
        
        Args:
            analysis: SourceAnalysis from analyzer
            target_genre: Target genre (must be in GENRE_TEMPLATES)
            
        Returns:
            WorldMapping with all element translations
        """
        if target_genre not in GENRE_TEMPLATES:
            raise ValueError(f"Unknown genre: {target_genre}. Available: {list(GENRE_TEMPLATES.keys())}")
        
        genre_template = GENRE_TEMPLATES[target_genre]
        print(f"🗺️  Mapping to {genre_template.name}...")
        
        # Create mapping prompt
        prompt = self._create_mapping_prompt(analysis, genre_template)
        
        # Call LLM
        response_text = self._call_llm(prompt)
        
        # Parse response
        mapping = self._parse_mapping(response_text, target_genre, genre_template)
        
        print(f"✅ Mapping complete: {len(mapping.character_mappings)} characters mapped")
        return mapping
    
    def _create_mapping_prompt(self, analysis: SourceAnalysis, genre_template) -> str:
        """Create the mapping prompt."""
        
        # Serialize analysis for context
        analysis_summary = {
            "characters": [
                {"name": c.name, "role": c.role, "traits": c.traits}
                for c in analysis.characters
            ],
            "setting": analysis.setting,
            "symbols": analysis.symbols,
            "conflicts": [c.description for c in analysis.conflicts]
        }
        
        prompt = f"""You are a world-building expert specializing in narrative adaptation. 
Your task is to map elements from a source story to a {genre_template.name} setting.

=== TARGET GENRE: {genre_template.name.upper()} ===

GENRE CHARACTERISTICS:
- Tone: {genre_template.tone}
- Technology Level: {genre_template.technology_level}
- Key Aesthetics: {', '.join(genre_template.key_aesthetics)}
- Naming Conventions: {', '.join(genre_template.naming_conventions)}

WORLD RULES:
{chr(10).join(f'- {rule}' for rule in genre_template.world_rules)}

=== SOURCE NARRATIVE ===
{json.dumps(analysis_summary, indent=2)}

=== MAPPING TASK ===

For each element in the source, create a target equivalent that:
1. Preserves narrative function (a weapon stays a weapon)
2. Maintains symbolic meaning
3. Fits the target genre's logic and aesthetics
4. Uses appropriate naming conventions
5. Respects the world rules

OUTPUT FORMAT (JSON only, no other text):
{{
  "characters": [
    {{
      "source_name": "Original Name",
      "target_name": "New Name",
      "target_role": "role in target world",
      "target_description": "brief description fitting genre",
      "preserved_traits": ["trait1", "trait2"],
      "narrative_function": "what role they serve"
    }}
  ],
  "locations": [
    {{
      "source": "Original Location",
      "target": "New Location",
      "description": "how it looks in target world",
      "narrative_function": "why this place matters"
    }}
  ],
  "objects": [
    {{
      "source": "Original Object",
      "target": "New Object",
      "symbolic_meaning": "what it represents",
      "narrative_function": "how it's used in story"
    }}
  ],
  "concepts": [
    {{
      "source": "Original Concept (e.g., family honor)",
      "target": "New Concept (e.g., corporate reputation)",
      "how_manifests": "how this concept appears in target world"
    }}
  ]
}}

IMPORTANT:
- Be creative but internally consistent
- All names must fit the genre's conventions
- Preserve the emotional weight of symbols
- Output ONLY valid JSON

Begin mapping:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM API."""
        try:
            if self.api_type == "gemini":
                # For Gemini, prepend system instruction to prompt
                full_prompt = "You are a creative world-building expert. Always respond with valid JSON.\n\n" + prompt
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.8,
                        max_output_tokens=2000,
                    )
                )
                return response.text
            
            elif self.api_type == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a creative world-building expert. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,  # Higher for creativity
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            elif self.api_type == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.8,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
        
        except Exception as e:
            print(f"❌ API Error: {e}")
            raise
    
    def _parse_mapping(self, response_text: str, genre: str, genre_template) -> WorldMapping:
        """Parse LLM response into WorldMapping."""
        
        # Clean response
        json_text = response_text.strip()
        if json_text.startswith("```"):
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'```\s*$', '', json_text)
        
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse mapping JSON: {e}")
            raise
        
        # Parse character mappings
        char_mappings = []
        for char in data.get("characters", []):
            char_mappings.append(ElementMapping(
                source=char["source_name"],
                target=char["target_name"],
                category="character",
                narrative_function=char.get("narrative_function", ""),
                symbolic_meaning=None
            ))
        
        # Parse location mappings
        loc_mappings = []
        for loc in data.get("locations", []):
            loc_mappings.append(ElementMapping(
                source=loc["source"],
                target=loc["target"],
                category="location",
                narrative_function=loc.get("narrative_function", ""),
                symbolic_meaning=None
            ))
        
        # Parse object mappings
        obj_mappings = []
        for obj in data.get("objects", []):
            obj_mappings.append(ElementMapping(
                source=obj["source"],
                target=obj["target"],
                category="object",
                narrative_function=obj.get("narrative_function", ""),
                symbolic_meaning=obj.get("symbolic_meaning", None)
            ))
        
        # Parse concept mappings
        concept_mappings = []
        for concept in data.get("concepts", []):
            concept_mappings.append(ElementMapping(
                source=concept["source"],
                target=concept["target"],
                category="concept",
                narrative_function=concept.get("how_manifests", ""),
                symbolic_meaning=None
            ))
        
        return WorldMapping(
            genre=genre,
            character_mappings=char_mappings,
            location_mappings=loc_mappings,
            object_mappings=obj_mappings,
            concept_mappings=concept_mappings,
            world_rules=genre_template.world_rules
        )


if __name__ == "__main__":
    # Test with mock analysis
    from models import Character, PlotBeat, Conflict
    
    test_analysis = SourceAnalysis(
        title="Romeo and Juliet",
        characters=[
            Character("Romeo", "hero", ["impulsive", "romantic"], ["love"], ["loss"], "matures"),
            Character("Juliet", "heroine", ["brave", "loyal"], ["freedom"], ["family"], "grows independent")
        ],
        themes=["love vs duty", "fate"],
        beats=[],
        conflicts=[
            Conflict("interpersonal", "Montague vs Capulet feud", ["Montague", "Capulet"])
        ],
        symbols={"poison": "death/betrayal"},
        setting="Verona, Renaissance Italy",
        tone="tragic romance",
        central_question="Can love transcend family loyalty?"
    )
    
    mapper = WorldMapper()
    mapping = mapper.create_mapping(test_analysis, "cyberpunk")
    
    print("\n=== MAPPING RESULTS ===")
    for m in mapping.character_mappings:
        print(f"{m.source} → {m.target}")