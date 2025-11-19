import os
import sys
import pandas as pd
import shutil
import re
from datetime import datetime
from pathlib import Path

def parse_srt_manual(filepath):
    """Parse an SRT file into a list of subtitle dictionaries."""
    subtitles = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into blocks based on double newline
    blocks = content.strip().split('\n\n')

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:  # Ensure it has index, time, and at least one text line
            index = int(lines[0])
            time_str = lines[1]
            text = "\n".join(lines[2:])

            # Extract start and end times
            time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_str)
            if time_match:
                start_time = time_match.group(1)
                end_time = time_match.group(2)
                subtitles.append({
                    'index': index,
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': text
                })
    return subtitles


def time_to_ms(t):
    """Convert SRT timestamp to milliseconds."""
    h, m, s_ms = t.split(':')
    s, ms = s_ms.split(',')
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)


def ms_to_time(ms):
    """Convert milliseconds to SRT timestamp format."""
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def translate_srt_times(srt_path, start_time_str):
    """
    Translate all timestamps in an SRT file by adding a start time offset.
    
    Args:
        srt_path: Path to the SRT file
        start_time_str: Start time in format HH:MM:SS,mmm
        
    Returns:
        List of translated subtitle dictionaries
    """
    srt_data = parse_srt_manual(srt_path)
    start_offset_ms = time_to_ms(start_time_str)
    
    for sub in srt_data:
        start_ms = time_to_ms(sub['start_time'])
        end_ms = time_to_ms(sub['end_time'])
        
        new_start_ms = start_ms + start_offset_ms
        new_end_ms = end_ms + start_offset_ms
        
        sub['start_time'] = ms_to_time(new_start_ms)
        sub['end_time'] = ms_to_time(new_end_ms)
    
    return srt_data


def write_srt_file(srt_data, output_path):
    """Write subtitle data to an SRT file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for sub in srt_data:
            f.write(f"{sub['index']}\n")
            f.write(f"{sub['start_time']} --> {sub['end_time']}\n")
            f.write(f"{sub['text']}\n\n")


def parse_acquisition_time(time_str):
    """
    Parse acquisition time string to SRT time format (HH:MM:SS,mmm).
    Handles format: YYYY:MM:DD HH:MM:SS
    
    Args:
        time_str: Acquisition time string
        
    Returns:
        Time in SRT format (HH:MM:SS,000) or None if parsing fails
    """
    time_str = str(time_str).strip()
    
    # Pattern for YYYY:MM:DD HH:MM:SS format
    # We only need the time part (HH:MM:SS)
    pattern = r'\d{4}:\d{2}:\d{2}\s+(\d{2}):(\d{2}):(\d{2})'
    match = re.search(pattern, time_str)
    
    if match:
        h, m, s = match.group(1), match.group(2), match.group(3)
        return f"{h}:{m}:{s},000"
    
    # Fallback: try to extract just time portion (HH:MM:SS)
    time_only_pattern = r'(\d{2}):(\d{2}):(\d{2})'
    match = re.search(time_only_pattern, time_str)
    
    if match:
        h, m, s = match.group(1), match.group(2), match.group(3)
        return f"{h}:{m}:{s},000"
    
    return None


def find_transcript_files(audio_filename, transcript_folder):
    """
    Find corresponding .srt and .txt files for an audio file.
    
    Args:
        audio_filename: Name of the audio file (with extension)
        transcript_folder: Folder to search for transcript files
        
    Returns:
        Tuple of (srt_path, txt_path) or (None, None) if not found
    """
    # Remove extension from audio filename
    base_name = os.path.splitext(audio_filename)[0]
    
    # Look for .srt and .txt files with same base name
    srt_path = os.path.join(transcript_folder, f"{base_name}.srt")
    txt_path = os.path.join(transcript_folder, f"{base_name}.txt")
    
    srt_exists = os.path.exists(srt_path)
    txt_exists = os.path.exists(txt_path)
    
    return (srt_path if srt_exists else None, txt_path if txt_exists else None)


def extract_original_name(filename):
    """Extract the original name from audio filename (without extension)."""
    return os.path.splitext(filename)[0]


def process_inventory(excel_path, transcript_folder, output_folder):
    """
    Process the inventory Excel file and generate translated transcripts.
    
    Args:
        excel_path: Path to Excel file with inventory
        transcript_folder: Folder containing original transcript files
        output_folder: Folder to save processed transcripts
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Create deprecated folder
    deprecated_folder = os.path.join(transcript_folder, "deprecated")
    os.makedirs(deprecated_folder, exist_ok=True)
    
    # Read Excel file
    print(f"📊 Reading Excel file: {excel_path}")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return
    
    # Verify columns exist
    if len(df.columns) < 2:
        print("❌ Excel file must have at least 2 columns (Filename, Acquisition Time)")
        return
    
    # Use first two columns regardless of their names
    filename_col = df.columns[0]
    time_col = df.columns[1]
    
    print(f"✅ Using columns: '{filename_col}' and '{time_col}'")
    
    # Filter for audio files
    df['is_audio'] = df[filename_col].astype(str).str.lower().str.endswith(('.m4a', '.M4A'))
    audio_files = df[df['is_audio']].copy()
    
    if len(audio_files) == 0:
        print("❌ No .m4a or .M4A files found in the spreadsheet")
        return
    
    print(f"\n📁 Found {len(audio_files)} audio files")
    
    # Parse acquisition times and sort by datetime
    audio_files['parsed_time'] = audio_files[time_col].apply(parse_acquisition_time)
    audio_files = audio_files.dropna(subset=['parsed_time'])
    
    # Sort by time (convert to comparable format)
    def time_to_sortable(time_str):
        """Convert HH:MM:SS,mmm to sortable number."""
        try:
            return time_to_ms(time_str)
        except:
            return 0
    
    audio_files['sort_key'] = audio_files['parsed_time'].apply(time_to_sortable)
    audio_files = audio_files.sort_values('sort_key')
    
    print(f"✅ Sorted {len(audio_files)} files by acquisition time")
    
    # Process each file
    processed_count = 0
    skipped_count = 0
    processed_base_names = set()  # Track which transcript files were processed
    
    for idx, (_, row) in enumerate(audio_files.iterrows(), 1):
        filename = row[filename_col]
        acquisition_time = row['parsed_time']
        
        print(f"\n[{idx}/{len(audio_files)}] Processing: {filename}")
        print(f"   Acquisition time: {acquisition_time}")
        
        # Find transcript files
        srt_path, txt_path = find_transcript_files(filename, transcript_folder)
        
        if not srt_path:
            print(f"   ⚠️  No .srt file found for {filename}")
            skipped_count += 1
            continue
        
        # Track the base name of processed files
        base_name = os.path.splitext(filename)[0]
        processed_base_names.add(base_name)
        
        print(f"   ✅ Found: {os.path.basename(srt_path)}")
        if txt_path:
            print(f"   ✅ Found: {os.path.basename(txt_path)}")
        
        # Translate SRT times
        try:
            translated_srt = translate_srt_times(srt_path, acquisition_time)
        except Exception as e:
            print(f"   ❌ Error translating times: {e}")
            skipped_count += 1
            continue
        
        # Generate output filename
        original_name = extract_original_name(filename)
        output_filename = f"Transcript_{idx:03d}_{original_name}.srt"
        output_path = os.path.join(output_folder, output_filename)
        
        # Write translated SRT file
        try:
            write_srt_file(translated_srt, output_path)
            print(f"   💾 Saved: {output_filename}")
            processed_count += 1
        except Exception as e:
            print(f"   ❌ Error saving file: {e}")
            skipped_count += 1
            continue
        
        # Copy corresponding TXT file if it exists
        if txt_path:
            txt_output_filename = f"Transcript_{idx:03d}_{original_name}.txt"
            txt_output_path = os.path.join(output_folder, txt_output_filename)
            try:
                shutil.copy2(txt_path, txt_output_path)
                print(f"   💾 Copied: {txt_output_filename}")
            except Exception as e:
                print(f"   ⚠️  Could not copy TXT file: {e}")
    
    # Move unprocessed transcript files to deprecated folder
    print("\n" + "=" * 60)
    print("🗂️  Checking for unprocessed transcript files...")
    print("=" * 60)
    
    moved_count = 0
    all_transcript_files = []
    
    # Find all .srt and .txt files in transcript folder
    for file in os.listdir(transcript_folder):
        if file.lower().endswith(('.srt', '.txt')):
            file_path = os.path.join(transcript_folder, file)
            if os.path.isfile(file_path):
                all_transcript_files.append(file)
    
    # Check which files were not processed
    for file in all_transcript_files:
        base_name = os.path.splitext(file)[0]
        
        # Skip if this file was processed
        if base_name in processed_base_names:
            continue
        
        # Move to deprecated folder
        source_path = os.path.join(transcript_folder, file)
        dest_path = os.path.join(deprecated_folder, file)
        
        try:
            shutil.move(source_path, dest_path)
            print(f"📦 Moved to deprecated: {file}")
            moved_count += 1
        except Exception as e:
            print(f"⚠️  Could not move {file}: {e}")
    
    if moved_count == 0:
        print("✅ No unprocessed files found (all transcripts matched inventory)")
    else:
        print(f"\n📦 Moved {moved_count} unprocessed file(s) to: {deprecated_folder}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total audio files in inventory: {len(audio_files)}")
    print(f"Successfully processed: {processed_count}")
    print(f"Skipped (no transcript found): {skipped_count}")
    print(f"Moved to deprecated: {moved_count}")
    print(f"\n✅ Processed transcripts saved to: {output_folder}")
    if moved_count > 0:
        print(f"📦 Deprecated files moved to: {deprecated_folder}")


def main():
    print("🎬 Transcript Inventory Processor")
    print("=" * 60)
    
    # Get Excel file path
    excel_path = input("\nEnter path to Excel inventory file: ").strip().strip('"\'')
    
    if not os.path.exists(excel_path):
        print(f"❌ File not found: {excel_path}")
        sys.exit(1)
    
    # Get transcript folder
    transcript_folder = input("\nEnter folder containing transcript files (.srt and .txt): ").strip().strip('"\'')
    
    if not os.path.isdir(transcript_folder):
        print(f"❌ Folder not found: {transcript_folder}")
        sys.exit(1)
    
    # Get output folder
    output_folder = input("\nEnter output folder for processed transcripts: ").strip().strip('"\'')
    
    if not output_folder:
        output_folder = os.path.join(os.getcwd(), "processed_transcripts")
        print(f"Using default output folder: {output_folder}")
    
    # Process inventory
    print("\n" + "=" * 60)
    process_inventory(excel_path, transcript_folder, output_folder)


if __name__ == "__main__":
    main()
