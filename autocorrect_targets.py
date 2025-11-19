import os
import sys
import re
import csv
from typing import List, Dict, Set

# Common misspellings and variations for lunar target names
# This can be expanded based on actual transcription errors encountered
TARGET_CORRECTIONS = {
    # Oceanus Procellarum
    "oceanus procellarum": ["ocean is procellarum", "oceanus procelerum", "ocean us procellarum", 
                             "oceanus procel arum", "oceanus procedure", "oceanis procellarum"],
    
    # Orientale Basin
    "orientale basin": ["oriental basin", "orientali basin", "orient ale basin", 
                        "orientale bay sin", "oriental a basin"],
    
    # Jackson Crater
    "jackson crater": ["jackson creator", "jackson crator", "jackson crater", 
                       "jackson creator", "jackson creator"],
    
    # Crookes Crater
    "crookes crater": ["crooks crater", "crook's crater", "crooks creator", 
                       "brooks crater", "crookes creator"],
    
    # Bose and Bhabha
    "bose": ["bohz", "boze", "bose", "bos"],
    "bhabha": ["baba", "babba", "bhaba", "bob ha", "ba ba"],
    
    # Sundman J Crater
    "sundman": ["sundmann", "sundman", "sundmin", "sun man", "sundman j"],
    
    # Mare Ingenii
    "mare ingenii": ["maria genie", "mary ingenii", "mare in genie", "mar a ingenii", 
                     "mare in jenny", "mare ingenui"],
    
    # Leibnitz Crater
    "leibnitz": ["lieb nitz", "leibnitz", "leibnitz", "lieb nets", "lie nits"],
    
    # Stefan L Crater
    "stefan": ["stephen", "steven", "stefan", "steffan"],
    
    # Grigg E Crater
    "grigg": ["grig", "greg", "grige", "griggs"],
    
    # Vavilov Crater
    "vavilov": ["vavilov", "vavilov", "vavilov", "vavilov"],
    
    # Earthset/Earthrise
    "earthset": ["earth set", "earth-set"],
    "earthrise": ["earth rise", "earth-rise"],
    
    # Korolev Basin
    "korolev": ["korolev", "korolev", "ころlev", "korol ev"],
    
    # Oppenheimer Basin
    "oppenheimer": ["oppenheimer", "oppen heimer", "oppenheimer", "openhimer"],
    
    # Apollo Basin
    "apollo basin": ["apollo bay sin", "apollo basin", "apollo basins"],
    
    # South Pole Region
    "south pole": ["south pole", "southpole"],
    
    # Dewar Crater
    "dewar": ["dewer", "dewar", "due war"],
    
    # Tsiolkovskiy Crater
    "tsiolkovskiy": ["tsiolkovsky", "tsiolkovskiy", "tsiolkovskiy", "tsialkovsky", 
                     "si ol kovsky", "see ol kovsky"],
    
    # Moscoviense Basin
    "moscoviense": ["moscovian", "moscoviense", "mosco vian", "mosco vienzi", 
                    "mosco viense"],
    
    # Ryder Crater
    "ryder": ["rider", "ryder", "writer"],
    
    # Aitken Crater
    "aitken": ["aitken", "aitkin", "atkin", "aitkens"],
    
    # Buys-Ballot Crater
    "buys-ballot": ["buys ballot", "buys-ballot", "buys ballot", "buys balot", 
                    "boys ballot"],
    
    # Poincaré Crater
    "poincaré": ["poincare", "poincaré", "poincare", "point care"],
    
    # Jules Verne Crater
    "jules verne": ["jules vern", "jules burn", "jewels verne", "jules verne"],
    
    # Schrodinger Basin
    "schrödinger": ["schrodinger", "schröedinger", "shrodinger", "schrodinger"],
    
    # Ohm Crater
    "ohm": ["om", "ohm", "ome"],
    
    # Whole Moon
    "whole moon": ["whole moon", "full moon"],
}


def generate_phonetic_variations(word: str) -> Set[str]:
    """
    Generate potential phonetic misspellings for a word based on common transcription errors.
    
    Args:
        word: The correct word/name
        
    Returns:
        Set of potential misspellings
    """
    variations = set()
    word_lower = word.lower()
    
    # Common phonetic substitutions for speech-to-text errors
    phonetic_rules = [
        # Vowel confusions
        ('a', ['e', 'uh']),
        ('e', ['a', 'i']),
        ('i', ['e', 'y']),
        ('o', ['uh', 'oh']),
        ('u', ['oo', 'uh']),
        
        # Consonant confusions
        ('c', ['k', 's']),
        ('k', ['c', 'ck']),
        ('s', ['c', 'z']),
        ('z', ['s']),
        ('f', ['ph', 'v']),
        ('v', ['f', 'b']),
        ('b', ['p', 'v']),
        ('p', ['b']),
        ('t', ['d']),
        ('d', ['t']),
        ('g', ['j']),
        ('j', ['g']),
        
        # Special patterns
        ('ch', ['tch', 'sh']),
        ('sh', ['ch']),
        ('th', ['t', 'f']),
        ('ph', ['f']),
        ('tion', ['shun']),
        ('sion', ['shun']),
    ]
    
    # Apply phonetic substitutions
    for original, replacements in phonetic_rules:
        if original in word_lower:
            for replacement in replacements:
                variations.add(word_lower.replace(original, replacement))
    
    # Space variations (for compound names)
    if ' ' in word_lower:
        variations.add(word_lower.replace(' ', ''))
        variations.add(word_lower.replace(' ', '-'))
    elif '-' in word_lower:
        variations.add(word_lower.replace('-', ' '))
        variations.add(word_lower.replace('-', ''))
    
    # Add version with spaces between syllables (e.g., "jackson" -> "jack son")
    if len(word_lower) > 5 and ' ' not in word_lower:
        # Try splitting at common syllable breaks
        for i in range(3, len(word_lower) - 2):
            variations.add(word_lower[:i] + ' ' + word_lower[i:])
    
    # Double consonant variations
    for char in 'bcdfghjklmnpqrstvwxyz':
        if char * 2 in word_lower:
            variations.add(word_lower.replace(char * 2, char))
        elif char in word_lower:
            variations.add(word_lower.replace(char, char * 2))
    
    # Remove the original word from variations
    variations.discard(word_lower)
    
    return variations


def generate_misspellings_for_target(target_name: str) -> Set[str]:
    """
    Generate potential misspellings for an entire target name.
    
    Args:
        target_name: The correct target name
        
    Returns:
        Set of potential misspellings
    """
    all_variations = set()
    target_lower = target_name.lower()
    
    # Generate variations for the whole name
    all_variations.update(generate_phonetic_variations(target_name))
    
    # If it's a multi-word name, generate variations for each word
    words = target_name.split()
    if len(words) > 1:
        # Generate variations for each word separately
        word_variations = []
        for word in words:
            variations = generate_phonetic_variations(word)
            variations.add(word.lower())
            word_variations.append(list(variations))
        
        # Combine variations (up to 3 combinations per word to avoid explosion)
        import itertools
        for combo in itertools.product(*[v[:3] if len(v) > 3 else v for v in word_variations]):
            all_variations.add(' '.join(combo))
    
    # Remove the original
    all_variations.discard(target_lower)
    
    return all_variations


def build_correction_map(target_names: List[str], auto_generate: bool = True) -> Dict[str, str]:
    """
    Build a comprehensive correction map from the target names list.
    
    Args:
        target_names: List of correct target names
        auto_generate: Whether to automatically generate phonetic variations
        
    Returns:
        Dictionary mapping misspellings to correct spellings
    """
    correction_map = {}
    
    for target in target_names:
        target_lower = target.lower()
        
        # Add exact match (case insensitive)
        correction_map[target_lower] = target
        
        # Check if this target has known misspellings in our predefined database
        for correct_form, misspellings in TARGET_CORRECTIONS.items():
            if correct_form in target_lower:
                for misspelling in misspellings:
                    correction_map[misspelling.lower()] = target
        
        # Auto-generate phonetic variations if enabled
        if auto_generate:
            generated_variations = generate_misspellings_for_target(target)
            for variation in generated_variations:
                # Only add if not already in map (predefined takes priority)
                if variation not in correction_map:
                    correction_map[variation] = target
    
    return correction_map


def autocorrect_text(text: str, correction_map: Dict[str, str]) -> tuple:
    """
    Apply autocorrections to text content.
    
    Args:
        text: The text to correct
        correction_map: Dictionary of misspelling -> correct spelling
        
    Returns:
        Tuple of (corrected_text, number_of_corrections)
    """
    corrected_text = text
    corrections_made = 0
    
    # Sort by length (longest first) to handle overlapping patterns
    sorted_corrections = sorted(correction_map.items(), key=lambda x: len(x[0]), reverse=True)
    
    for misspelling, correct_spelling in sorted_corrections:
        # Create a case-insensitive regex pattern that matches whole words
        pattern = r'\b' + re.escape(misspelling) + r'\b'
        
        # Count matches before replacement
        matches = len(re.findall(pattern, corrected_text, re.IGNORECASE))
        
        if matches > 0:
            # Replace while preserving the case of the first letter
            def replace_preserve_case(match):
                original = match.group(0)
                if original[0].isupper():
                    return correct_spelling.title()
                return correct_spelling
            
            corrected_text = re.sub(pattern, replace_preserve_case, corrected_text, flags=re.IGNORECASE)
            corrections_made += matches
    
    return corrected_text, corrections_made


def process_srt_file(filepath: str, correction_map: Dict[str, str]) -> int:
    """
    Process an SRT file and apply corrections.
    
    Args:
        filepath: Path to the SRT file
        correction_map: Dictionary of corrections
        
    Returns:
        Number of corrections made
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        corrected_content, corrections = autocorrect_text(content, correction_map)
        
        if corrections > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            print(f"  ✅ {os.path.basename(filepath)}: {corrections} correction(s)")
        else:
            print(f"  ⚪ {os.path.basename(filepath)}: No corrections needed")
        
        return corrections
        
    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return 0


def process_txt_file(filepath: str, correction_map: Dict[str, str]) -> int:
    """
    Process a TXT file and apply corrections.
    
    Args:
        filepath: Path to the TXT file
        correction_map: Dictionary of corrections
        
    Returns:
        Number of corrections made
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        corrected_content, corrections = autocorrect_text(content, correction_map)
        
        if corrections > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            print(f"  ✅ {os.path.basename(filepath)}: {corrections} correction(s)")
        else:
            print(f"  ⚪ {os.path.basename(filepath)}: No corrections needed")
        
        return corrections
        
    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return 0


def process_files(base_filename: str, correction_map: Dict[str, str]) -> tuple:
    """
    Process both SRT and TXT files with the same base filename.
    
    Args:
        base_filename: Base filename without extension
        correction_map: Dictionary of corrections
        
    Returns:
        Tuple of (srt_corrections, txt_corrections)
    """
    srt_file = f"{base_filename}.srt"
    txt_file = f"{base_filename}.txt"
    
    srt_corrections = 0
    txt_corrections = 0
    
    print(f"\n📄 Processing: {os.path.basename(base_filename)}")
    
    if os.path.exists(srt_file):
        srt_corrections = process_srt_file(srt_file, correction_map)
    else:
        print(f"  ⚠️  {os.path.basename(srt_file)} not found")
    
    if os.path.exists(txt_file):
        txt_corrections = process_txt_file(txt_file, correction_map)
    else:
        print(f"  ⚠️  {os.path.basename(txt_file)} not found")
    
    return srt_corrections, txt_corrections


def load_target_names_from_file(filepath: str) -> List[str]:
    """
    Load target names from a text file (one per line) or CSV file.
    
    Args:
        filepath: Path to the file containing target names (.txt or .csv)
        
    Returns:
        List of target names
    """
    try:
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext == '.csv':
            return load_target_names_from_csv(filepath)
        else:
            # Treat as plain text file
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Error reading target names file: {e}")
        return []


def load_target_names_from_csv(filepath: str) -> List[str]:
    """
    Load target names from a CSV file.
    Supports various formats:
    - Single column with target names
    - Column labeled 'target_name', 'name', 'target', etc.
    - Multiple columns (will try to detect the right one)
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        List of target names
    """
    try:
        target_names = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            # Try to detect if file has headers
            sample = f.read(1024)
            f.seek(0)
            
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(sample)
            
            reader = csv.reader(f)
            
            if has_header:
                headers = next(reader)
                # Try to find the target name column
                target_col_idx = None
                
                for idx, header in enumerate(headers):
                    header_lower = header.lower()
                    if any(keyword in header_lower for keyword in ['target_name', 'target', 'name', 'ltp_name']):
                        target_col_idx = idx
                        break
                
                if target_col_idx is None:
                    # Default to first column
                    target_col_idx = 0
                    print(f"⚠️  No target name column found, using first column: '{headers[0]}'")
                else:
                    print(f"✅ Using column: '{headers[target_col_idx]}'")
                
                for row in reader:
                    if row and len(row) > target_col_idx:
                        name = row[target_col_idx].strip()
                        if name and name.lower() != 'null' and name.lower() != 'nan':
                            target_names.append(name)
            else:
                # No header, use first column
                for row in reader:
                    if row:
                        name = row[0].strip()
                        if name and name.lower() != 'null' and name.lower() != 'nan':
                            target_names.append(name)
        
        return target_names
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return []


def main():
    print("🎯 Lunar Target Name Autocorrect Tool")
    print("=" * 60)
    
    # Get target names
    print("\nProvide target names in one of three ways:")
    print("1. Path to a text file containing target names (one per line)")
    print("2. Path to a CSV file with target names column")
    print("3. Enter target names manually (comma-separated)")
    
    target_input = input("\nEnter file path or target names: ").strip()
    
    target_names = []
    
    # Check if it's a file path
    if os.path.exists(target_input):
        target_names = load_target_names_from_file(target_input)
        print(f"\n✅ Loaded {len(target_names)} target names from file")
    else:
        # Parse as comma-separated list
        target_names = [name.strip() for name in target_input.split(',') if name.strip()]
        print(f"\n✅ Parsed {len(target_names)} target names")
    
    if not target_names:
        print("❌ No target names provided. Exiting.")
        sys.exit(1)
    
    print("\nTarget names to use for autocorrection:")
    for i, name in enumerate(target_names, 1):
        print(f"  {i}. {name}")
    
    # Ask about auto-generation
    auto_gen = input("\nAuto-generate phonetic misspellings? (yes/no) [yes]: ").strip().lower()
    auto_generate = auto_gen != 'no'
    
    # Build correction map
    correction_map = build_correction_map(target_names, auto_generate=auto_generate)
    print(f"\n🔧 Built correction map with {len(correction_map)} patterns")
    
    if auto_generate:
        print("   (Includes predefined + auto-generated phonetic variations)")
    else:
        print("   (Using predefined patterns only)")
    
    # Get file(s) to process
    print("\n" + "=" * 60)
    print("Provide files to process:")
    print("1. Single file (without extension, e.g., 'transcript_001')")
    print("2. Directory path (to process all files in directory)")
    
    file_input = input("\nEnter file/directory path: ").strip().strip('"\'')
    
    if not file_input:
        print("❌ No file or directory provided. Exiting.")
        sys.exit(1)
    
    total_srt_corrections = 0
    total_txt_corrections = 0
    files_processed = 0
    
    # Check if it's a directory
    if os.path.isdir(file_input):
        print(f"\n📁 Processing directory: {file_input}")
        
        # Find all unique base filenames (without extensions)
        base_files = set()
        for filename in os.listdir(file_input):
            if filename.endswith(('.srt', '.txt')):
                base_name = os.path.splitext(filename)[0]
                base_files.add(os.path.join(file_input, base_name))
        
        for base_file in sorted(base_files):
            srt_corr, txt_corr = process_files(base_file, correction_map)
            total_srt_corrections += srt_corr
            total_txt_corrections += txt_corr
            if srt_corr > 0 or txt_corr > 0:
                files_processed += 1
    else:
        # Single file (base filename without extension)
        # Remove extension if provided
        base_file = os.path.splitext(file_input)[0]
        
        srt_corr, txt_corr = process_files(base_file, correction_map)
        total_srt_corrections += srt_corr
        total_txt_corrections += txt_corr
        if srt_corr > 0 or txt_corr > 0:
            files_processed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Files with corrections: {files_processed}")
    print(f"Total SRT corrections: {total_srt_corrections}")
    print(f"Total TXT corrections: {total_txt_corrections}")
    print(f"Total corrections: {total_srt_corrections + total_txt_corrections}")
    print("\n✅ Processing complete!")


if __name__ == "__main__":
    main()
