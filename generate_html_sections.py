"""
Generate HTML sections for analyze_transcripts.html from transcript files in a directory.

This script scans a directory for transcript files and generates:
1. transcriptFiles object mapping
2. transcriptDisplayNames object mapping
3. sectionNumberToDisplay object mapping
4. <option> elements for the dropdown

Usage:
    python generate_html_sections.py [directory_path]
    
If no directory is specified, defaults to "output_trans_leader" folder.
"""

import os
import re
import sys
from pathlib import Path


def extract_transcript_info(filename):
    """
    Extract transcript number and display name from filename.
    
    Expected format: Transcript_XXX_<anything>.srt
    Returns: (number, display_name)
    Example: Transcript_001_sim2025a000055.srt -> ("001", "sim2025a000055")
    """
    # Pattern: Transcript_XXX_<rest>.srt
    pattern = r'Transcript_(\d{3})_(.+)\.srt'
    match = re.match(pattern, filename)
    
    if match:
        number = match.group(1)
        display_name = match.group(2)
        return number, display_name
    
    # Handle catchall or other special files
    if filename.lower() == "catchall.srt":
        return None, "Catchall"
    
    return None, None


def generate_html_sections(directory_path):
    """
    Generate HTML sections for all transcript files in the directory.
    
    Returns a dictionary with:
    - transcript_files: JavaScript object for transcriptFiles
    - display_names: JavaScript object for transcriptDisplayNames
    - section_numbers: JavaScript object for sectionNumberToDisplay
    - dropdown_options: HTML option elements
    """
    directory = Path(directory_path)
    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist.")
        sys.exit(1)
    
    # Get all .srt files
    srt_files = sorted(directory.glob("*.srt"))
    
    transcript_files_lines = []
    display_names_lines = []
    section_numbers_lines = []
    dropdown_options_lines = []
    
    for srt_file in srt_files:
        filename = srt_file.name
        number, display_name = extract_transcript_info(filename)
        
        if number and display_name:
            # Construct relative path (assuming directory is like "10-9")
            relative_path = f"{directory.name}/{filename}"
            
            # transcriptFiles mapping
            transcript_files_lines.append(f'            "{number}": "{relative_path}"')
            
            # transcriptDisplayNames mapping
            display_names_lines.append(f'            "{relative_path}": "{display_name}"')
            
            # sectionNumberToDisplay mapping
            section_numbers_lines.append(f'            "{number}": "{display_name}"')
            
            # Dropdown option
            dropdown_options_lines.append(f'                <option value="{relative_path}">{display_name}</option>')
        
        elif filename.lower() == "catchall.srt":
            # Handle catchall specially
            relative_path = filename
            display_names_lines.append(f'            "{relative_path}": "Catchall"')
            dropdown_options_lines.append(f'                <option value="{relative_path}">Catchall</option>')
    
    # Build output sections
    transcript_files_js = "const transcriptFiles = {\n" + ",\n".join(transcript_files_lines) + "\n        };"
    display_names_js = "const transcriptDisplayNames = {\n" + ",\n".join(display_names_lines) + "\n        };"
    section_numbers_js = "const sectionNumberToDisplay = {\n" + ",\n".join(section_numbers_lines) + "\n        };"
    dropdown_html = "\n".join(dropdown_options_lines)
    
    return {
        "transcript_files": transcript_files_js,
        "display_names": display_names_js,
        "section_numbers": section_numbers_js,
        "dropdown_options": dropdown_html
    }


def main():
    # Get directory from command line or use default
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = "output_trans_leader"
    
    print(f"Scanning directory: {directory_path}")
    print("=" * 80)
    
    sections = generate_html_sections(directory_path)
    
    # Output each section
    print("\n// ===== TRANSCRIPT FILES MAPPING =====")
    print(sections["transcript_files"])
    
    print("\n\n// ===== TRANSCRIPT DISPLAY NAMES MAPPING =====")
    print(sections["display_names"])
    
    print("\n\n// ===== SECTION NUMBER TO DISPLAY MAPPING =====")
    print(sections["section_numbers"])
    
    print("\n\n<!-- ===== DROPDOWN OPTIONS ===== -->")
    print(sections["dropdown_options"])
    
    print("\n" + "=" * 80)
    print("Copy the sections above and paste them into analyze_transcripts.html")
    print(f"Total files processed: {len(sections['dropdown_options'].split(chr(10)))}")


if __name__ == "__main__":
    main()
