from pydub import AudioSegment

AudioSegment.converter = r"C:\Users\TS6166_ANUPAMA\Downloads\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"

# Test converting or loading audio
audio = AudioSegment.from_file("sample.mp3")
print("Audio duration:", len(audio), "ms")
