#!/usr/bin/env python3
"""
Narrative Transformation System - Command Line Interface
Entry point for running transformations from the terminal.
"""

import argparse
import os
import json
import sys
from pathlib import Path

from transformer import NarrativeTransformer
from config import GENRE_TEMPLATES


def main():
    """Main CLI function."""
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Transform classic narratives into new genres",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transform Romeo & Juliet to cyberpunk
  python run.py --source examples/romeo_juliet.txt --title "Romeo and Juliet" --genre cyberpunk
  
  # Use fewer beats for faster generation
  python run.py --source input.txt --title "My Story" --genre space_opera --beats 8
  
Available genres:
  """ + ", ".join(GENRE_TEMPLATES.keys())
    )
    
    parser.add_argument(
        "--source",
        required=True,
        help="Path to source text file"
    )
    
    parser.add_argument(
        "--title",
        required=True,
        help="Title of the source work"
    )
    
    parser.add_argument(
        "--genre",
        required=True,
        choices=list(GENRE_TEMPLATES.keys()),
        help="Target genre for transformation"
    )
    
    parser.add_argument(
        "--beats",
        type=int,
        default=12,
        help="Number of story beats to generate (default: 12)"
    )
    
    parser.add_argument(
        "--output",
        default="output.txt",
        help="Output file path (default: output.txt)"
    )
    
    parser.add_argument(
        "--metadata",
        default=None,
        help="Optional: Save metadata as JSON to this file"
    )
    
    parser.add_argument(
        "--model",
        default=None,
        help="Optional: Specify model (e.g., gpt-4, claude-sonnet-4-20250514)"
    )
    
    args = parser.parse_args()
    
    # Validate source file exists
    if not os.path.exists(args.source):
        print(f"❌ Error: Source file '{args.source}' not found")
        sys.exit(1)
    
    # Load source text
    try:
        with open(args.source, 'r', encoding='utf-8') as f:
            source_text = f.read()
    except Exception as e:
        print(f"❌ Error reading source file: {e}")
        sys.exit(1)
    
    if not source_text.strip():
        print("❌ Error: Source file is empty")
        sys.exit(1)
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run transformation
    try:
        print("\n🚀 Starting narrative transformation...\n")
        
        transformer = NarrativeTransformer(model=args.model)
        
        story, metadata = transformer.transform(
            source_text=source_text,
            source_title=args.title,
            target_genre=args.genre,
            num_beats=args.beats
        )
        
        # Save output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(story)
        
        print(f"✅ Story saved to: {args.output}")
        print(f"   Word count: {metadata['word_count']}")
        print(f"   Average tension: {metadata['avg_tension']:.2f}")
        
        # Save metadata if requested
        if args.metadata:
            metadata_path = Path(args.metadata)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(args.metadata, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"📊 Metadata saved to: {args.metadata}")
        
        # Print character fates
        print("\n📖 Character Fates:")
        for char, fate in metadata['character_fates'].items():
            print(f"   {char}: {fate}")
        
        # Print tension curve
        print("\n📈 Tension Curve:")
        tension_curve = metadata['tension_curve']
        max_tension = max(tension_curve)
        for i, tension in enumerate(tension_curve):
            bar_length = int((tension / max_tension) * 30) if max_tension > 0 else 0
            bar = "█" * bar_length
            print(f"   Beat {i+1:2d}: {bar} {tension:.2f}")
        
        print("\n🎉 Transformation complete!\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Transformation interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error during transformation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()