#!/usr/bin/env python3
import json

with open('fate_parse_step4.json', 'r') as f:
    data = json.load(f)

# Check the section titles on the pages where CH3, CH5, and CH6 appear
problematic_sections = ["CH3: This Guy's Guys", "CH5: Trey's Memoir", "CH6: Todd's About"]

for section_name in problematic_sections:
    page_id = f'page_{data["section_start_pages"][section_name]}'
    page = data['pages'][page_id]
    print(f'\n{section_name} -> {page_id}:')
    for item in page['content']:
        if item['type'] == 'section_title':
            actual_title = item['content']['title']
            section_key = item['content']['section_name']
            print(f'  Section key: "{section_key}"')
            print(f'  Actual title: "{actual_title}"')
            print(f'  Match TOC: {section_key == section_name}')
            
            # Check character codes for apostrophes
            for i, char in enumerate(section_key):
                if char in ["'", "'"]:
                    print(f'    Apostrophe at position {i}: ord({repr(char)}) = {ord(char)}')
            for i, char in enumerate(section_name):
                if char in ["'", "'"]:
                    print(f'    TOC apostrophe at position {i}: ord({repr(char)}) = {ord(char)}')