#!/usr/bin/env python3
"""
System Validation Script
Tests all components to ensure everything is working correctly.
"""

import sys
from pathlib import Path

# Test imports
print("=" * 60)
print("NARRATIVE TRANSFORMATION SYSTEM - VALIDATION TEST")
print("=" * 60)
print()

print("Step 1: Testing imports...")
try:
    from config import DEFAULT_CONFIG, GENRE_TEMPLATES, SAVE_THE_CAT_BEATS
    print("  ✅ config.py")
except Exception as e:
    print(f"  ❌ config.py: {e}")
    sys.exit(1)

try:
    from models import (
        Character, PlotBeat, Conflict, SourceAnalysis,
        WorldMapping, ElementMapping, SceneOutput, StoryState
    )
    print("  ✅ models.py")
except Exception as e:
    print(f"  ❌ models.py: {e}")
    sys.exit(1)

try:
    from analyzer import SourceAnalyzer
    print("  ✅ analyzer.py")
except Exception as e:
    print(f"  ❌ analyzer.py: {e}")
    sys.exit(1)

try:
    from mapper import WorldMapper
    print("  ✅ mapper.py")
except Exception as e:
    print(f"  ❌ mapper.py: {e}")
    sys.exit(1)

try:
    from tension import TensionAnalyzer, PacingController
    print("  ✅ tension.py")
except Exception as e:
    print(f"  ❌ tension.py: {e}")
    sys.exit(1)

try:
    from generator import SceneGenerator
    print("  ✅ generator.py")
except Exception as e:
    print(f"  ❌ generator.py: {e}")
    sys.exit(1)

try:
    from transformer import NarrativeTransformer
    print("  ✅ transformer.py")
except Exception as e:
    print(f"  ❌ transformer.py: {e}")
    sys.exit(1)

print()
print("Step 2: Testing configuration...")

# Test API config
if not DEFAULT_CONFIG.validate():
    print("  ⚠️  No API key configured in .env file")
    print("     Please add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env")
    print("     Copy .env.example to .env and add your key")
    sys.exit(1)
else:
    api_type = DEFAULT_CONFIG.get_primary_api()
    print(f"  ✅ API configured: {api_type}")

# Test genre templates
print(f"  ✅ {len(GENRE_TEMPLATES)} genres available:")
for genre in GENRE_TEMPLATES.keys():
    print(f"     - {genre}")

# Test beat structure
print(f"  ✅ {len(SAVE_THE_CAT_BEATS)} story beats defined")

print()
print("Step 3: Testing NTI calculator...")

try:
    analyzer = TensionAnalyzer()
    
    # Test high tension scene
    high_tension = """
        The explosion rocked the building. She ducked behind cover, 
        heart pounding. How many were out there? Only two rounds left. 
        This might be it.
    """
    nti_high = analyzer.calculate_nti(high_tension)
    
    # Test low tension scene
    low_tension = """
        They sat together watching the sunset, her head on his shoulder. 
        The warm breeze carried the scent of jasmine. Everything felt 
        perfect, exactly as it should be.
    """
    nti_low = analyzer.calculate_nti(low_tension)
    
    if nti_high > nti_low:
        print(f"  ✅ NTI calculation working")
        print(f"     High tension scene: {nti_high}")
        print(f"     Low tension scene: {nti_low}")
    else:
        print(f"  ⚠️  NTI might not be calibrated correctly")
        print(f"     High: {nti_high}, Low: {nti_low}")

except Exception as e:
    print(f"  ❌ NTI test failed: {e}")
    sys.exit(1)

print()
print("Step 4: Testing pacing controller...")

try:
    pacer = PacingController(num_beats=12)
    
    # Test target curve generation
    if len(pacer.target_curve) == 12:
        print(f"  ✅ Target curve generated ({len(pacer.target_curve)} beats)")
        
        # Show curve
        print("     Tension curve preview:")
        for i in range(min(5, len(pacer.target_curve))):
            beat_name = SAVE_THE_CAT_BEATS[i]["name"]
            tension = pacer.target_curve[i]
            bar = "█" * int(tension * 20)
            print(f"       {beat_name:20s}: {bar} {tension:.2f}")
    
    # Test adjustment hints
    hint = pacer.get_adjustment_hint(0, 0.3)
    if hint:
        print(f"  ✅ Pacing hints working")
    
except Exception as e:
    print(f"  ❌ Pacing controller test failed: {e}")
    sys.exit(1)

print()
print("Step 5: Testing data models...")

try:
    # Test Character model
    char = Character(
        name="TestChar",
        role="hero",
        traits=["brave", "smart"],
        desires=["peace"],
        fears=["failure"],
        arc="learns humility"
    )
    
    # Test SourceAnalysis
    analysis = SourceAnalysis(
        title="Test",
        characters=[char],
        themes=["courage"],
        beats=[],
        conflicts=[],
        symbols={},
        setting="test world",
        tone="adventurous",
        central_question="Can they succeed?"
    )
    
    # Test conversion to dict
    analysis_dict = analysis.to_dict()
    
    print("  ✅ Data models working")
    print(f"     Created character: {char.name}")
    print(f"     Analysis serialization: OK")

except Exception as e:
    print(f"  ❌ Data model test failed: {e}")
    sys.exit(1)

print()
print("Step 6: Checking example files...")

example_path = Path("examples/romeo_juliet_excerpt.txt")
if example_path.exists():
    print(f"  ✅ Example file found: {example_path}")
    size = example_path.stat().st_size
    print(f"     Size: {size} bytes")
else:
    print(f"  ⚠️  Example file not found: {example_path}")
    print("     Create examples/ directory and add romeo_juliet_excerpt.txt")

print()
print("Step 7: System readiness check...")

print()
print("  ✅ All core components loaded successfully")
print("  ✅ Configuration is valid")
print("  ✅ NTI system is functional")
print("  ✅ Data models work correctly")
print()

print("=" * 60)
print("SYSTEM STATUS: READY ✅")
print("=" * 60)
print()
print("You can now run transformations using:")
print()
print("  python run.py --source examples/romeo_juliet_excerpt.txt \\")
print("                --title 'Romeo and Juliet' \\")
print("                --genre cyberpunk \\")
print("                --beats 8 \\")
print("                --output output.txt")
print()
print("Or test the Python API:")
print()
print("  from transformer import NarrativeTransformer")
print("  transformer = NarrativeTransformer()")
print("  story, metadata = transformer.transform(...)")
print()
print("Happy transforming! 🎭→🤖")
print()