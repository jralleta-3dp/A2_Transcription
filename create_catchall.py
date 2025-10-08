import re
import os


print("Welcome to the Catchall SRT Creator!")
print("This script will help you create a consolidated SRT file from multiple transcripts.")
print("Please ensure your transcript files are in the same directory as this script.")

print("WARNING - YOUR TRANSCRIPTS MUST HAVE AN ID # IN THE FILENAME - e.g. Transcript_001_example.srt")

transcripts_folder = input("Enter the folder path containing your transcript files (or press Enter for current directory): ")
if transcripts_folder.strip() == "":
    transcripts_folder = "."
if not os.path.isdir(transcripts_folder):
    print(f" ❌ Folder '{transcripts_folder}' not found. Please check the path and try again.")
    exit(1)

output_filename = "catchall.srt"

def parse_srt_manual(filepath):
    subtitles = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into blocks based on double newline
    blocks = content.strip().split('\n\n')

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3: # Ensure it has index, time, and at least one text line
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


#create the catchall file, an example catchall exists as an example for the format used, it's filname is catchall_example.srt
def create_catchall(transcripts_folder, output_filename):
    transcript_files = [f for f in os.listdir(transcripts_folder) if f.lower().endswith('.srt')]
    all_subtitles = []
    current_index = 1

    #create the new file environment
    with open(output_filename, 'w', encoding='utf-8') as f:
        for transcript_file in sorted(transcript_files):
            transcript_path = os.path.join(transcripts_folder, transcript_file)
            id_tag = re.search(r'Transcript_(\d{3})', transcript_file)
            id_number = id_tag.group(1) if id_tag else "000"
            print(f"Processing '{transcript_file}' with ID '{id_number}'...")

            subtitles = parse_srt_manual(transcript_path)
            # we are not changing anything inside of the transcript, itself, we are only adding the ### Transcript {id_number} to the start of the transcript block, then pasting the transcript as is
            f.write(f"### Transcript {id_number}\n\n")

            #write each line
            for subtitle in subtitles:
                f.write(f"{subtitle['index']}\n{subtitle['start_time']} --> {subtitle['end_time']}\n{subtitle['text']}\n\n")
            
        #once all id's and lines are written to the file - we are done
    print(f" ✅ Catchall SRT file '{output_filename}' created successfully!")
    return

create_catchall(transcripts_folder, output_filename)
