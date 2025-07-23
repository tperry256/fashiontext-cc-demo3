#!/usr/bin/env python3
"""
Step 1 preprocessor for tsm.txt - parses structure and matches table of contents to actual sections/chapters
"""

import json
import re
from typing import Dict, List, Any

def parse_tsm_step1(input_file: str = "tsm.txt", output_file: str = "fate_parse_step1.json") -> Dict[str, Any]:
    """Parse tsm.txt and create structured JSON matching table of contents to content"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Extract table of contents sections with their various formats
    toc_sections = [
        ("Open Ontology", ["__Open Ontology__"]),
        ("Licensing Info", ["__Licensing Info__"]), 
        ("About This Work", ["__About this work__"]),  # Note lowercase 'this work'
        ("CH1: Preface for Susie", ["__CH1. Preface for Susie__"]),  # Note period instead of colon
        ("CH2: The Zyla Preface", ["__CH2. The Zyla Preface__"]), 
        ("CH3: This Guy's Guys", ["__CH3. This Guy's Guys__"]),
        ("CH4: Zyla Speakeasy", ["__CH4: Zyla Speakeasy__"]),
        ("CH5: Trey's Memoir", ["__CH5: Trey's Memoir__"]),
        ("CH6: Todd's About", ["__CH6: Todd's About__"]),
        ("CH7: Style Guide", ["__CH7: Style Guide__"]),
        ("Useful Glossary", ["__Useful Glossary__"]),
        ("Copyright Info", ["__Copyright Info__"])
    ]
    
    result = {
        "metadata": {
            "title": "TheSusie FashionMemo",
            "author": "Todd Perry",
            "version": "V:3.1",
            "last_updated": "Jul. 23, 2025",
            "source_file": input_file,
            "parsing_step": "step1"
        },
        "table_of_contents": [section[0] for section in toc_sections],
        "sections": {}
    }
    
    # Find section boundaries and extract content
    current_section = None
    current_content = []
    
    for i, line in enumerate(lines):
        line_clean = line.strip()
        
        # Skip line numbers and arrows from the original format
        if '→' in line:
            line_clean = line.split('→', 1)[1] if '→' in line else line_clean
        
        # Check if this line starts a new section
        section_found = None
        for section_name, section_patterns in toc_sections:
            # Check if line matches any of the patterns for this section
            for pattern in section_patterns:
                if line_clean == pattern:
                    section_found = section_name
                    break
            if section_found:
                break
        
        if section_found:
            # Save previous section if exists
            if current_section and current_content:
                content_text = '\n'.join(current_content).strip()
                result["sections"][current_section] = {
                    "title": current_section,
                    "content": content_text,
                    "line_start": result["sections"].get(current_section, {}).get("line_start", 0),
                    "line_end": i - 1,
                    "word_count": len(content_text.split()) if content_text else 0
                }
            
            # Start new section
            current_section = section_found
            current_content = []
            if current_section not in result["sections"]:
                result["sections"][current_section] = {"line_start": i}
        
        elif current_section and line_clean:
            # Add content to current section (skip empty lines at start)
            if current_content or line_clean:
                current_content.append(line_clean)
    
    # Handle last section
    if current_section and current_content:
        content_text = '\n'.join(current_content).strip()
        result["sections"][current_section] = {
            "title": current_section,
            "content": content_text,
            "line_start": result["sections"].get(current_section, {}).get("line_start", 0),
            "line_end": len(lines) - 1,
            "word_count": len(content_text.split()) if content_text else 0
        }
    
    # Add statistics
    total_words = sum(section.get("word_count", 0) for section in result["sections"].values())
    expected_sections = [s[0] for s in toc_sections]
    result["statistics"] = {
        "total_sections": len(result["sections"]),
        "total_lines": len(lines),
        "total_words": total_words,
        "sections_found": list(result["sections"].keys()),
        "sections_missing": [s for s in expected_sections if s not in result["sections"]]
    }
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result

if __name__ == "__main__":
    result = parse_tsm_step1()
    print(f"Parsed {result['statistics']['total_sections']} sections")
    print(f"Total words: {result['statistics']['total_words']}")
    print(f"Sections found: {result['statistics']['sections_found']}")
    if result['statistics']['sections_missing']:
        print(f"Sections missing: {result['statistics']['sections_missing']}")