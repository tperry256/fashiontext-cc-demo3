#!/usr/bin/env python3
"""
Step 2 preprocessor for tsm.txt - reads step1 JSON and breaks content into paragraphs with IDs and line numbers
"""

import json
from typing import Dict, List, Any

def parse_tsm_step2(input_file: str = "fate_parse_step1.json", output_file: str = "fate_parse_step2.json") -> Dict[str, Any]:
    """Read step1 JSON and split each section's content into paragraphs with word counts"""
    
    # Read the step1 JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        step1_data = json.load(f)
    
    # Create step2 structure with root node
    result = {
        "metadata": {
            "title": step1_data["metadata"]["title"],
            "author": step1_data["metadata"]["author"],
            "version": step1_data["metadata"]["version"],
            "last_updated": step1_data["metadata"]["last_updated"],
            "source_file": step1_data["metadata"]["source_file"],
            "parsing_step": "step2",
            "previous_step": input_file,
            "id": "root",
            "parent_id": None
        },
        "table_of_contents": step1_data["table_of_contents"],
        "sections": {}
    }
    
    # Initialize counters and ID tracker
    total_paragraphs = 0
    total_words = 0
    next_id = 1
    
    for section_name, section_data in step1_data["sections"].items():
        content = section_data.get("content", "")
        section_id = f"section_{next_id}"
        next_id += 1
        
        # Split content into paragraphs by line breaks, ignoring empty ones
        raw_paragraphs = content.split('\n')
        paragraphs = []
        
        # Track line position within the section content
        current_line_offset = 0
        section_start_line = section_data.get("line_start", 0)
        
        for para_index, para in enumerate(raw_paragraphs):
            para_clean = para.strip()
            if para_clean:  # Ignore empty paragraphs
                word_count = len(para_clean.split())
                para_id = f"para_{next_id}"
                next_id += 1
                
                # Calculate approximate line number for this paragraph
                # Note: This is an approximation since we're working from processed content
                paragraph_line = section_start_line + current_line_offset + para_index
                
                paragraphs.append({
                    "id": para_id,
                    "parent_id": section_id,
                    "text": para_clean,
                    "word_count": word_count,
                    "line_number": paragraph_line,
                    "paragraph_index": len(paragraphs)  # 0-based index within section
                })
                total_words += word_count
        
        total_paragraphs += len(paragraphs)
        
        # Create section entry with paragraphs
        result["sections"][section_name] = {
            "id": section_id,
            "parent_id": "root",
            "title": section_data.get("title", section_name),
            "line_start": section_data.get("line_start"),
            "line_end": section_data.get("line_end"),
            "total_word_count": section_data.get("word_count", 0),
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs
        }
    
    # Add statistics
    result["statistics"] = {
        "id": f"stats_{next_id}",
        "parent_id": "root",
        "total_sections": len(result["sections"]),
        "total_paragraphs": total_paragraphs,
        "total_words": total_words,
        "total_nodes": next_id,  # Total number of IDs assigned
        "sections_processed": list(result["sections"].keys()),
        "average_paragraphs_per_section": round(total_paragraphs / len(result["sections"]), 2) if result["sections"] else 0,
        "average_words_per_paragraph": round(total_words / total_paragraphs, 2) if total_paragraphs > 0 else 0
    }
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result

if __name__ == "__main__":
    result = parse_tsm_step2()
    print(f"Processed {result['statistics']['total_sections']} sections")
    print(f"Total paragraphs: {result['statistics']['total_paragraphs']}")
    print(f"Total words: {result['statistics']['total_words']}")
    print(f"Total nodes: {result['statistics']['total_nodes']}")
    print(f"Average paragraphs per section: {result['statistics']['average_paragraphs_per_section']}")
    print(f"Average words per paragraph: {result['statistics']['average_words_per_paragraph']}")
    
    # Show sample paragraph breakdown for first section
    first_section = list(result['sections'].keys())[0]
    section_data = result['sections'][first_section]
    print(f"\nSample breakdown for '{first_section}':")
    print(f"  Section ID: {section_data['id']}")
    print(f"  Parent ID: {section_data['parent_id']}")
    print(f"  {section_data['paragraph_count']} paragraphs")
    if section_data['paragraphs']:
        first_para = section_data['paragraphs'][0]
        print(f"  First paragraph ID: {first_para['id']}")
        print(f"  First paragraph parent: {first_para['parent_id']}")
        print(f"  First paragraph line: {first_para['line_number']}")
        print(f"  First paragraph words: {first_para['word_count']}")
        print(f"  Text preview: {first_para['text'][:100]}...")