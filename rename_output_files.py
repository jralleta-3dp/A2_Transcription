import os
import re

def rename_files_in_folder(folder_path):
    """
    Remove 'Transcript_XXX_' prefix from all files in the specified folder.
    
    Args:
        folder_path: Path to the folder containing files to rename
    """
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    if not os.path.isdir(folder_path):
        print(f"❌ Not a directory: {folder_path}")
        return
    
    # Pattern to match Transcript_XXX_ prefix (where XXX is 3 digits)
    pattern = r'^Transcript_\d{3}_'
    
    renamed_count = 0
    skipped_count = 0
    
    print(f"📁 Processing folder: {folder_path}\n")
    
    # Get all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    for filename in files:
        # Check if filename matches the pattern
        if re.match(pattern, filename):
            # Remove the prefix
            new_filename = re.sub(pattern, '', filename)
            
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            # Check if new filename already exists
            if os.path.exists(new_path):
                print(f"⚠️  Skipped (target exists): {filename}")
                skipped_count += 1
                continue
            
            try:
                os.rename(old_path, new_path)
                print(f"✅ {filename} → {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"❌ Error renaming {filename}: {e}")
                skipped_count += 1
        else:
            print(f"⚪ Skipped (no prefix): {filename}")
            skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"Total files: {len(files)}")
    print(f"Renamed: {renamed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"\n✅ Complete!")


if __name__ == "__main__":
    # Default to output_trans folder
    folder = r"c:\Users\jralleta\Desktop\Projects\A2_Transcription\output_trans"
    
    print("🔄 Filename Renamer - Remove Transcript_XXX_ Prefix")
    print("="*60)
    
    rename_files_in_folder(folder)
