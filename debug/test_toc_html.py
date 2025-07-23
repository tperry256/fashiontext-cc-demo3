#!/usr/bin/env python3
import json
import html

# Load the data
with open('fate_parse_step4.json') as f:
    data = json.load(f)

print('TOC entries as they would appear in HTML:')
for entry in data['table_of_contents']:
    section_name = entry['section_name']
    page_id = entry['page_id']
    
    # This is how the HTML is generated in renderTableOfContents
    onclick_param = f"navigateToPageWithSectionScroll('{page_id}', '{section_name}')"
    escaped_section = html.escape(section_name)
    
    print(f'\nSection: {section_name}')
    print(f'  Raw onclick: {onclick_param}')
    print(f'  HTML escaped: {escaped_section}')
    print(f'  Full HTML: <a href="#" class="toc-item" onclick="{onclick_param}">{escaped_section} (page {entry["page_number"]})</a>')
    
    if "'" in section_name:
        print(f'  *** Contains apostrophe - potential issue ***')