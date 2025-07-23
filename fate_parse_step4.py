#!/usr/bin/env python3
"""
Step 4 preprocessor for tsm.txt - converts step2 paragraphs into paginated content (~250 words per page)
"""

import json
from typing import Dict, List, Any, Tuple

def create_page_content_item(item_type: str, content: Any, source_node_id: str = None) -> Dict[str, Any]:
    """Create a standardized content item for a page"""
    item = {
        "type": item_type,
        "content": content
    }
    if source_node_id:
        item["source_node_id"] = source_node_id
    return item

def parse_tsm_step4(input_file: str = "fate_parse_step2.json", output_file: str = "fate_parse_step4.json", 
                   target_words_per_page: int = 250) -> Dict[str, Any]:
    """Convert step2 paragraphs into paginated content with table of contents"""
    
    # Read the step2 JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        step2_data = json.load(f)
    
    # Initialize pagination variables
    pages = []
    current_page_content = []
    current_page_word_count = 0
    page_number = 1
    section_start_pages = {}  # section_name -> page_number
    
    # Helper function to finalize current page
    def finalize_current_page():
        nonlocal current_page_content, current_page_word_count, page_number, pages
        
        if current_page_content:
            page_id = f"page_{page_number}"
            pages.append({
                "id": page_id,
                "parent_id": "root",
                "page_number": page_number,
                "word_count": current_page_word_count,
                "content": current_page_content.copy(),
                "next_page": f"page_{page_number + 1}" if True else None  # Will be updated later
            })
            
            # Reset for next page
            current_page_content = []
            current_page_word_count = 0
            page_number += 1
    
    # Process all sections in order
    for section_name, section_data in step2_data["sections"].items():
        section_id = section_data["id"]
        section_title = section_data["title"]
        
        # Check if we need to add section title to current or new page
        section_title_words = len(section_title.split())
        
        # If adding section title would exceed limit, start new page
        if current_page_word_count > 0 and (current_page_word_count + section_title_words) > target_words_per_page:
            finalize_current_page()
        
        # Record where this section starts
        section_start_pages[section_name] = page_number
        
        # Add section title to current page
        current_page_content.append(create_page_content_item(
            "section_title", 
            {
                "title": section_title,
                "section_name": section_name
            },
            section_id
        ))
        current_page_word_count += section_title_words
        
        # Process paragraphs in this section
        for paragraph in section_data["paragraphs"]:
            para_word_count = paragraph["word_count"]
            
            # If adding this paragraph would exceed the limit, start a new page
            if current_page_word_count + para_word_count > target_words_per_page:
                finalize_current_page()
            
            # Add paragraph to current page
            current_page_content.append(create_page_content_item(
                "paragraph",
                {
                    "text": paragraph["text"],
                    "word_count": para_word_count,
                    "line_number": paragraph["line_number"],
                    "paragraph_index": paragraph["paragraph_index"]
                },
                paragraph["id"]
            ))
            current_page_word_count += para_word_count
    
    # Finalize the last page
    finalize_current_page()
    
    # Update next_page references and remove the reference from the last page
    for i, page in enumerate(pages):
        if i < len(pages) - 1:
            page["next_page"] = pages[i + 1]["id"]
        else:
            page["next_page"] = None
    
    # Create table of contents with page references
    table_of_contents = []
    for section_name in step2_data["table_of_contents"]:
        if section_name in section_start_pages:
            table_of_contents.append({
                "section_name": section_name,
                "page_number": section_start_pages[section_name],
                "page_id": f"page_{section_start_pages[section_name]}"
            })
    
    # Create the first page with TOC if it doesn't already exist
    if pages and len(pages[0]["content"]) > 0:
        # Insert TOC at the beginning of first page
        toc_content = create_page_content_item(
            "table_of_contents",
            {
                "title": "Table of Contents",
                "sections": table_of_contents
            }
        )
        pages[0]["content"].insert(0, toc_content)
        pages[0]["word_count"] += len("Table of Contents".split())
    
    # Create step4 structure
    result = {
        "metadata": {
            "title": step2_data["metadata"]["title"],
            "author": step2_data["metadata"]["author"],
            "version": step2_data["metadata"]["version"],
            "last_updated": step2_data["metadata"]["last_updated"],
            "source_file": step2_data["metadata"]["source_file"],
            "parsing_step": "step4",
            "previous_step": input_file,
            "id": "root",
            "parent_id": None,
            "target_words_per_page": target_words_per_page
        },
        "table_of_contents": table_of_contents,
        "section_start_pages": section_start_pages,
        "pages": {page["id"]: page for page in pages},
        "page_order": [page["id"] for page in pages],
        "statistics": {
            "id": "stats_step4",
            "parent_id": "root",
            "total_pages": len(pages),
            "total_sections": len(section_start_pages),
            "target_words_per_page": target_words_per_page,
            "actual_words_per_page": {
                "min": min(page["word_count"] for page in pages) if pages else 0,
                "max": max(page["word_count"] for page in pages) if pages else 0,
                "average": round(sum(page["word_count"] for page in pages) / len(pages), 1) if pages else 0
            },
            "pages_with_multiple_sections": len([
                page for page in pages 
                if len(set(item.get("content", {}).get("section_name") 
                          for item in page["content"] 
                          if item["type"] == "section_title")) > 1
            ]),
            "content_distribution": {
                "pages_with_toc": len([p for p in pages if any(item["type"] == "table_of_contents" for item in p["content"])]),
                "pages_with_section_titles": len([p for p in pages if any(item["type"] == "section_title" for item in p["content"])]),
                "pages_with_only_paragraphs": len([p for p in pages if all(item["type"] == "paragraph" for item in p["content"])])
            }
        }
    }
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result

if __name__ == "__main__":
    result = parse_tsm_step4()
    stats = result["statistics"]
    
    print(f"Pagination Analysis:")
    print(f"  Total pages: {stats['total_pages']}")
    print(f"  Target words per page: {stats['target_words_per_page']}")
    print(f"  Actual words per page:")
    print(f"    Min: {stats['actual_words_per_page']['min']}")
    print(f"    Max: {stats['actual_words_per_page']['max']}")
    print(f"    Average: {stats['actual_words_per_page']['average']}")
    
    print(f"\nContent distribution:")
    for category, count in stats['content_distribution'].items():
        print(f"  {category}: {count}")
    
    print(f"\nPages with multiple sections: {stats['pages_with_multiple_sections']}")
    
    print(f"\nTable of Contents:")
    toc = result["table_of_contents"]
    for entry in toc[:5]:  # Show first 5 entries
        print(f"  {entry['section_name']}: page {entry['page_number']}")
    if len(toc) > 5:
        print(f"  ... and {len(toc) - 5} more sections")
    
    print(f"\nSample page content:")
    first_page = result["pages"][result["page_order"][0]]
    print(f"  Page 1 ({first_page['word_count']} words):")
    for item in first_page["content"][:3]:
        if item["type"] == "table_of_contents":
            print(f"    - Table of Contents")
        elif item["type"] == "section_title":
            print(f"    - Section: {item['content']['title']}")
        elif item["type"] == "paragraph":
            preview = item["content"]["text"][:60] + "..." if len(item["content"]["text"]) > 60 else item["content"]["text"]
            print(f"    - Paragraph: {preview}")
    
    if len(first_page["content"]) > 3:
        print(f"    ... and {len(first_page['content']) - 3} more items")