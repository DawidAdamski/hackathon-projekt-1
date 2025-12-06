"""
Script to process orig.txt file and generate anonymized version with synthetic data.

Usage:
    python process_file.py [--input orig.txt] [--output anonymized_synthetic.txt]
"""

import argparse
import json
import re
import random
from pathlib import Path
from typing import Optional
from tqdm import tqdm
from src.synthesis.morph_generator import MorphologicalGenerator


def anonymize_text_with_synthesis(
    text: str, 
    generator: MorphologicalGenerator,
    use_llm: bool = True
) -> str:
    """
    Replace PII tokens in text with synthetic data.
    Maintains context between tokens for consistency (e.g., name -> gender).
    Uses LLM to analyze context when available.
    
    Args:
        text: Input text with tokens like [name], [city], etc.
        generator: MorphologicalGenerator instance
        use_llm: Whether to use LLM for generation (False = Faker only)
        
    Returns:
        Text with tokens replaced by synthetic data
    """
    # Pattern to match tokens like [name], [surname], [city], etc.
    token_pattern = r'\[([^\]]+)\]'
    
    # Context to store generated values for consistency
    context_values = {}
    
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
            "username": "{username}",
            "user-name": "{username}",
        }
        
        entity_type = token_mapping.get(token, f"{{{token}}}")
        
        # Use LLM to analyze context if available and use_llm is True
        if use_llm and generator.llm and token in ["name", "surname", "city", "address"]:
            # Get context around the token (100 chars before and after)
            match_start = match.start()
            context_start = max(0, match_start - 100)
            context_end = min(len(text), match.end() + 100)
            context_snippet = text[context_start:context_end]
            
            context_type = generator._analyze_context_with_llm(context_snippet, original)
            
            # Adjust entity type based on context
            if context_type == "adres" and token == "name":
                # If [name] is part of address, treat it as street name
                entity_type = "{address}"
            elif context_type == "miejscowosc" and token == "name":
                # If [name] is a place name
                entity_type = "{city}"
            elif context_type == "osoba" and token in ["name", "surname"]:
                # Keep as person name
                pass
        
        synthetic = generator.generate(
            original, 
            entity_type, 
            context=text, 
            prefer_llm=use_llm and generator.llm is not None,
            context_values=context_values
        )
        return synthetic
    
    # Step 1: Replace all tokens with Faker (fast, no LLM)
    anonymized = re.sub(token_pattern, replace_token, text)
    
    # Step 2: If LLM is enabled, do two-stage LLM processing
    if use_llm and generator.llm:
        # Process 1: Fill any remaining tokens (WARUNKOWY - tylko jeśli są tokeny [ ])
        filled_text = generator._fill_missing_tokens_with_llm(anonymized)
        if filled_text:
            anonymized = filled_text
        
        # Process 2: Correct morphology (ZAWSZE wykonywany)
        corrected_text = generator._correct_morphology_with_llm(anonymized)
        if corrected_text:
            anonymized = corrected_text
    
    return anonymized


def process_file(
    input_file: Path,
    output_file: Path,
    generator: MorphologicalGenerator,
    generate_jsonl: bool = True,
    sample_size: Optional[int] = None
) -> None:
    """
    Process input file line by line and generate anonymized output.
    
    Args:
        input_file: Path to input file (orig.txt)
        output_file: Path to output file (anonymized_synthetic.txt)
        generator: MorphologicalGenerator instance
        generate_jsonl: Whether to also generate JSONL file
        sample_size: If provided, randomly sample this many lines for processing
    """
    print(f"Processing {input_file}...")
    print(f"Output will be saved to {output_file}")
    
    # Generate JSONL filename
    jsonl_file = output_file.with_suffix('.jsonl') if generate_jsonl else None
    if jsonl_file:
        print(f"JSONL output will be saved to {jsonl_file}")
    
    # Read all lines
    print("\nReading file...")
    with open(input_file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        total_lines = len(all_lines)
    
    # Sample mode vs normal mode
    if sample_size:
        # SAMPLE MODE: Show comparison of 3 versions
        if sample_size < total_lines:
            print(f"Randomly sampling {sample_size} lines from {total_lines} total lines...")
            # Get random line indices
            sampled_indices = sorted(random.sample(range(total_lines), sample_size))
            # Create list of (line_num, line) tuples, preserving original line numbers
            lines_to_process = [(idx + 1, all_lines[idx]) for idx in sampled_indices]
            print(f"Selected lines: {', '.join(map(str, [idx+1 for idx in sampled_indices[:10]]))}{'...' if len(sampled_indices) > 10 else ''}\n")
        else:
            print(f"Sample size ({sample_size}) >= total lines ({total_lines}), processing all lines\n")
            lines_to_process = [(i+1, line) for i, line in enumerate(all_lines)]
        
        # Process and show comparison
        print("=" * 80)
        print("COMPARISON MODE - Showing 3 versions of each line:")
        print("=" * 80)
        
        for idx, (line_num, line) in enumerate(lines_to_process, 1):
            original_line = line.rstrip('\n\r')
            
            if not line.strip():
                print(f"\n[Line {line_num}] (empty line)")
                continue
            
            print(f"\n[Line {line_num}]")
            print(f"1. ORIGINAL:     {original_line}")
            
            try:
                # Version 2: Faker only (no LLM)
                faker_version = anonymize_text_with_synthesis(line, generator, use_llm=False)
                print(f"2. AFTER FAKER: {faker_version.rstrip()}")
                
                # Version 3: With LLM verification (if available)
                if generator.llm:
                    llm_version = anonymize_text_with_synthesis(line, generator, use_llm=True)
                    print(f"3. AFTER LLM:   {llm_version.rstrip()}")
                else:
                    print(f"3. AFTER LLM:   (LLM not available, same as Faker)")
            except Exception as e:
                print(f"   ERROR: {e}")
            
            if idx < len(lines_to_process):
                print("-" * 80)
        
        print("\n" + "=" * 80)
        print("✓ Sample comparison complete!")
        print(f"  Processed {len(lines_to_process)} lines for comparison")
        print("  (No files created in sample mode)")
        
    else:
        # NORMAL MODE: Process all lines and save to files
        lines_to_process = [(i+1, line) for i, line in enumerate(all_lines)]
        print(f"Found {total_lines} lines to process\n")
        
        processed_lines = 0
        error_count = 0
        
        # Create progress bar
        pbar = tqdm(
            total=len(lines_to_process),
            desc="Processing",
            unit="lines",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
        
        # Process lines sequentially
        results = {}
        
        for line_num, line in lines_to_process:
            original_line = line.rstrip('\n\r')
            
            if line.strip():  # Skip empty lines
                try:
                    anonymized_line = anonymize_text_with_synthesis(line, generator, use_llm=True)
                    anonymized_clean = anonymized_line.rstrip('\n\r')
                    results[line_num] = (original_line, anonymized_line, anonymized_clean, None)
                    processed_lines += 1
                except Exception as e:
                    error_count += 1
                    results[line_num] = (original_line, line, original_line, str(e))
                    pbar.set_postfix({"errors": error_count})
            else:
                # Empty line
                results[line_num] = ("", line, "", None)
            
            pbar.update(1)
        
        pbar.close()
        
        # Write results in order
        print("\nWriting results to files...")
        with open(output_file, "w", encoding="utf-8") as outfile, \
             (open(jsonl_file, "w", encoding="utf-8") if jsonl_file else None) as jsonl_outfile:
            
            for line_num in sorted(results.keys()):
                original_line, anonymized_line, anonymized_clean, error = results[line_num]
                
                # Write to text file
                outfile.write(anonymized_line)
                
                # Write to JSONL file
                if jsonl_outfile:
                    json_obj = {
                        "line_number": line_num,
                        "original": original_line,
                        "synthetic": anonymized_clean
                    }
                    if error:
                        json_obj["error"] = error
                    jsonl_outfile.write(json.dumps(json_obj, ensure_ascii=False) + '\n')
        
        print(f"\n✓ Processing complete!")
        print(f"  Total lines in file: {total_lines}")
        print(f"  Processed lines: {len(lines_to_process)}")
        print(f"  Successfully processed: {processed_lines}")
        if error_count > 0:
            print(f"  Errors: {error_count}")
        print(f"  Text output saved to: {output_file}")
        if jsonl_file:
            print(f"  JSONL output saved to: {jsonl_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Process orig.txt and generate anonymized version with synthetic data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_file.py
  python process_file.py ../nask_train/orig.txt
  python process_file.py --input ../nask_train/orig.txt --output output.txt
  python process_file.py ../nask_train/orig.txt output.txt
        """
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=str,
        default=None,
        help="Input file path (positional argument)"
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        type=str,
        default=None,
        help="Output file path (positional argument, optional)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input file path (alternative to positional argument)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (alternative to positional argument)"
    )
    parser.add_argument(
        "--no-jsonl",
        action="store_true",
        help="Don't generate JSONL file (only text output)"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        metavar="N",
        help="Randomly sample N lines for processing (useful for testing)"
    )
    
    args = parser.parse_args()
    
    # Determine input file (positional takes precedence, then --input, then default)
    if args.input_file:
        input_file = Path(args.input_file)
    elif args.input:
        input_file = Path(args.input)
    else:
        input_file = Path("nask_train/orig.txt")
    
    # Determine output file (positional takes precedence, then --output, then default)
    if args.output_file:
        output_file = Path(args.output_file)
    elif args.output:
        output_file = Path(args.output)
    else:
        # Auto-generate output filename from input
        output_file = input_file.parent / f"{input_file.stem}_synthetic{input_file.suffix}"
    
    # Check if input file exists
    if not input_file.exists():
        print(f"✗ Error: Input file not found: {input_file}")
        return
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load config to get LLM mode
    llm_mode = None
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                llm_mode = config.get("llm", {}).get("mode")
        except Exception:
            pass
    
    # Initialize generator
    print("Initializing MorphologicalGenerator...")
    try:
        # Try with morphology first, fallback to simple faking if Spacy not available
        try:
            if llm_mode:
                generator = MorphologicalGenerator(use_morphology=True, llm_mode=llm_mode)
            else:
                generator = MorphologicalGenerator(use_morphology=True)
            print("✓ Generator initialized with morphology support\n")
        except Exception as e:
            print(f"⚠️  Spacy not available ({e}), using simple faking (no morphology)\n")
            if llm_mode:
                generator = MorphologicalGenerator(use_morphology=False, llm_mode=llm_mode)
            else:
                generator = MorphologicalGenerator(use_morphology=False)
            print("✓ Generator initialized (simple mode)\n")
    except Exception as e:
        print(f"✗ Error initializing generator: {e}")
        print("\nMake sure you have:")
        print("  1. Installed dependencies: uv pip install -r requirements.txt")
        print("  2. (Optional) For morphology: python -m spacy download pl_core_news_lg")
        print("  3. (Optional) For local LLM: ollama serve (and model pulled)")
        return
    
    # Process file
    try:
        process_file(
            input_file, 
            output_file, 
            generator, 
            generate_jsonl=not args.no_jsonl,
            sample_size=args.sample
        )
    except Exception as e:
        print(f"\n✗ Error during processing: {e}")
        raise


if __name__ == "__main__":
    main()

