from moviepy.editor import VideoFileClip , ImageClip , AudioFileClip , CompositeVideoClip
from moviepy.video.fx.speedx import speedx
import cv2
import numpy as np    
import srt
from datetime import timedelta
import os
import whisper_timestamped as whisper

#api key
open_ai_key = os.getenv('OPENAI_KEY')

#load model
model = whisper.load_model("base")

#function to format timestamps
def format_timestamp(time_in_seconds):
    hours = int(time_in_seconds // 3600)
    minutes = int((time_in_seconds % 3600) // 60)
    seconds = int(time_in_seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

#function to convert the audio to text:
def srt_from_audio(audio_path, subtitle_directory_path, title):
    try:
        print("Transcription started...")
        audio_model = whisper.load_audio(audio_path)
        result = whisper.transcribe(model, audio_model, language="fr")
        with open(os.path.join(subtitle_directory_path, f"{title} fr.srt"), "w") as f:
            for i, segment in enumerate(result["segments"]):
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                f.write(f"{i+1}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(segment["text"] + "\n\n")
        print(f"Transcription completed. Subtitles saved to {subtitle_directory_path}")
    
    except Exception as e:
        print(f"Error during transcription or file writing: {e}")

#modifying subtitles file with audio
def adjust_srt_timing(srt_path, speed_factor):
    with open(srt_path, 'r') as file:
        subtitles = list(srt.parse(file.read()))

    with open(srt_path, 'w') as file:
        for sub in subtitles:
            #manually scale the start and end times
            sub.start = timedelta(seconds=sub.start.total_seconds() / speed_factor)
            sub.end = timedelta(seconds=sub.end.total_seconds() / speed_factor)
            file.write(srt.compose([sub]))

def add_subtitles_and_audio(video_path , audio_path , srt_path , output_path):
    #Loading the video and audio:
    video = VideoFileClip(video_path)
    translated_audio = AudioFileClip(audio_path)
   
    #calculate the speed factor
    speed_factor = translated_audio.duration / video.duration
    print("speed factor is: ", speed_factor)

    #sync the audio and subtitles if they are not same as the video length
    if speed_factor != 1:
        translated_audio = speedx(translated_audio, factor = speed_factor)
        adjust_srt_timing(srt_path, speed_factor)
    
    #Loading subtitles:
    with open(srt_path , 'r') as f:
        subtitle_generator = srt.parse(f.read())
        subtitles = list(subtitle_generator)
        subtitle_clips = []
        
    for sub in subtitles:
        img = np.zeros((100, video.size[0], 3), dtype=np.uint8)
        cv2.putText(img, sub.content, (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        clip = ImageClip(img).set_duration(sub.end.total_seconds() - sub.start.total_seconds()).set_start(sub.start.total_seconds())
        subtitle_clips.append(clip)

    #Overlaying subtitles on the video clip:
    video = CompositeVideoClip([video] + subtitle_clips)
        
    #Replacing the original audio in the video with translated audio:
    video = video.set_audio(translated_audio)
        
    #Final output video:
    video.write_videofile(output_path)

#main function
if __name__ == "__main__":
    try:    
        original_video_name = input("Enter the name of original video file: ")
        if not original_video_name:
            raise ValueError("Video file name cannot be empty.")
        
        #split name 
        title, extension = os.path.splitext(original_video_name)
        
        #original video path
        video_directory_path = '/app/project/Milestone5/ground_truth'
        video_path = os.path.join(video_directory_path , f"{title}.mp4")
        
        #translated audio path
        audio_directory_path = '/app/project/Milestone5/translated_audio_file_french'
        audio_path = os.path.join(audio_directory_path , f"{title} fr audio.wav")
        
        #subtitle path
        subtitle_directory_path = '/app/project/Milestone5/translated_subtitle_file'
        srt_path = os.path.join(subtitle_directory_path, f"{title} fr.srt")
        
        #translated video path
        output_directory_path = '/app/project/Milestone5/translated_video'
        output_path = os.path.join(output_directory_path, f"{title} fr video.mp4")

        #converting the audio to srt
        srt_from_audio(audio_path, subtitle_directory_path, title)        
        
        #replacing audio and adding subtitle in video
        add_subtitles_and_audio(video_path , audio_path , srt_path , output_path)
        
    except Exception as e:
        print(f"An error occured: {e}")
