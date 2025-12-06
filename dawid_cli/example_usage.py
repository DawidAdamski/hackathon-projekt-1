"""
Example usage of the synthesis module for generating synthetic data.

This script demonstrates how to use the MorphologicalGenerator
to replace PII tokens with synthetic Polish data.
"""

import re
from pathlib import Path
from src.synthesis.morph_generator import MorphologicalGenerator


def anonymize_text_with_synthesis(text: str, generator: MorphologicalGenerator) -> str:
    """
    Replace PII tokens in text with synthetic data.
    
    Args:
        text: Input text with tokens like [name], [city], etc.
        generator: MorphologicalGenerator instance
        
    Returns:
        Text with tokens replaced by synthetic data
    """
    # Pattern to match tokens like [name], [surname], [city], etc.
    token_pattern = r'\[([^\]]+)\]'
    
    def replace_token(match):
        token = match.group(1).lower().strip()
        original = match.group(0)
        
        # Map common variations (handle both [name] and [name] [surname] formats)
        token_mapping = {
            "name": "{name}",
            "surname": "{surname}",
            "city": "{city}",
            "address": "{address}",
            "phone": "{phone}",
            "email": "{email}",
            "pesel": "{pesel}",
            "document-number": "{document-number}",
            "age": "{age}",
            "sex": "{sex}",
            "company": "{company}",
            "date": "{date}",
            "data": "{date}",
            "bank-account": "{bank-account}",
        }
        
        entity_type = token_mapping.get(token, f"{{{token}}}")
        synthetic = generator.generate(original, entity_type)
        return synthetic
    
    anonymized = re.sub(token_pattern, replace_token, text)
    return anonymized


def main():
    """Main function to demonstrate usage."""
    # Initialize generator
    print("Initializing MorphologicalGenerator...")
    try:
        generator = MorphologicalGenerator()
        print("✓ Generator initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing generator: {e}")
        print("Make sure you have installed spacy model: python -m spacy download pl_core_news_lg")
        return
    
    # Example 1: Simple text with tokens
    print("\n" + "="*60)
    print("Example 1: Simple text replacement")
    print("="*60)
    
    example_text = "Nazywam się [name] [surname], mój PESEL to [pesel]. Mieszkam w [city] przy ulicy [address]."
    print(f"Original: {example_text}")
    
    anonymized = anonymize_text_with_synthesis(example_text, generator)
    print(f"Anonymized: {anonymized}")
    
    # Example 2: Process file
    print("\n" + "="*60)
    print("Example 2: Processing orig.txt file")
    print("="*60)
    
    orig_file = Path(__file__).parent.parent / "nask_train" / "orig.txt"
    if orig_file.exists():
        print(f"Reading from: {orig_file}")
        
        with open(orig_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Process first 5 lines as example
        print(f"\nProcessing first 5 lines...")
        for i, line in enumerate(lines[:5], 1):
            if line.strip():
                print(f"\nLine {i}:")
                print(f"  Original: {line.strip()[:100]}...")
                anonymized_line = anonymize_text_with_synthesis(line, generator)
                print(f"  Anonymized: {anonymized_line.strip()[:100]}...")
    else:
        print(f"File not found: {orig_file}")
        print("Skipping file processing example")
    
    # Example 3: Test different entity types
    print("\n" + "="*60)
    print("Example 3: Testing different entity types")
    print("="*60)
    
    test_cases = [
        ("[name]", "{name}"),
        ("[surname]", "{surname}"),
        ("[city]", "{city}"),
        ("[phone]", "{phone}"),
        ("[email]", "{email}"),
        ("[pesel]", "{pesel}"),
    ]
    
    for original, entity_type in test_cases:
        synthetic = generator.generate(original, entity_type)
        print(f"{original:15} -> {synthetic}")


if __name__ == "__main__":
    main()

