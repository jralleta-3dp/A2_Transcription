import shutil
import os
import sys
import re

print("Welcome to the SRT Time Translator!")

print("Please provide the input SRT filename (e.g., 'Transcript_001_example.srt'):")

print("If the file is in the same directory as this script, just provide the filename.")

filename = input("Please enter the input SRT filename (case & character sensitive): ")

if os.path.exists(filename):
    print(f" 👻 File '{filename}' found. ")
else:
    print(f" ❌ File '{filename}' not found. Please check the filename and try again.")
    sys.exit(1)



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

def time_to_ms(t):
    h, m, s_ms = t.split(':')
    s, ms = s_ms.split(',')
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

def ms_to_time(ms):
    h = ms // 3600000
    h = h % 24  # This line would limit hours to 0-23 range
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def translate_time(input_file, output_file):
    print("Please provide the start time of the audio in the format HH:MM:SS,mmm (e.g., 00:01:30,500 for 1 minute, 30 seconds, and 500 milliseconds):")
    start_time = input("Start time: ")
    time_pattern = r'(\d{2}):(\d{2}):(\d{2}),(\d{3})'
    match = re.match(time_pattern, start_time)
    if not match:
        print(" ❌ Invalid time format. Please use HH:MM:SS,mmm format.")
        sys.exit(1)
    
    print(f" ⏱️ You have provided a transcript start time of {start_time}.")
    print(f" All timestamps in this transcript will be adjusted relative to this time , 01:00:00,000 will become {start_time}+01:00:00,000 and so on...")
    proceed = input("Do you want to proceed? (yes/no): ").strip().lower()
    if proceed != 'yes':
        print(" ❌ Operation cancelled by the user.")
        sys.exit(0)
    else:
        print(" ✅ Proceeding with time translation...")
        #parse the srt file in as a python object
        srt_data = parse_srt_manual(input_file)
        for sub in srt_data:
            print(f"Index: {sub['index']}, Time: {sub['start_time']} - {sub['end_time']}, Text: {sub['text']}")
            #calculate the new times
            start_ms = time_to_ms(sub['start_time'])
            end_ms = time_to_ms(sub['end_time'])

            start_offset_ms = time_to_ms(start_time)
            new_start_ms = start_ms + start_offset_ms
            new_end_ms = end_ms + start_offset_ms

            print(f"New Time: {ms_to_time(new_start_ms)} - {ms_to_time(new_end_ms)}, Text: {sub['text']}")

            #write the new times to the sub object
            sub['start_time'] = ms_to_time(new_start_ms)
            sub['end_time'] = ms_to_time(new_end_ms)

        #print the new transcript in it's entirety with it's new times
        print("Here is the translated transcript with adjusted times:")
        for sub in srt_data:
            print(f"{sub['index']}\n{sub['start_time']} --> {sub['end_time']}\n{sub['text']}\n")
        
        #write the new transcript to a new file
        if not output_file:
            output_file = input("Please provide the output SRT filename (e.g., 'Transcript_001_example_corrected.srt'): ")
            with open(output_file, 'w', encoding='utf-8') as f:
                for sub in srt_data:
                    f.write(f"{sub['index']}\n{sub['start_time']} --> {sub['end_time']}\n{sub['text']}\n\n")
        else:
            print(f" ✅ Writing translated transcript to '{output_file}'...")
            with open(output_file, 'w', encoding='utf-8') as f:
                for sub in srt_data:
                    f.write(f"{sub['index']}\n{sub['start_time']} --> {sub['end_time']}\n{sub['text']}\n\n")

#ranslate_time(filename, None)