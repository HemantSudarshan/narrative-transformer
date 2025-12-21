#!/usr/bin/env python
"""
Test script to run 3 different transformations and verify outputs
"""
import sys
import os

# Force fresh environment
for module in list(sys.modules.keys()):
    if module.startswith(('config', 'analyzer', 'mapper', 'generator', 'transformer', 'models', 'tension')):
        del sys.modules[module]

from dotenv import load_dotenv
load_dotenv(override=True)

from transformer import NarrativeTransformer

print("="*70)
print("TESTING NARRATIVE TRANSFORMER WITH 3 DIFFERENT STORIES")
print("="*70)

tests = [
    {
        "name": "Test 1: Cinderella → Space Opera",
        "source_file": "examples/cinderella.txt",
        "title": "Cinderella",
        "genre": "space_opera",
        "output_file": "output/test1_cinderella_space.txt"
    },
    {
        "name": "Test 2: Tortoise & Hare → Cyberpunk",
        "source_file": "examples/tortoise_hare.txt",
        "title": "The Tortoise and the Hare",
        "genre": "cyberpunk",
        "output_file": "output/test2_tortoise_cyber.txt"
    },
    {
        "name": "Test 3: Icarus → Post-Apocalyptic",
        "source_file": "examples/icarus.txt",
        "title": "The Flight of Icarus",
        "genre": "post_apocalyptic",
        "output_file": "output/test3_icarus_postapoc.txt"
    }
]

results = []

for i, test in enumerate(tests, 1):
    print(f"\n{'='*70}")
    print(f"{test['name']}")
    print(f"{'='*70}\n")
    
    try:
        # Read source
        with open(test['source_file'], 'r', encoding='utf-8') as f:
            source_text = f.read()
        
        # Transform
        transformer = NarrativeTransformer()
        story, metadata = transformer.transform(
            source_text=source_text,
            source_title=test['title'],
            target_genre=test['genre'],
            num_beats=3  # Quick test with 3 beats
        )
        
        # Save output
        with open(test['output_file'], 'w', encoding='utf-8') as f:
            f.write(story)
        
        # Collect results
        result = {
            "test": test['name'],
            "status": "✅ SUCCESS",
            "word_count": metadata.get('word_count', 0),
            "avg_tension": metadata.get('avg_tension', 0),
            "characters": len(metadata.get('character_states', {})),
            "output": test['output_file']
        }
        results.append(result)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Words: {result['word_count']}")
        print(f"   Avg Tension: {result['avg_tension']:.2f}")
        print(f"   Characters: {result['characters']}")
        print(f"   Output: {result['output']}")
        
    except Exception as e:
        result = {
            "test": test['name'],
            "status": f"❌ FAILED: {str(e)}",
            "word_count": 0,
            "avg_tension": 0,
            "characters": 0,
            "output": None
        }
        results.append(result)
        print(f"\n❌ FAILED: {e}")

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}\n")

for result in results:
    print(f"{result['test']}")
    print(f"  Status: {result['status']}")
    if result['word_count'] > 0:
        print(f"  Words: {result['word_count']}")
        print(f"  Tension: {result['avg_tension']:.2f}")
        print(f"  Characters: {result['characters']}")
    print()

# Overall stats
successes = sum(1 for r in results if "✅" in r['status'])
print(f"Overall: {successes}/3 tests passed")
print(f"\nAll outputs saved to 'output/' directory")
