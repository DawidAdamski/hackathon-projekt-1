"""
Test script to compare generated synthetic data with original and anonymized files.

Compares:
- orig.txt (with tokens like [name], [city])
- anonymized.txt (with real anonymized data)
- anonymized_synthetic.txt (our generated synthetic data)
"""

from pathlib import Path
from typing import List, Dict, Tuple
import re
from collections import Counter


def extract_tokens(text: str) -> List[str]:
    """
    Extract all tokens from text (e.g., [name], [city]).
    
    Args:
        text: Input text
        
    Returns:
        List of tokens found
    """
    pattern = r'\[([^\]]+)\]'
    return re.findall(pattern, text)


def extract_entities(text: str) -> List[Tuple[str, int, int]]:
    """
    Extract entities that might be PII (names, cities, phones, etc.).
    This is a simple heuristic - in production you'd use NER.
    
    Args:
        text: Input text
        
    Returns:
        List of (entity_text, start_pos, end_pos) tuples
    """
    entities = []
    
    # Pattern for phone numbers
    phone_pattern = r'(\+?\d{2,3}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3})'
    for match in re.finditer(phone_pattern, text):
        entities.append((match.group(1), match.start(), match.end()))
    
    # Pattern for emails
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    for match in re.finditer(email_pattern, text):
        entities.append((match.group(1), match.start(), match.end()))
    
    # Pattern for PESEL (11 digits)
    pesel_pattern = r'\b(\d{11})\b'
    for match in re.finditer(pesel_pattern, text):
        entities.append((match.group(1), match.start(), match.end()))
    
    return entities


def compare_files(
    orig_file: Path,
    anonymized_file: Path,
    synthetic_file: Path
) -> Dict:
    """
    Compare three files and generate statistics.
    
    Args:
        orig_file: Path to orig.txt
        anonymized_file: Path to anonymized.txt
        synthetic_file: Path to anonymized_synthetic.txt
        
    Returns:
        Dictionary with comparison statistics
    """
    results = {
        "total_lines": 0,
        "lines_with_tokens": 0,
        "token_types": Counter(),
        "entities_found": {
            "anonymized": 0,
            "synthetic": 0,
        },
        "differences": [],
        "sample_comparisons": [],
    }
    
    # Read all files
    with open(orig_file, "r", encoding="utf-8") as f:
        orig_lines = f.readlines()
    
    with open(anonymized_file, "r", encoding="utf-8") as f:
        anonymized_lines = f.readlines()
    
    with open(synthetic_file, "r", encoding="utf-8") as f:
        synthetic_lines = f.readlines()
    
    results["total_lines"] = len(orig_lines)
    
    # Compare line by line
    for i, (orig_line, anon_line, synth_line) in enumerate(
        zip(orig_lines, anonymized_lines, synthetic_lines), 1
    ):
        # Count tokens in original
        tokens = extract_tokens(orig_line)
        if tokens:
            results["lines_with_tokens"] += 1
            results["token_types"].update(tokens)
        
        # Count entities in anonymized and synthetic
        anon_entities = extract_entities(anon_line)
        synth_entities = extract_entities(synth_line)
        
        results["entities_found"]["anonymized"] += len(anon_entities)
        results["entities_found"]["synthetic"] += len(synth_entities)
        
        # Find differences (if tokens were replaced)
        if tokens and (anon_line != orig_line or synth_line != orig_line):
            # Check if tokens were actually replaced
            orig_has_tokens = bool(extract_tokens(orig_line))
            anon_has_tokens = bool(extract_tokens(anon_line))
            synth_has_tokens = bool(extract_tokens(synth_line))
            
            if orig_has_tokens and not anon_has_tokens and not synth_has_tokens:
                # Tokens were replaced in both
                if len(results["sample_comparisons"]) < 10:
                    results["sample_comparisons"].append({
                        "line_num": i,
                        "original": orig_line.strip()[:100],
                        "anonymized": anon_line.strip()[:100],
                        "synthetic": synth_line.strip()[:100],
                    })
    
    return results


def print_comparison_report(results: Dict):
    """
    Print a formatted comparison report.
    
    Args:
        results: Results dictionary from compare_files
    """
    print("=" * 80)
    print("COMPARISON REPORT")
    print("=" * 80)
    
    print(f"\n📊 Statistics:")
    print(f"  Total lines: {results['total_lines']}")
    print(f"  Lines with tokens: {results['lines_with_tokens']}")
    
    print(f"\n🏷️  Token Types Found:")
    for token, count in results['token_types'].most_common():
        print(f"  [{token}]: {count} occurrences")
    
    print(f"\n🔍 Entities Detected:")
    print(f"  In anonymized.txt: {results['entities_found']['anonymized']}")
    print(f"  In synthetic.txt: {results['entities_found']['synthetic']}")
    
    print(f"\n📝 Sample Comparisons (first 10):")
    for sample in results['sample_comparisons']:
        print(f"\n  Line {sample['line_num']}:")
        print(f"    Original:    {sample['original']}...")
        print(f"    Anonymized:  {sample['anonymized']}...")
        print(f"    Synthetic:   {sample['synthetic']}...")
    
    print("\n" + "=" * 80)


def validate_synthetic_file(synthetic_file: Path) -> Dict:
    """
    Validate that synthetic file doesn't contain original tokens.
    
    Args:
        synthetic_file: Path to synthetic file
        
    Returns:
        Dictionary with validation results
    """
    validation = {
        "total_lines": 0,
        "lines_with_remaining_tokens": 0,
        "remaining_tokens": [],
        "valid": True,
    }
    
    with open(synthetic_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    validation["total_lines"] = len(lines)
    
    for i, line in enumerate(lines, 1):
        tokens = extract_tokens(line)
        if tokens:
            validation["lines_with_remaining_tokens"] += 1
            validation["remaining_tokens"].extend([
                (i, token) for token in tokens
            ])
            validation["valid"] = False
    
    return validation


def print_validation_report(validation: Dict):
    """
    Print validation report.
    
    Args:
        validation: Validation results dictionary
    """
    print("=" * 80)
    print("VALIDATION REPORT")
    print("=" * 80)
    
    if validation["valid"]:
        print("\n✅ SUCCESS: No remaining tokens found in synthetic file!")
    else:
        print(f"\n⚠️  WARNING: Found {validation['lines_with_remaining_tokens']} lines with remaining tokens")
        print(f"\nRemaining tokens:")
        for line_num, token in validation["remaining_tokens"][:20]:  # Show first 20
            print(f"  Line {line_num}: [{token}]")
        
        if len(validation["remaining_tokens"]) > 20:
            print(f"  ... and {len(validation['remaining_tokens']) - 20} more")
    
    print("=" * 80)


def main():
    """Main function."""
    # File paths
    base_dir = Path(__file__).parent.parent.parent
    orig_file = base_dir / "nask_train" / "orig.txt"
    anonymized_file = base_dir / "nask_train" / "anonymized.txt"
    synthetic_file = base_dir / "nask_train" / "anonymized_synthetic.txt"
    
    print("🔍 File Comparison Test")
    print(f"Base directory: {base_dir}")
    print(f"Original: {orig_file}")
    print(f"Anonymized: {anonymized_file}")
    print(f"Synthetic: {synthetic_file}\n")
    
    # Check if files exist
    if not orig_file.exists():
        print(f"✗ Error: {orig_file} not found")
        return
    
    if not anonymized_file.exists():
        print(f"⚠️  Warning: {anonymized_file} not found (comparison will be limited)")
        anonymized_file = None
    
    if not synthetic_file.exists():
        print(f"✗ Error: {synthetic_file} not found")
        print("   Run 'python process_file.py' first to generate it")
        return
    
    # Validate synthetic file
    print("\n" + "=" * 80)
    print("VALIDATING SYNTHETIC FILE")
    print("=" * 80)
    validation = validate_synthetic_file(synthetic_file)
    print_validation_report(validation)
    
    # Compare files if anonymized exists
    if anonymized_file and anonymized_file.exists():
        print("\n" + "=" * 80)
        print("COMPARING FILES")
        print("=" * 80)
        results = compare_files(orig_file, anonymized_file, synthetic_file)
        print_comparison_report(results)
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    main()

