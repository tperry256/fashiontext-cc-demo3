#!/usr/bin/env python3
"""
Step 3 preprocessor for tsm.txt - creates word index and node path index from step2 JSON
"""

import json
import re
from collections import defaultdict
from typing import Dict, List, Any, Set

# Common English stop words
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 
    'will', 'with', 'the', 'this', 'but', 'they', 'have', 'had', 'what', 'said', 
    'each', 'which', 'she', 'do', 'how', 'their', 'if', 'up', 'out', 'many', 
    'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 
    'into', 'him', 'time', 'two', 'more', 'go', 'no', 'way', 'could', 'my', 
    'than', 'first', 'been', 'call', 'who', 'oil', 'sit', 'now', 'find', 
    'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part', 'over', 
    'new', 'sound', 'take', 'only', 'little', 'work', 'know', 'place', 
    'year', 'live', 'me', 'back', 'give', 'most', 'very', 'after', 'thing', 
    'our', 'just', 'name', 'good', 'sentence', 'man', 'think', 'say', 'great', 
    'where', 'help', 'through', 'much', 'before', 'line', 'right', 'too', 
    'mean', 'old', 'any', 'same', 'tell', 'boy', 'follow', 'came', 'want', 
    'show', 'also', 'around', 'form', 'three', 'small', 'set', 'put', 'end', 
    'why', 'again', 'turn', 'here', 'off', 'went', 'see', 'own', 'under', 
    'last', 'might', 'us', 'left', 'big', 'try', 'kind', 'hand', 'picture', 
    'move', 'play', 'spell', 'air', 'away', 'animal', 'house', 'point', 
    'page', 'letter', 'mother', 'answer', 'found', 'study', 'still', 'learn', 
    'should', 'america', 'world'
}

def clean_word(word: str) -> str:
    """Clean a word by removing punctuation and converting to lowercase"""
    # Remove punctuation and convert to lowercase
    cleaned = re.sub(r'[^\w]', '', word.lower())
    return cleaned

def extract_words(text: str) -> List[str]:
    """Extract meaningful words from text, excluding stop words"""
    words = text.split()
    meaningful_words = []
    
    for word in words:
        cleaned = clean_word(word)
        if cleaned and len(cleaned) > 2 and cleaned not in STOP_WORDS:
            meaningful_words.append(cleaned)
    
    return meaningful_words

def build_node_path_index(step2_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Build an index mapping node IDs to their path from root"""
    path_index = {}
    
    # Root node
    root_id = step2_data["metadata"]["id"]
    path_index[root_id] = [root_id]
    
    # Statistics node
    stats_id = step2_data["statistics"]["id"]
    path_index[stats_id] = [root_id, stats_id]
    
    # Process sections and their paragraphs
    for section_name, section_data in step2_data["sections"].items():
        section_id = section_data["id"]
        section_path = [root_id, section_id]
        path_index[section_id] = section_path
        
        # Process paragraphs within this section
        for paragraph in section_data["paragraphs"]:
            para_id = paragraph["id"]
            para_path = section_path + [para_id]
            path_index[para_id] = para_path
    
    return path_index

def build_paragraph_to_page_mapping(step4_file: str = "fate_parse_step4.json") -> Dict[str, str]:
    """Build mapping from paragraph node IDs to page IDs"""
    try:
        with open(step4_file, 'r', encoding='utf-8') as f:
            step4_data = json.load(f)
        
        para_to_page = {}
        for page_id, page_data in step4_data["pages"].items():
            for content_item in page_data["content"]:
                if content_item["type"] == "paragraph" and "source_node_id" in content_item:
                    para_id = content_item["source_node_id"]
                    para_to_page[para_id] = page_id
        
        return para_to_page
    except FileNotFoundError:
        print("Warning: step4 file not found, paragraph-to-page mapping will be empty")
        return {}

def parse_tsm_step3(input_file: str = "fate_parse_step2.json", output_file: str = "fate_parse_step3.json") -> Dict[str, Any]:
    """Create word index and node path index from step2 JSON"""
    
    # Read the step2 JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        step2_data = json.load(f)
    
    # Build word index: word -> list of node IDs containing that word
    word_index = defaultdict(set)
    total_words_processed = 0
    unique_words = set()
    
    # Process all text-containing nodes
    for section_name, section_data in step2_data["sections"].items():
        section_id = section_data["id"]
        
        # Index words from section title
        title_words = extract_words(section_data["title"])
        for word in title_words:
            word_index[word].add(section_id)
            unique_words.add(word)
        
        # Index words from paragraphs
        for paragraph in section_data["paragraphs"]:
            para_id = paragraph["id"]
            para_words = extract_words(paragraph["text"])
            
            for word in para_words:
                word_index[word].add(para_id)
                unique_words.add(word)
                total_words_processed += 1
    
    # Convert sets to sorted lists for JSON serialization
    word_index_serializable = {
        word: sorted(list(node_ids)) 
        for word, node_ids in word_index.items()
    }
    
    # Build node path index
    path_index = build_node_path_index(step2_data)
    
    # Build paragraph-to-page mapping
    paragraph_to_page = build_paragraph_to_page_mapping()
    
    # Create step3 structure
    result = {
        "metadata": {
            "title": step2_data["metadata"]["title"],
            "author": step2_data["metadata"]["author"],
            "version": step2_data["metadata"]["version"],
            "last_updated": step2_data["metadata"]["last_updated"],
            "source_file": step2_data["metadata"]["source_file"],
            "parsing_step": "step3",
            "previous_step": input_file,
            "id": "root",
            "parent_id": None
        },
        "word_index": word_index_serializable,
        "node_path_index": path_index,
        "paragraph_to_page_mapping": paragraph_to_page,
        "statistics": {
            "id": f"stats_step3",
            "parent_id": "root",
            "total_sections": step2_data["statistics"]["total_sections"],
            "total_paragraphs": step2_data["statistics"]["total_paragraphs"],
            "total_nodes": step2_data["statistics"]["total_nodes"],
            "unique_meaningful_words": len(unique_words),
            "total_word_instances": total_words_processed,
            "stop_words_excluded": len(STOP_WORDS),
            "most_common_words": sorted(
                [(word, len(nodes)) for word, nodes in word_index.items()],
                key=lambda x: x[1],
                reverse=True
            )[:20],  # Top 20 most common words
            "words_by_frequency": {
                "1_occurrence": len([w for w, nodes in word_index.items() if len(nodes) == 1]),
                "2-5_occurrences": len([w for w, nodes in word_index.items() if 2 <= len(nodes) <= 5]),
                "6-10_occurrences": len([w for w, nodes in word_index.items() if 6 <= len(nodes) <= 10]),
                "11+_occurrences": len([w for w, nodes in word_index.items() if len(nodes) > 10])
            }
        }
    }
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result

if __name__ == "__main__":
    result = parse_tsm_step3()
    stats = result["statistics"]
    
    print(f"Word Index Analysis:")
    print(f"  Unique meaningful words: {stats['unique_meaningful_words']}")
    print(f"  Total word instances: {stats['total_word_instances']}")
    print(f"  Stop words excluded: {stats['stop_words_excluded']}")
    
    print(f"\nWord frequency distribution:")
    freq_dist = stats['words_by_frequency']
    for category, count in freq_dist.items():
        print(f"  {category}: {count} words")
    
    print(f"\nTop 10 most common words:")
    for word, count in stats['most_common_words'][:10]:
        print(f"  '{word}': appears in {count} nodes")
    
    print(f"\nNode path examples:")
    path_index = result["node_path_index"]
    sample_paths = list(path_index.items())[:5]
    for node_id, path in sample_paths:
        print(f"  {node_id}: {' -> '.join(path)}")
    
    print(f"\nWord index sample:")
    word_index = result["word_index"]
    sample_words = list(word_index.items())[:3]
    for word, nodes in sample_words:
        print(f"  '{word}': found in {len(nodes)} nodes: {nodes[:5]}{'...' if len(nodes) > 5 else ''}")