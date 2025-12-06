"""
Simple unit tests for MorphologicalGenerator.
"""

from src.synthesis.morph_generator import MorphologicalGenerator


def test_basic_generation():
    """Test basic data generation."""
    generator = MorphologicalGenerator()
    
    # Test name generation
    name = generator.generate("[name]", "{name}")
    assert name and len(name) > 0, "Name should be generated"
    print(f"✓ Generated name: {name}")
    
    # Test city generation
    city = generator.generate("[city]", "{city}")
    assert city and len(city) > 0, "City should be generated"
    print(f"✓ Generated city: {city}")
    
    # Test phone generation
    phone = generator.generate("[phone]", "{phone}")
    assert phone and len(phone) > 0, "Phone should be generated"
    print(f"✓ Generated phone: {phone}")
    
    # Test email generation
    email = generator.generate("[email]", "{email}")
    assert "@" in email, "Email should contain @"
    print(f"✓ Generated email: {email}")


def test_token_replacement():
    """Test token replacement in text."""
    generator = MorphologicalGenerator()
    
    text = "Nazywam się [name] [surname], mój PESEL to [pesel]."
    
    # Simple replacement (would need regex in real usage)
    import re
    token_pattern = r'\[([^\]]+)\]'
    
    def replace_token(match):
        token = match.group(1).lower().strip()
        token_mapping = {
            "name": "{name}",
            "surname": "{surname}",
            "pesel": "{pesel}",
        }
        entity_type = token_mapping.get(token, f"{{{token}}}")
        return generator.generate(match.group(0), entity_type)
    
    result = re.sub(token_pattern, replace_token, text)
    
    assert "[name]" not in result, "Tokens should be replaced"
    assert "[surname]" not in result, "Tokens should be replaced"
    assert "[pesel]" not in result, "Tokens should be replaced"
    
    print(f"✓ Original: {text}")
    print(f"✓ Result:   {result}")


if __name__ == "__main__":
    print("Running simple tests...\n")
    test_basic_generation()
    print()
    test_token_replacement()
    print("\n✅ All tests passed!")

