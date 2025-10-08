Usage

1. Provide transcripts in .srt format to the root of the application directory
    a. Expect that SRT format contains timestamps - if you would like those to be relative to your application - run translate_time.py with the decided start time of the audio.
    b. Catchall.srt  - assumes that you have inserted the separations between transcript start and end. Luckily if you assign times inside of the transcript file - times are automatically calculated
2. Map the transcript file names to dropdown values in analyze_transcripts.html
3. Map the audio number to the transcript name for clicking on time in catchall to be brought to audio transcript - located in js for above file
4. Map the new transcripts number and name to the keys in ShowFullTranscript function.
4. Analyze transcripts!
