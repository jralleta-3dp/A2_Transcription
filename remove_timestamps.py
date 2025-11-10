import os
import re
import sys

def clean_transcript_file(file_path):
    """
    Clean a single transcript file by removing utterance numbers, timestamps, and line breaks between utterances.
    Format the output as readable paragraphs, not one continuous line.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into blocks (separated by double newlines)
        blocks = content.strip().split('\n\n')
        
        cleaned_sentences = []
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:  # Should have: number, timestamp, text (and possibly more text lines)
                # Skip the first line (utterance number) and second line (timestamp)
                # Keep everything from the third line onwards as the actual text
                text_lines = lines[2:]
                # Join all text lines and add to our cleaned sentences
                text_content = ' '.join(text_lines).strip()
                if text_content:  # Only add non-empty content
                    cleaned_sentences.append(text_content)
        
        # Join each utterance with single line breaks - each utterance on its own line
        formatted_text = '\n'.join(cleaned_sentences)
        
        # Write the cleaned text back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        print(f"✅ Cleaned: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def clean_all_txt_files(directory_path):
    """
    Process all .txt files in the specified directory.
    """
    if not os.path.exists(directory_path):
        print(f"❌ Directory not found: {directory_path}")
        return
    
    if not os.path.isdir(directory_path):
        print(f"❌ Path is not a directory: {directory_path}")
        return
    
    # Find all .txt files in the directory
    txt_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.txt')]
    
    if not txt_files:
        print(f"❌ No .txt files found in: {directory_path}")
        return
    
    print(f"📁 Found {len(txt_files)} .txt files in: {directory_path}")
    print("🔄 Processing files...")
    
    success_count = 0
    
    for filename in txt_files:
        file_path = os.path.join(directory_path, filename)
        if clean_transcript_file(file_path):
            success_count += 1
    
    print(f"\n✅ Successfully processed {success_count}/{len(txt_files)} files")

def main():
    print("🧹 Transcript Formatter")
    print("This script removes utterance numbers, timestamps, and puts each utterance on its own line.")
    print()
    
    # Get directory path from user
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = input("Enter the directory path containing .txt files: ").strip()
        # Remove quotes if user added them
        directory_path = directory_path.strip('"\'')
    
    if not directory_path:
        print("❌ No directory path provided.")
        sys.exit(1)
    
    # Convert to absolute path
    directory_path = os.path.abspath(directory_path)
    
    print(f"🎯 Target directory: {directory_path}")
    
    # Confirm with user before proceeding
    confirm = input("\n⚠️  This will OVERWRITE the original files. Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        sys.exit(0)
    
    # Process the files
    clean_all_txt_files(directory_path)

if __name__ == "__main__":
    main()
